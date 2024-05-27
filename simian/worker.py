import json
import os
import sys
import subprocess
from typing import Any, Dict

from distributaur.core import register_function, app

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

celery = app


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


def upload_to_huggingface(output_dir: str, repo_dir: str) -> None:
    """Upload the rendered outputs to a Hugging Face repository."""
    env_vars = get_env_vars()
    hf_token = os.getenv("HF_TOKEN") or env_vars.get("HF_TOKEN")
    repo_id = os.getenv("HF_REPO_ID") or env_vars.get("HF_REPO_ID")
    from huggingface_hub import HfApi

    api = HfApi(token=hf_token)

    for root, dirs, files in os.walk(output_dir):
        for file in files:
            local_path = os.path.join(root, file)
            path_in_repo = os.path.join(repo_dir, file) if repo_dir else file

            try:
                print(
                    f"Uploading {local_path} to Hugging Face repo {repo_id} at {path_in_repo}"
                )
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


def run_job(
    combination_index: int,
    combination: Dict[str, Any],
    width: int,
    height: int,
    output_dir: str,
    hdri_path: str,
    start_frame: int = 0,
    end_frame: int = 65,
) -> None:
    """
    Run a rendering job with the specified combination index and settings.

    Args:
        combination_index (int): The index of the combination to render.
        combination (Dict[str, Any]): The combination dictionary.
        width (int): The width of the rendered output.
        height (int): The height of the rendered output.
        output_dir (str): The directory to save the rendered output.
        hdri_path (str): The path to the HDRI file.
        start_frame (int, optional): The starting frame number. Defaults to 0.
        end_frame (int, optional): The ending frame number. Defaults to 65.

    Returns:
        None
    """
    combination = json.dumps(combination)
    combination = '"' + combination.replace('"', '\\"') + '"'

    os.makedirs(output_dir, exist_ok=True)

    args = f"--width {width} --height {height} --combination_index {combination_index}"
    args += f" --output_dir {output_dir}"
    args += f" --hdri_path {hdri_path}"
    args += f" --start_frame {start_frame} --end_frame {end_frame}"
    args += f" --combination {combination}"

    command = f"{sys.executable} simian/render.py -- {args}"
    print("Worker running: ", command)

    subprocess.run(["bash", "-c", command], check=False)

    upload_to_huggingface(output_dir)

    for file in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


register_function(run_job)
