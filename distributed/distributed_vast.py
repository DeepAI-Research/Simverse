import os
import sys
import time

# Append Simian to sys.path before importing from package
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

from simian.utils import get_combination_objects
from distributed.vendor.vast import create_instance, search_offers, copy, destroy_instance, execute

def rent_nodes(max_price, max_nodes):    
    # Search for GPU nodes that meet the requirements
    query = f"gpu_ram >= 4 total_flops > 1 dph <= {max_price}"
    offers = search_offers(query)
    
    # Filter offers and rent nodes
    rented_nodes = []
    for offer in offers:
        if len(rented_nodes) >= max_nodes:
            break
        
        try:
            instance = create_instance(offer["id"])
            rented_nodes.append(instance)
            print(f"Rented node: {instance['id']}")
        except Exception as e:
            print(f"Error renting node: {offer['id']}, {str(e)}")
    
    return rented_nodes

def start_workers(nodes):
    for node in nodes:
        try:
            # Copy the Dockerfile to the node
            copy("Dockerfile", f"{node['id']}:/root/Dockerfile")
            
            # Build and run the Docker container
            execute(node["id"], "docker build -t blender-worker .")
            execute(node["id"], "docker run -d --name blender-worker blender-worker")
            print(f"Worker started on node: {node['id']}")
        except Exception as e:
            print(f"Error starting worker on node: {node['id']}, {str(e)}")

def monitor_jobs(nodes):
    completed_jobs = 0
    total_jobs = len(get_combination_objects())
    
    while completed_jobs < total_jobs:
        for node in nodes:
            try:
                # Check the status of the worker
                status = execute(node["id"], "docker ps -a --filter name=blender-worker --format '{{.Status}}'")
                if "Exited" in status:
                    completed_jobs += 1
                    print(f"Job completed on node: {node['id']}")
            except Exception as e:
                print(f"Error monitoring job on node: {node['id']}, {str(e)}")
        
        time.sleep(60)  # Wait for 60 seconds before checking again
    
    print("All jobs completed")

def terminate_nodes(nodes):
    for node in nodes:
        try:
            # Stop and remove the Docker container
            execute(node["id"], "docker stop blender-worker")
            execute(node["id"], "docker rm blender-worker")
            
            # Destroy the node
            destroy_instance(node["id"])
            print(f"Node terminated: {node['id']}")
        except Exception as e:
            print(f"Error terminating node: {node['id']}, {str(e)}")

def main(max_price, max_nodes):
    nodes = rent_nodes(max_price, max_nodes)
    start_workers(nodes)
    monitor_jobs(nodes)
    terminate_nodes(nodes)

if __name__ == "__main__":
    max_price = float(sys.argv[1])
    max_nodes = int(sys.argv[2])
    main(max_price, max_nodes)