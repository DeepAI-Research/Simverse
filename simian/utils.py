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
    with open("combinations.json", "r") as file:
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


def get_env_vars(path=".env"):
    env_vars = {}
    if not os.path.exists(path):
        return env_vars
    with open(path, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            env_vars[key] = value
    return env_vars


def get_redis_values(path=".env"):
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


def upload_outputs(output_dir):
    # determine if s3 or huggingface environment variables are set up
    # env_vars = get_env_vars()
    # aws_access_key_id = env_vars.get("AWS_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID")
    # huggingface_token = env_vars.get("HF_TOKEN") or os.getenv("HF_TOKEN")
    # if aws_access_key_id and huggingface_token:
    #     print("Warning: Both AWS and Hugging Face credentials are set. Defaulting to Huggingface. Remove credentials to default to AWS.")
    #     upload_to_huggingface(output_dir, combination)
    # elif aws_access_key_id is None and huggingface_token is None:
    #     raise ValueError("No AWS or Hugging Face credentials found. Please set one.")
    # elif aws_access_key_id:
    #     upload_to_s3(output_dir, combination)
    # elif huggingface_token:
    upload_to_huggingface(output_dir)


# def upload_to_s3(output_dir, combination):
#     """
#     Uploads the rendered outputs to an S3 bucket.

#     Args:
#     - output_dir (str): The directory where the rendered outputs are saved.
#     - bucket_name (str): The name of the S3 bucket.
#     - s3_path (str): The path in the S3 bucket where files should be uploaded.

#     Returns:
#     - None
#     """
#     import boto3
#     from botocore.exceptions import NoCredentialsError, PartialCredentialsError

#     env_vars = get_env_vars()
#     aws_access_key_id = env_vars.get("AWS_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID")
#     aws_secret_access_key = env_vars.get("AWS_SECRET_ACCESS_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY")

#     s3_client = boto3.client(
#         "s3",
#         aws_access_key_id,
#         aws_secret_access_key
#     )

#     bucket_name = combination.get("bucket_name", os.getenv("AWS_BUCKET_NAME")) or env_vars.get("AWS_BUCKET_NAME")
#     s3_path = combination.get("upload_path", os.getenv("AWS_UPLOAD_PATH")) or env_vars.get("AWS_UPLOAD_PATH")

#     for root, dirs, files in os.walk(output_dir):
#         for file in files:
#             local_path = os.path.join(root, file)
#             s3_file_path = os.path.join(s3_path, file) if s3_path else file

#             try:
#                 s3_client.upload_file(local_path, bucket_name, s3_file_path)
#                 print(f"Uploaded {local_path} to s3://{bucket_name}/{s3_file_path}")
#             except FileNotFoundError:
#                 print(f"File not found: {local_path}")
#             except NoCredentialsError:
#                 print("AWS credentials not found.")
#             except PartialCredentialsError:
#                 print("Incomplete AWS credentials.")
#             except Exception as e:
#                 print(f"Failed to upload {local_path} to s3://{bucket_name}/{s3_file_path}: {e}")


def upload_to_huggingface(output_dir):
    """
    Uploads the rendered outputs to a Hugging Face repository.

    Args:
    - output_dir (str): The directory where the rendered outputs are saved.
    - repo_id (str): The repository ID on Hugging Face.

    Returns:
    - None
    """
    env_vars = get_env_vars()
    hf_token = os.getenv("HF_TOKEN") or env_vars.get("HF_TOKEN")
    repo_id = os.getenv("HF_REPO_ID") or env_vars.get("HF_REPO_ID")
    repo_path = os.getenv("HF_PATH") or env_vars.get("HF_PATH", "")
    from huggingface_hub import HfApi

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
                print(
                    f"Uploaded {local_path} to Hugging Face repo {repo_id} at {path_in_repo}"
                )
            except Exception as e:
                print(
                    f"Failed to upload {local_path} to Hugging Face repo {repo_id} at {path_in_repo}: {e}"
                )
