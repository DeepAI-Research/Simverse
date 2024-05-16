import os
import sys
import argparse
import requests
import json
from typing import Dict, List, Tuple
import time
import hashlib
import re
import urllib.parse

server_url_default = "https://console.vast.ai"
headers = {}

def http_get(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if response is not None:
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        raise


def apiurl(subpath: str, query_args: Dict = None, api_key: str = None) -> str:
    if query_args is None:
        query_args = {}
    if api_key is not None:
        query_args["api_key"] = api_key
    query_json = "&".join(
        "{x}={y}".format(x=x, y=requests.utils.quote(json.dumps(y)))
        for x, y in query_args.items()
    )
    return server_url_default + "/api/v0" + subpath + "?" + query_json

def http_put(req_url, headers, json):
    response = requests.put(req_url, headers=headers, json=json)
    response.raise_for_status()
    return response

def http_del(req_url, headers, json={}):
    response = requests.delete(req_url, headers=headers, json=json)
    response.raise_for_status()
    return response

def http_post(req_url, headers, json={}):
    response = requests.post(req_url, headers=headers, json=json)
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error response content: {response.content}")
        raise e
    return response

def parse_query(
    query_str: str, res: Dict = None, fields={}, field_alias={}, field_multiplier={}
) -> Dict:
    if res is None:
        res = {}
    if type(query_str) == list:
        query_str = " ".join(query_str)
    query_str = query_str.strip()
    pattern = r"([a-zA-Z0-9_]+)( *[=><!]+| +(?:[lg]te?|nin|neq|eq|not ?eq|not ?in|in) )?( *)(\[[^\]]+\]|\"[^\"]+\"|[^ ]+)?( *)"
    opts = re.findall(pattern, query_str)
    op_names = {
        ">=": "gte", ">": "gt", "gt": "gt", "gte": "gte", "<=": "lte", "<": "lt",
        "lt": "lt", "lte": "lte", "!=": "neq", "==": "eq", "=": "eq", "eq": "eq",
        "neq": "neq", "noteq": "neq", "not eq": "neq", "notin": "notin",
        "not in": "notin", "nin": "notin", "in": "in",
    }
    joined = "".join("".join(x) for x in opts)
    if joined != query_str:
        raise ValueError(
            "Unconsumed text. Did you forget to quote your query? "
            + repr(joined)
            + " != "
            + repr(query_str)
        )
    for field, op, _, value, _ in opts:
        value = value.strip(",[]")
        v = res.setdefault(field, {})
        op = op.strip()
        op_name = op_names.get(op)
        if field in field_alias:
            res.pop(field)
            field = field_alias[field]
        if not field in fields:
            print(
                "Warning: Unrecognized field: {}, see list of recognized fields.".format(
                    field
                ),
                file=sys.stderr,
            )
        if not op_name:
            raise ValueError(
                "Unknown operator. Did you forget to quote your query? "
                + repr(op).strip("u")
            )
        if op_name in ["in", "notin"]:
            value = [x.strip() for x in value.split(",") if x.strip()]
        if not value:
            raise ValueError(
                "Value cannot be blank. Did you forget to quote your query? "
                + repr((field, op, value))
            )
        if not field:
            raise ValueError(
                "Field cannot be blank. Did you forget to quote your query? "
                + repr((field, op, value))
            )
        if value in ["?", "*", "any"]:
            if op_name != "eq":
                raise ValueError("Wildcard only makes sense with equals.")
            if field in v:
                del v[field]
            if field in res:
                del res[field]
            continue
        if isinstance(value, str):
            value = value.replace("_", " ")
            value = value.strip('"')
        elif isinstance(value, list):
            value = [x.replace("_", " ") for x in value]
            value = [x.strip('"') for x in value]
        if field in field_multiplier:
            value = float(value) * field_multiplier[field]
            v[op_name] = value
        else:
            if (value == "true") or (value == "True"):
                v[op_name] = True
            elif (value == "false") or (value == "False"):
                v[op_name] = False
            elif (value == "None") or (value == "null"):
                v[op_name] = None
            else:
                v[op_name] = value
        if field not in res:
            res[field] = v
        else:
            res[field].update(v)
    return res

offers_fields = {
    "bw_nvlink", "compute_cap", "cpu_cores", "cpu_ram", "cuda_max_good",
    "direct_port_count", "disk_bw", "disk_space", "dlperf", "dph_total",
    "driver_version", "duration", "external", "flops_per_dphtotal", "gpu_mem_bw",
    "gpu_name", "gpu_ram", "has_avx", "id", "inet_down", "inet_down_cost",
    "inet_up", "inet_up_cost", "machine_id", "min_bid", "mobo_name", "num_gpus",
    "pci_gen", "pcie_bw", "reliability", "rentable", "rented", "storage_cost",
    "total_flops", "verified"
}

offers_alias = {
    "cuda_vers": "cuda_max_good", "reliability": "reliability2",
    "dlperf_usd": "dlperf_per_dphtotal", "dph": "dph_total",
    "flops_usd": "flops_per_dphtotal",
}

offers_mult = {
    "cpu_ram": 1000, "duration": 24 * 60 * 60
}

def get_runtype(args):
    runtype = "ssh"
    if args.jupyter_dir or args.jupyter_lab:
        args.jupyter = True
    if args.jupyter and runtype == "args":
        print(
            "Error: Can't use --jupyter and --args together. Try --onstart or --onstart-cmd instead of --args.",
            file=sys.stderr,
        )
        return 1
    if args.jupyter:
        runtype = (
            "jupyter_direc ssh_direc ssh_proxy"
            if args.direct
            else "jupyter_proxy ssh_proxy"
        )
    if args.ssh:
        runtype = "ssh_direc ssh_proxy" if args.direct else "ssh_proxy"
    return runtype

def parse_env(envs):
    result = {}
    if envs is None:
        return result
    env = envs.split(" ")
    prev = None
    for e in env:
        if prev is None:
            if e in {"-e", "-p", "-h"}:
                prev = e
            else:
                return result
        else:
            if prev == "-p":
                if set(e).issubset(set("0123456789:tcp/udp")):
                    result["-p " + e] = "1"
                else:
                    return result
            elif prev == "-e":
                kv = e.split("=")
                if len(kv) >= 2:
                    val = kv[1].strip("'\"")
                    result[kv[0]] = val
                else:
                    return result
            else:
                result[prev] = e
            prev = None
    return result

import urllib.parse

def search_offers(max_price, api_key):
    base_url = "https://console.vast.ai/api/v0/bundles/"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    url = base_url+"?q={\"gpu_ram\":\">=4\"}"
    
    print("url", url)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json = response.json()
        return json["offers"]

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        print(f"Response: {response.text if response else 'No response'}")
        raise

def create_instance(offer_id, image, env=None):
    json_blob = {
        "client_id": "me",
        "image": image,
        "env": parse_env(env),
        "price": 0,  # Assuming a default value of 0 for price
        "disk": 0,  # Assuming a default value of 0 for disk
        "label": "",  # Assuming an empty string for label
        "extra": "",
        "onstart": "",
        "runtype": "ssh",
        "image_login": "",
        "python_utf8": False,
        "lang_utf8": False,
        "use_jupyter_lab": False,
        "jupyter_dir": "",
        "create_from": "",
        "force": False
    }
    url = apiurl(f"/asks/{offer_id}/")
    print(f"Request URL: {url}")
    print(f"Request JSON: {json_blob}")
    response = http_put(url, headers=headers, json=json_blob)
    return response.json()


def destroy_instance(instance_id):
    url = apiurl(f"/instances/{instance_id}/")
    response = http_del(url, headers={}, json={})
    return response.json()

def execute_command(instance_id, command):
    url = apiurl(f"/instances/command/{instance_id}/")
    json_blob = {"command": command}
    response = http_put(url, headers={}, json=json_blob)
    result_url = response.json().get("result_url", None)
    if result_url is None:
        api_key_id_h = hashlib.md5(
            (api_key + str(instance_id)).encode("utf-8")
        ).hexdigest()
        result_url = (
            "https://s3.amazonaws.com/vast.ai/instance_logs/"
            + api_key_id_h
            + "C.log"
        )
    for i in range(30):
        time.sleep(0.3)
        r = requests.get(result_url)
        if r.status_code == 200:
            return r.text
    return None

def rent_nodes(max_price, max_nodes, image, api_key, env=None):
    offers = search_offers(max_price, api_key)
    rented_nodes = []
    for offer in offers:
        print(f"Offer: {offer}")
        if len(rented_nodes) >= max_nodes:
            break
        try:
            instance = create_instance(offer["id"], image, env)
            rented_nodes.append(instance)
            print(f"Rented node: {instance['id']}")
        except Exception as e:
            print(f"Error renting node: {offer['id']}, {str(e)}")
    return rented_nodes

def start_workers(nodes, image, env_vars=None):
    for node in nodes:
        try:
            execute_command(node["id"], f"docker pull {image}")
            env_vars_str = " ".join([f"-e {var}" for var in env_vars]) if env_vars else ""
            execute_command(node["id"], f"docker run -d --name worker {env_vars_str} {image}")
            print(f"Worker started on node: {node['id']}")
        except Exception as e:
            print(f"Error starting worker on node: {node['id']}, {str(e)}")

def terminate_nodes(nodes):
    for node in nodes:
        try:
            execute_command(node["id"], "docker stop worker")
            execute_command(node["id"], "docker rm worker")
            destroy_instance(node["id"])
            print(f"Node terminated: {node['id']}")
        except Exception as e:
            print(f"Error terminating node: {node['id']}, {str(e)}")

def main(max_price, max_nodes, image, api_key, env=None, env_vars=None):
    nodes = rent_nodes(max_price, max_nodes, image, api_key, env)
    start_workers(nodes, image, env_vars)
    input("Press Enter to terminate nodes...")
    terminate_nodes(nodes)


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--max-price", type=float, required=True, help="Maximum price per hour")
#     parser.add_argument("--max-nodes", type=int, required=True, help="Maximum number of nodes")
#     parser.add_argument("--image", type=str, required=True, help="Docker image to run")
#     parser.add_argument("--env", type=str, default=None, help="Environment variables for the container")
#     parser.add_argument("--api-key", required=True, help="Vast.ai API key")
#     parser.add_argument("--env-vars", type=str, default="", help="Comma-separated list of environment variables (e.g., 'VAR1=value1,VAR2=value2')")
#     args = parser.parse_args()
#     api_key = args.api_key
#     headers["Authorization"] = "Bearer " + api_key
#     env_vars = args.env_vars.split(",") if args.env_vars else None
#     main(args.max_price, args.max_nodes, args.image, api_key, args.env, env_vars)

import unittest
import os
import sys
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

from simian.distributed_vast import rent_nodes, start_workers, terminate_nodes, headers
from simian.utils import get_env_vars

class TestDistributedVast(unittest.TestCase):
    def test_rent_run_terminate(self):
        env_vars = get_env_vars()
        vast_api_key = os.getenv("VAST_API_KEY") or env_vars.get("VAST_API_KEY")
        
        # Assert that vast_api_key exists
        self.assertIsNotNone(vast_api_key, "Vast API key not found.")
        
        headers["Authorization"] = "Bearer " + vast_api_key
        
        max_price = 0.5
        max_nodes = 1
        image = "arfx/simian-worker:latest"
        env = None
        
        nodes = rent_nodes(max_price, max_nodes, image, vast_api_key, env)

        self.assertEqual(len(nodes), 1)
        
        start_workers(nodes, image)
        # Perform any additional assertions or checks here
        
        terminate_nodes(nodes)

if __name__ == "__main__":
    unittest.main()