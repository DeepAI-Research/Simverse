import importlib
import json
import os
import platform
import re
import subprocess
import sys
from typing import Dict, Any


def check_imports() -> None:
    """Check and install required Python packages specified in the requirements.txt file."""
    with open("requirements.txt", "r") as f:
        requirements = [line.strip() for line in f]  # Strip newline characters and spaces

    package_name_pattern = re.compile(r"^\s*([\w\d\.\-_]+)")  # Regex to capture the package name

    for requirement in requirements:
        if requirement:  # Ensure the requirement is not an empty string
            match = package_name_pattern.search(requirement)
            if match:
                package_name = match.group(1)
                try:
                    importlib.import_module(package_name)  # Import using just the package name
                except ImportError:
                    print(f"Installing {requirement}")
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", requirement],
                        check=True,  # Ensures any error in installation raises an exception
                    )


check_imports()


def get_combination_objects(file: str = "combinations.json") -> Dict[str, Any]:
    """Fetch an array containing the combinations of objects to render.

    Args:
        file (str): The path to the JSON file containing the combinations. Defaults to "combinations.json".

    Returns:
        Dict[str, Any]: A dictionary containing the combinations.
    """
    with open(file, "r") as f:
        combinations = json.load(f)
    return combinations["combinations"]


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


def get_redis_values(path: str = ".env") -> str:
    """Get the Redis connection URL from the specified file.

    Args:
        path (str): The path to the file containing the environment variables. Defaults to ".env".

    Returns:
        str: The Redis connection URL.
    """
    env_vars = get_env_vars(path)

    host = env_vars.get("REDIS_HOST", os.getenv("REDIS_HOST", "localhost"))
    password = env_vars.get("REDIS_PASSWORD", os.getenv("REDIS_PASSWORD", None))
    port = env_vars.get("REDIS_PORT", os.getenv("REDIS_PORT", 6379))
    username = env_vars.get("REDIS_USER", os.getenv("REDIS_USER", None))
    if password is None:
        redis_url = f"redis://{host}:{port}"
    else:
        redis_url = f"redis://{username}:{password}@{host}:{port}"
    return redis_url


def upload_outputs(output_dir: str) -> None:
    """Upload the rendered outputs to a Hugging Face repository.

    Args:
        output_dir (str): The directory where the rendered outputs are saved.
    """
    upload_to_huggingface(output_dir)


def upload_to_huggingface(output_dir: str) -> None:
    """Upload the rendered outputs to a Hugging Face repository.

    Args:
        output_dir (str): The directory where the rendered outputs are saved.
    """
    from huggingface_hub import HfApi

    env_vars = get_env_vars()
    hf_token = os.getenv("HF_TOKEN") or env_vars.get("HF_TOKEN")
    repo_id = os.getenv("HF_REPO_ID") or env_vars.get("HF_REPO_ID")
    repo_path = os.getenv("HF_PATH") or env_vars.get("HF_PATH", "")

    api = HfApi(token=hf_token)

    for root, dirs, files in os.walk(output_dir):
        for file in files:
            local_path = os.path.join(root, file)
            path_in_repo = os.path.join(repo_path, file) if repo_path else file

            try:
                api.upload_file(
                    path_or_fileobj=local_path,
                    path_in_repo=path_in_repo,
                    repo_id=repo_id,
                    token=hf_token,
                    repo_type="dataset",
                )
                print(f"Uploaded {local_path} to Hugging Face repo {repo_id} at {path_in_repo}")
            except Exception as e:
                print(f"Failed to upload {local_path} to Hugging Face repo {repo_id} at {path_in_repo}: {e}")