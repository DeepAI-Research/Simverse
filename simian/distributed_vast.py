# distributed_vast.py
import os
import sys
import time

# Append Simian to sys.path before importing from package
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from simian.utils import get_combination_objects

# Import necessary functions and classes from vast.py
from vendor.vast import (
    apiurl,
    http_put,
    http_del,
    http_post,
    parse_query,
    offers_fields,
    offers_alias,
    offers_mult,
    get_runtype,
    parse_env,
)

class DistributedVast:
    def __init__(self, args):
        self.args = args

    def search_offers(self, query):
        base_query = {
            "verified": {"eq": True},
            "external": {"eq": False},
            "rentable": {"eq": True},
            "rented": {"eq": False},
        }
        query_params = parse_query(query, base_query, offers_fields, offers_alias, offers_mult)
        url = apiurl(self.args, "/bundles/")
        r = http_post(self.args, url, headers={}, json={"q": query_params})
        r.raise_for_status()
        return r.json()["offers"]

    def create_instance(self, offer_id, image, env=None):
        runtype = get_runtype(self.args)
        json_blob = {
            "client_id": "me",
            "image": image,
            "env": parse_env(env),
            "runtype": runtype,
        }
        url = apiurl(self.args, f"/asks/{offer_id}/")
        r = http_put(self.args, url, headers={}, json=json_blob)
        r.raise_for_status()
        return r.json()

    def destroy_instance(self, instance_id):
        url = apiurl(self.args, f"/instances/{instance_id}/")
        r = http_del(self.args, url, headers={}, json={})
        r.raise_for_status()
        return r.json()

    def execute(self, instance_id, command):
        url = apiurl(self.args, f"/instances/command/{instance_id}/")
        json_blob = {"command": command}
        r = http_put(self.args, url, headers={}, json=json_blob)
        r.raise_for_status()
        return r.json()

    def rent_nodes(self, max_price, max_nodes, image, env=None):
        # Search for GPU nodes that meet the requirements
        query = f"gpu_ram >= 4 total_flops > 1 dph <= {max_price}"
        offers = self.search_offers(query)

        # Filter offers and rent nodes
        rented_nodes = []
        for offer in offers:
            if len(rented_nodes) >= max_nodes:
                break
            try:
                instance = self.create_instance(offer["id"], image, env)
                rented_nodes.append(instance)
                print(f"Rented node: {instance['id']}")
            except Exception as e:
                print(f"Error renting node: {offer['id']}, {str(e)}")
        return rented_nodes

    def start_workers(self, nodes, image, env_vars=None):
        for node in nodes:
            try:
                # Pull the Docker container
                self.execute(node["id"], f"docker pull {image}")
                
                # Construct the environment variables string
                env_vars_str = " ".join([f"-e {var}" for var in env_vars]) if env_vars else ""
                
                # Run the Docker container with environment variables
                self.execute(node["id"], f"docker run -d --name worker {env_vars_str} {image}")
                print(f"Worker started on node: {node['id']}")
            except Exception as e:
                print(f"Error starting worker on node: {node['id']}, {str(e)}")


    def terminate_nodes(self, nodes):
        for node in nodes:
            try:
                # Stop and remove the Docker container
                self.execute(node["id"], "docker stop worker")
                self.execute(node["id"], "docker rm worker")
                # Destroy the node
                self.destroy_instance(node["id"])
                print(f"Node terminated: {node['id']}")
            except Exception as e:
                print(f"Error terminating node: {node['id']}, {str(e)}")

def main(args):
    dist_vast = DistributedVast(args)
    nodes = dist_vast.rent_nodes(args.max_price, args.max_nodes, args.image, args.env)
    dist_vast.start_workers(nodes, args.image)
    input("Press Enter to terminate nodes...")
    dist_vast.terminate_nodes(nodes)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--max-price", type=float, required=True, help="Maximum price per hour")
    parser.add_argument("--max-nodes", type=int, required=True, help="Maximum number of nodes")
    parser.add_argument("--image", type=str, required=True, help="Docker image to run")
    parser.add_argument("--env", type=str, default=None, help="Environment variables for the container")
    parser.add_argument("--url", default="https://console.vast.ai", help="Vast.ai API URL")
    parser.add_argument("--api-key", required=True, help="Vast.ai API key")
    parser.add_argument("--env-vars", type=str, default="", help="Comma-separated list of environment variables (e.g., 'VAR1=value1,VAR2=value2')")

    args = parser.parse_args()

    main(args)