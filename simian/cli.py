import argparse
import os
import signal
import sys
import time
import json
from typing import Dict

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

from distributaur.core import (
    configure,
    execute_function,
    register_function,
    get_env_vars,
    config,
    redis_client,
    check_job_status,
    attach_to_existing_job,
    monitor_job_status,
)

from distributaur.vast import rent_nodes, terminate_nodes, handle_signal

from simian.worker import *


def get_env_vars(path: str = ".env") -> Dict[str, str]:
    """Get the environment variables from the specified file.

    Args:
        path (str): The path to the file containing the environment variables. Defaults to ".env".

    Returns:
        Dict[str, str]: A dictionary containing the environment variables.
    """
    env_vars = {}
    if not os.path.exists(path):
        return env_vars
    with open(path, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            env_vars[key] = value
    return env_vars


def get_settings(args):
    env_vars = get_env_vars(".env")

    settings = {
        "start_index": args.start_index or int(env_vars.get("START_INDEX", 0)),
        "combinations_file": args.combinations_file
        or env_vars.get("COMBINATIONS_FILE", "combinations.json"),
        "end_index": args.end_index or int(env_vars.get("END_INDEX", 100)),
        "start_frame": args.start_frame or int(env_vars.get("START_FRAME", 0)),
        "end_frame": args.end_frame or int(env_vars.get("END_FRAME", 65)),
        "width": args.width or int(env_vars.get("WIDTH", 1920)),
        "height": args.height or int(env_vars.get("HEIGHT", 1080)),
        "output_dir": args.output_dir or env_vars.get("OUTPUT_DIR", "./renders"),
        "hdri_path": args.hdri_path or env_vars.get("HDRI_PATH", "./backgrounds"),
        "max_price": args.max_price or float(env_vars.get("MAX_PRICE", 0.1)),
        "max_nodes": args.max_nodes or int(env_vars.get("MAX_NODES", 1)),
        "image": args.image
        or env_vars.get("DOCKER_IMAGE", "arfx/simian-worker:latest"),
        "api_key": args.api_key or env_vars.get("VAST_API_KEY", ""),
        "redis_host": args.redis_host or env_vars.get("REDIS_HOST", "localhost"),
        "redis_port": args.redis_port or int(env_vars.get("REDIS_PORT", 6379)),
        "redis_user": args.redis_user or env_vars.get("REDIS_USER", ""),
        "redis_password": args.redis_password or env_vars.get("REDIS_PASSWORD", ""),
        "hf_token": args.hf_token or env_vars.get("HF_TOKEN", ""),
        "hf_repo_id": args.hf_repo_id or env_vars.get("HF_REPO_ID", ""),
        "hf_path": args.hf_path or env_vars.get("HF_PATH", ""),
    }

    # Load combinations from file
    with open(settings["combinations_file"], "r") as f:
        combinations = json.load(f)
        settings["combinations"] = combinations["combinations"]

    return settings


def setup_and_run(job_config):
    tasks = []
    for combination_index in range(job_config["start_index"], job_config["end_index"]):
        task = execute_function(
            "run_job",
            {
                "combination_index": combination_index,
                "combination": job_config["combinations"][combination_index],
                "width": job_config["width"],
                "height": job_config["height"],
                "output_dir": job_config["output_dir"],
                "hdri_path": job_config["hdri_path"],
                "start_frame": job_config["start_frame"],
                "end_frame": job_config["end_frame"],
            },
        )
        tasks.append(task)

    for task in tasks:
        print(f"Task {task.id} dispatched.")

    while not all(task.ready() for task in tasks):
        time.sleep(1)

    print("All tasks have been completed!")


def start_new_job(args):
    print("Starting a new job...")
    settings = get_settings(args)
    job_id = args.job_id or input("Enter a unique job ID: ")

    # Override environment variables with provided arguments
    os.environ["REDIS_HOST"] = args.redis_host or settings["redis_host"]
    os.environ["REDIS_PORT"] = str(args.redis_port or settings["redis_port"])
    os.environ["REDIS_USER"] = args.redis_user or settings["redis_user"]
    os.environ["REDIS_PASSWORD"] = args.redis_password or settings["redis_password"]
    os.environ["HF_TOKEN"] = args.hf_token or settings["hf_token"]
    os.environ["HF_REPO_ID"] = args.hf_repo_id or settings["hf_repo_id"]
    os.environ["HF_PATH"] = args.hf_path or settings["hf_path"]

    print("Renting nodes on Vast.ai...")
    # Rent nodes from vast.ai
    nodes = rent_nodes(
        max_price=settings["max_price"],
        max_nodes=settings["max_nodes"],
        image=settings["image"],
        api_key=settings["api_key"],
    )
    print("Nodes rented successfully!")

    # Set up signal handler for graceful shutdown
    signal_handler = handle_signal(nodes)
    signal.signal(signal.SIGINT, signal_handler)

    print("Configuring distributaur...")

    job_config = {
        "job_id": job_id,
        "max_price": settings["max_price"],
        "max_nodes": settings["max_nodes"],
        "docker_image": settings["image"],
        "start_index": settings["start_index"],
        "end_index": settings["end_index"],
        "combinations": settings["combinations"],
        "width": settings["width"],
        "height": settings["height"],
        "output_dir": settings["output_dir"],
        "hdri_path": settings["hdri_path"],
        "start_frame": settings["start_frame"],
        "end_frame": settings["end_frame"],
    }

    # Check if the job is already running
    if attach_to_existing_job(job_id):
        print("Attaching to an existing job...")
        # Monitor job status and handle success/failure conditions
        monitor_job_status(job_id)
    else:
        print("Setting up and running the job...")
        # Run the job
        setup_and_run(job_config)
        # Monitor job status and handle success/failure conditions
        monitor_job_status(job_id)
    print("Job completed!")
    # Terminate the rented nodes
    terminate_nodes(nodes)


def main():
    parser = argparse.ArgumentParser(description="Simian CLI")
    parser.add_argument("action", choices=["start", "list"], help="Action to perform")
    parser.add_argument("--job-id", help="Unique job ID")
    parser.add_argument("--start-index", type=int, help="Starting index for rendering")
    parser.add_argument(
        "--combinations-file", help="Path to the combinations JSON file"
    )
    parser.add_argument("--end-index", type=int, help="Ending index for rendering")
    parser.add_argument("--start-frame", type=int, help="Starting frame number")
    parser.add_argument("--end-frame", type=int, help="Ending frame number")
    parser.add_argument("--width", type=int, help="Rendering width in pixels")
    parser.add_argument("--height", type=int, help="Rendering height in pixels")
    parser.add_argument("--output-dir", help="Output directory")
    parser.add_argument("--hdri-path", help="HDRI path")
    parser.add_argument("--max-price", type=float, help="Maximum price per hour")
    parser.add_argument("--max-nodes", type=int, help="Maximum number of nodes")
    parser.add_argument("--image", help="Docker image")
    parser.add_argument("--api-key", help="Vast.ai API key")
    parser.add_argument("--redis-host", help="Redis host")
    parser.add_argument("--redis-port", type=int, help="Redis port")
    parser.add_argument("--redis-user", help="Redis user")
    parser.add_argument("--redis-password", help="Redis password")
    parser.add_argument("--hf-token", help="Hugging Face token")
    parser.add_argument("--hf-repo-id", help="Hugging Face repository ID")
    parser.add_argument("--hf-path", help="Hugging Face path")
    args = parser.parse_args()

    if args.action == "start":
        start_new_job(args)
    elif args.action == "list":
        list_jobs()


def list_jobs():
    job_keys = redis_client.keys("celery-task-meta-*")
    jobs = {}
    for key in job_keys:
        job_id = key.decode("utf-8").split("-")[-1]
        if job_id not in jobs:
            jobs[job_id] = check_job_status(job_id)

    if not jobs:
        print("No existing jobs found.")
        return

    print("Existing jobs:")
    for job_id, status_counts in jobs.items():
        print(f"Job ID: {job_id}")
        print(f"  Status: {status_counts}")
        print()

    while True:
        selection = input(
            "Enter a job ID to attach to, 'd' to delete a job, 'c' to clear all jobs, or 'q' to quit: "
        )
        if selection == "q":
            break
        elif selection == "c":
            confirm = input("Are you sure you want to clear all jobs? (y/n): ")
            if confirm.lower() == "y":
                redis_client.flushdb()
                print("All jobs cleared.")
            break
        elif selection == "d":
            job_id = input("Enter the job ID to delete: ")
            if job_id in jobs:
                keys = redis_client.keys(f"celery-task-meta-*{job_id}")
                for key in keys:
                    redis_client.delete(key)
                print(f"Job {job_id} deleted.")
            else:
                print(f"Job {job_id} not found.")
        elif selection in jobs:
            print(f"Attaching to job {selection}...")
            sys.argv = [sys.argv[0], "--job-id", selection]
            break
        else:
            print("Invalid selection.")


if __name__ == "__main__":
    main()
