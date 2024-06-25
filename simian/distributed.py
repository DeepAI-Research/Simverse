import argparse
import json
import logging
import os
import time
from tqdm import tqdm
from typing import Dict

from distributaur.distributaur import Distributaur

from .worker import run_job

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    def get_env_vars(path: str = ".env") -> Dict[str, str]:
        """Get the environment variables from the specified file."""
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
            "api_key": args.api_key or env_vars.get("VAST_API_KEY", ""),
            "redis_host": args.redis_host or env_vars.get("REDIS_HOST", "localhost"),
            "redis_port": args.redis_port or int(env_vars.get("REDIS_PORT", 6379)),
            "redis_user": args.redis_user or env_vars.get("REDIS_USER", ""),
            "redis_password": args.redis_password or env_vars.get("REDIS_PASSWORD", ""),
            "hf_token": args.hf_token or env_vars.get("HF_TOKEN", ""),
            "hf_repo_id": args.hf_repo_id or env_vars.get("HF_REPO_ID", ""),
            "hf_path": args.hf_path or env_vars.get("HF_PATH", ""),
            "broker_pool_limit": args.broker_pool_limit
            or int(env_vars.get("BROKER_POOL_LIMIT", 1)),
        }

        # Load combinations from file
        with open(settings["combinations_file"], "r") as f:
            combinations = json.load(f)
            settings["combinations"] = combinations["combinations"]

        return settings

    def start_new_job(args):
        logger.info("Starting a new job...")
        settings = get_settings(args)

        # Override environment variables with provided arguments
        os.environ["REDIS_HOST"] = args.redis_host or settings["redis_host"]
        os.environ["REDIS_PORT"] = str(args.redis_port or settings["redis_port"])
        os.environ["REDIS_USER"] = args.redis_user or settings["redis_user"]
        os.environ["REDIS_PASSWORD"] = args.redis_password or settings["redis_password"]
        os.environ["HF_TOKEN"] = args.hf_token or settings["hf_token"]
        os.environ["HF_REPO_ID"] = args.hf_repo_id or settings["hf_repo_id"]
        os.environ["HF_PATH"] = args.hf_path or settings["hf_path"]

        job_config = {
            "max_price": settings["max_price"],
            "max_nodes": settings["max_nodes"],
            "start_index": settings["start_index"],
            "end_index": settings["end_index"],
            "combinations": settings["combinations"],
            "width": settings["width"],
            "height": settings["height"],
            "output_dir": settings["output_dir"],
            "hdri_path": settings["hdri_path"],
            "start_frame": settings["start_frame"],
            "end_frame": settings["end_frame"],
            "api_key": settings["api_key"],
            "hf_token": settings["hf_token"],
            "hf_repo_id": settings["hf_repo_id"],
            "hf_path": settings["hf_path"],
            "redis_host": settings["redis_host"],
            "redis_port": settings["redis_port"],
            "redis_user": settings["redis_user"],
            "redis_password": settings["redis_password"],
            "broker_pool_limit": settings["broker_pool_limit"],
        }

        print("*** JOB CONFIG")
        print(job_config)

        distributaur = Distributaur(
            hf_repo_id=job_config["hf_repo_id"],
            hf_token=job_config["hf_token"],
            vast_api_key=job_config["api_key"],
            redis_host=job_config["redis_host"],
            redis_port=job_config["redis_port"],
            redis_username=job_config["redis_user"],
            redis_password=job_config["redis_password"],
            broker_pool_limit=job_config["broker_pool_limit"],
        )

        max_price = job_config["max_price"]
        max_nodes = job_config["max_nodes"]
        docker_image = "arfx/simian-worker:latest"
        module_name = "simian.worker"

        print("MAX PRICE: ", max_price)
        print("SEARCHING FOR NODES...")
        num_nodes_avail = len(distributaur.search_offers(max_price))
        print("TOTAL NODES AVAILABLE: ", num_nodes_avail)

        rented_nodes = distributaur.rent_nodes(
            max_price, max_nodes, docker_image, module_name
        )

        print("TOTAL RENTED NODES: ", len(rented_nodes))
        print(rented_nodes)

        distributaur.register_function(run_job)

        tasks = []

        # Submit tasks
        for combination_index in range(
            job_config["start_index"],
            min(job_config["end_index"], len(job_config["combinations"])),
        ):
            task = distributaur.execute_function(
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

        # Wait for tasks to complete
        print("Tasks submitted to queue. Waiting for tasks to complete...")


        prev_tasks = 0
        first_task_done = False
        queue_start_time = time.time()
        # Wait for the tasks to complete
        print("Tasks submitted to queue. Initializing queue...")
        with tqdm(total=len(tasks), unit="task") as pbar:
            while not all(task.ready() for task in tasks):
                current_tasks = sum([task.ready() for task in tasks])
                pbar.update(current_tasks - pbar.n)

                if current_tasks > 0:
                    # begin estimation from time of first task
                    if not first_task_done:
                        first_task_done = True
                        first_task_start_time = time.time()
                        print("Initialization completed. Tasks started...")

                    # calculate and print total elapsed time and estimated time left
                    end_time = time.time()
                    elapsed_time = end_time - first_task_start_time
                    time_per_tasks = elapsed_time / current_tasks
                    time_left = time_per_tasks * (len(tasks) - current_tasks)

                    pbar.set_postfix(
                        elapsed=f"{elapsed_time:.2f}s", time_left=f"{time_left:.2f}"
                    )            

        print("All tasks have been completed!")

    parser = argparse.ArgumentParser(description="Simian CLI")
    parser.add_argument("--start-index", type=int, help="Starting index for rendering")
    parser.add_argument(
        "--combinations-file", help="Path to the combinations JSON file"
    )
    parser.add_argument("--end_index", type=int, help="Ending index for rendering")
    parser.add_argument("--start_frame", type=int, help="Starting frame number")
    parser.add_argument("--end_frame", type=int, help="Ending frame number")
    parser.add_argument("--width", type=int, help="Rendering width in pixels")
    parser.add_argument("--height", type=int, help="Rendering height in pixels")
    parser.add_argument("--output_dir", help="Output directory")
    parser.add_argument("--hdri_path", help="HDRI path")
    parser.add_argument("--max_price", type=float, help="Maximum price per hour")
    parser.add_argument("--max_nodes", type=int, help="Maximum number of nodes")
    parser.add_argument("--api_key", help="Vast.ai API key")
    parser.add_argument("--redis_host", help="Redis host")
    parser.add_argument("--redis_port", type=int, help="Redis port")
    parser.add_argument("--redis_user", help="Redis user")
    parser.add_argument("--redis_password", help="Redis password")
    parser.add_argument("--hf_token", help="Hugging Face token")
    parser.add_argument("--hf_repo-id", help="Hugging Face repository ID")
    parser.add_argument("--hf_path", help="Hugging Face path")
    parser.add_argument(
        "--broker_pool_limit", type=int, help="Limit on redis pool size"
    )
    args = parser.parse_args()

    start_new_job(args)
