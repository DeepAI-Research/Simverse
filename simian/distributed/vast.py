import os
import sys
import requests
import json
from typing import Dict
import time
import hashlib
import re
from redis import Redis
from simian.utils import get_env_vars, get_redis_values
import signal

server_url_default = "https://console.vast.ai"
headers = {}

redis_client = Redis.from_url(get_redis_values())

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
    url = base_url+"?q={\"gpu_ram\":\">=4\",\"rentable\":{\"eq\":true},\"dph_total\":{\"lte\":0.1480339514817041},\"sort_option\":{\"0\":[\"dph_total\",\"asc\"],\"1\":[\"total_flops\",\"asc\"]}}"
    
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

def create_instance(offer_id, image, env):
    # check that the env is a dictionary and has the vars REDIS_HOST, REDIS_PORT, REDIS_USER, REDIS_PASSWORD, HF_TOKEN, HF_REPO_ID, HF_PATH, VAST_API_KEY
    if env is None:
        raise ValueError("env is required")
    
    if not isinstance(env, dict):
        raise ValueError("env must be a dictionary")
    
    if not all(k in env for k in ["REDIS_HOST", "REDIS_PORT", "REDIS_USER", "REDIS_PASSWORD"]):
        # warn about missing redis env vars
        print("Warning: Missing Redis environment variables")
        
    if not all(k in env for k in ["HF_TOKEN", "HF_REPO_ID", "HF_PATH"]):
        # warn about missing huggingface env vars
        print("Warning: Missing Hugging Face environment variables")
        
    if not "VAST_API_KEY" in env:
        # warn about missing vast api key
        print("Warning: Missing Vast API key")
        
    print("Creating instance...")
    print("VAST_API_KEY", env["VAST_API_KEY"])
    
    # print headers
    print("HEADERS", headers)
    
    json_blob = {
        "client_id": "me",
        "image": image,
        "env": "",
        "disk": 16,  # Set a non-zero value for disk
        "onstart": f"export PATH=$PATH:/ &&  cd ../ && REDIS_HOST={env['REDIS_HOST']} REDIS_PORT={env['REDIS_PORT']} REDIS_USER={env['REDIS_USER']} REDIS_PASSWORD={env['REDIS_PASSWORD']} HF_TOKEN={env['HF_TOKEN']} HF_REPO_ID={env['HF_REPO_ID']} HF_PATH={env['HF_PATH']} VAST_API_KEY={env['VAST_API_KEY']} celery -A simian.worker worker --loglevel=info",
        "runtype": "ssh ssh_proxy",
        "image_login": None,
        "python_utf8": False,
        "lang_utf8": False,
        "use_jupyter_lab": False,
        "jupyter_dir": None,
        "create_from": "",
        "template_hash_id": "250671155ccbc28d0609af524b75a80e",
        "template_id": 108305
    }
    url = apiurl(f"/asks/{offer_id}/")
    print(f"Request URL: {url}")
    print(f"Request JSON: {json_blob}")
    response = http_put(url, headers={
        "Authorization": f"Bearer {env['VAST_API_KEY']}",
        }, json=json_blob)
    return response.json()

def destroy_instance(instance_id):
    env = get_env_vars()
    headers = {
        'Authorization': f'Bearer {env["VAST_API_KEY"]}'
    }
    url = apiurl(f"/instances/{instance_id}/")
    print(f"Terminating instance: {instance_id}")
    response = http_del(url, headers=headers, json={})
    return response.json()

def rent_nodes(max_price, max_nodes, image, api_key, env=get_env_vars()):
    env['VAST_API_KEY'] = api_key or env.get("VAST_API_KEY")
    offers = search_offers(max_price, api_key)
    rented_nodes = []
    for offer in offers:
        if len(rented_nodes) >= max_nodes:
            break
        try:
            print("offer is ***")
            print(offer)
            instance = create_instance(offer["id"], image, env)
            print("INSTANCE: ")
            print(instance)
            rented_nodes.append({
                "offer_id": offer["id"],
                "instance_id": instance["new_contract"]
            })
            print(f"Rented node {offer['id']} on contract: {instance['new_contract']}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                # print the response itself
                print(f"Error renting node: {offer['id']}, {e.response.text}")
                print(f"Offer {offer['id']} is unavailable. Trying next offer...")
            else:
                print(f"Error renting node: {offer['id']}, {str(e)}")
                raise
    return rented_nodes

def terminate_nodes(nodes):
    for node in nodes:
        print("node", node)
        try:
            time.sleep(2)  # Add a delay before terminating
            destroy_instance(node["offer_id"])
        except Exception as e:
            print(f"Error terminating node: {node['offer_id']}, {str(e)}")

def check_job_status():
    # Get all keys with the prefix "task_status:"
    task_keys = redis_client.keys("task_status:*")
    
    # Count the number of tasks in each status
    status_counts = {
        "QUEUED": 0,
        "IN_PROGRESS": 0,
        "TIMEOUT": 0,
        "COMPLETE": 0,
        "FAILED": 0
    }
    
    for key in task_keys:
        status = redis_client.get(key).decode("utf-8")
        status_counts[status] += 1
    
    return status_counts

def monitor_job_status(job=None):
    while True:
        status_counts = check_job_status()
        print(f"Job status: {status_counts}")

        if status_counts["IN_PROGRESS"] == 0 and status_counts["QUEUED"] == 0:
            break

        time.sleep(10)  # Wait for 10 seconds before checking again

        # Check for tasks that have been in the IN_PROGRESS state for more than 60 minutes
        task_keys = redis_client.keys("task_status:*")
        for key in task_keys:
            status = redis_client.get(key).decode("utf-8")
            if status == "IN_PROGRESS":
                task_start_time = redis_client.get(f"task_start_time:{key.decode('utf-8').split(':')[1]}")
                if task_start_time:
                    task_start_time = float(task_start_time)
                    current_time = time.time()
                    if current_time - task_start_time > 3600:  # 60 minutes
                        redis_client.set(key, "TIMEOUT")
                        print(f"Task {key.decode('utf-8').split(':')[1]} marked as TIMEOUT by the manager")


def handle_sigint(nodes):
    print("Received SIGINT. Terminating all running workers...")
    terminate_nodes(nodes)
    sys.exit(0)

def attach_to_existing_job():
    # Check if there are any tasks with the status "IN_PROGRESS" or "QUEUED"
    status_counts = check_job_status()
    
    if status_counts["IN_PROGRESS"] > 0 or status_counts["QUEUED"] > 0:
        print("Attaching to an existing job...")
        return True
    else:
        print("No existing job found.")
        return False
