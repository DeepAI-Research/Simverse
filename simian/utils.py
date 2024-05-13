import importlib
import json
import os
import platform
import re
import subprocess
import sys


def check_imports() -> None:
    """
    Checks and installs required Python packages specified in the requirements.txt file.

    Args:
        None

    Returns:
        None
    """
    with open("requirements.txt", "r") as f:
        requirements = [
            line.strip() for line in f
        ]  # Strip newline characters and spaces

    package_name_pattern = re.compile(
        r"^\s*([\w\d\.\-_]+)"
    )  # Regex to capture the package name

    for requirement in requirements:
        if requirement:  # Ensure the requirement is not an empty string
            match = package_name_pattern.search(requirement)
            if match:
                package_name = match.group(1)
                try:
                    importlib.import_module(
                        package_name
                    )  # Import using just the package name
                except ImportError:
                    print(f"Installing {requirement}")
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", requirement],
                        check=True,  # Ensures any error in installation raises an exception
                    )


check_imports()

def get_combination_objects(file="combinations.json") -> dict:
    """
    Fetches an array containing the combinations of objects to render.
    
    Args:
    - file (str): The path to the JSON file containing the combinations.
    
    Returns:
    - dict: A dictionary containing the combinations.
    """
    with open('combinations.json', 'r') as file:
        combinations = json.load(file)
    return combinations["combinations"]


def get_blender_path():
    # if we are on macOS, then application_path is /Applications/Blender.app/Contents/MacOS/Blender
    if platform.system() == "Darwin":
        application_path = "/Applications/Blender.app/Contents/MacOS/Blender"
    else:
        application_path = "./blender/blender"
    if not os.path.exists(application_path):
        raise FileNotFoundError(f"Blender not found at {application_path}.")
    return application_path


def get_redis_values(path=".env"):

    # look for .env file, throw error if it cannot be found
    if not os.path.exists(path):
        raise FileNotFoundError("No .env file found")
    
    env_vars = {}
    with open(path, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            env_vars[key] = value
            
    # set the env vars
    os.environ.update(env_vars)
    
    host = env_vars.get("REDIS_HOST", "localhost")
    password = env_vars.get("REDIS_PASSWORD", None)
    port = env_vars.get("REDIS_PORT", 6379)
    username = env_vars.get("REDIS_USER", None)
    if password is None:
        redis_url = f"redis://{host}:{port}"
    else:
        redis_url = f"redis://{username}:{password}@{host}:{port}"
    return redis_url