import json
import os
import sys
import tempfile
from unittest.mock import patch
from huggingface_hub import HfApi

current_dir = os.path.dirname(os.path.abspath(__file__))
combiner_path = os.path.join(current_dir, "../")
sys.path.append(combiner_path)

from simian.worker import get_env_vars, upload_to_huggingface, run_job

def test_get_env_vars():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write("KEY1=value1\nKEY2=value2")
        temp_file.close()

        env_vars = get_env_vars(temp_file.name)
        assert env_vars == {"KEY1": "value1", "KEY2": "value2"}

        os.unlink(temp_file.name)

@patch('simian.worker.subprocess.run')
@patch('simian.worker.upload_to_huggingface')
def test_run_job(mock_upload_to_huggingface, mock_subprocess_run):
    combination_index = 0
    combination = {"objects": []}
    width = 1920
    height = 1080
    output_dir = "test_output"
    hdri_path = "test_hdri"
    start_frame = 0
    end_frame = 10

    run_job(combination_index, combination, width, height, output_dir, hdri_path, start_frame, end_frame)

    combination_str = json.dumps(combination)
    combination_str = '"' + combination_str.replace('"', '\\"') + '"'

    command = f"{sys.executable} simian/render.py -- --width {width} --height {height} --combination_index {combination_index}"
    command += f" --output_dir {output_dir}"
    command += f" --hdri_path {hdri_path}"
    command += f" --start_frame {start_frame} --end_frame {end_frame}"
    command += f" --combination {combination_str}"

    mock_subprocess_run.assert_called_once_with(['bash', '-c', command], check=False)
    mock_upload_to_huggingface.assert_called_once_with(output_dir)


def test_upload_to_huggingface():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_files = ["test1.txt", "test2.txt"]
        for file in test_files:
            file_path = os.path.join(temp_dir, file)
            with open(file_path, "w") as f:
                f.write("Test content")

        # Read environment variables from .env file
        env_vars = get_env_vars()
        hf_token = env_vars.get("HF_TOKEN") or os.getenv("HF_TOKEN")
        repo_id = env_vars.get("HF_REPO_ID") or os.getenv("HF_REPO_ID")
        repo_path = env_vars.get("HF_PATH") or os.getenv("HF_PATH") or "data"

        # Check if the required environment variables are set
        assert hf_token is not None, "HF_TOKEN is not set in .env file"
        assert repo_id is not None, "HF_REPO_ID is not set in .env file"
        assert repo_path is not None, "HF_PATH is not set in .env file"

        # Call the upload_to_huggingface function
        upload_to_huggingface(temp_dir, repo_path)

        # Check if the files exist in the Hugging Face repository
        api = HfApi()
        repo_files = api.list_repo_files(
            repo_id=repo_id, repo_type="dataset", token=hf_token
        )
        for file in test_files:
            assert (
                os.path.join(repo_path, file) in repo_files
            ), f"File {os.path.join(repo_path, file)} was not uploaded to the Hugging Face repository"

        # Delete the files
        for file in test_files:
            api.delete_file(
                repo_id=repo_id,
                path_in_repo=os.path.join(repo_path, file),
                repo_type="dataset",
                token=hf_token,
            )
            # Verify the file has been deleted
            repo_files = api.list_repo_files(
                repo_id=repo_id, repo_type="dataset", token=hf_token
            )
            assert (
                os.path.join(repo_path, file) not in repo_files
            ), f"File {os.path.join(repo_path, file)} was not deleted from the Hugging Face repository"


if __name__ == "__main__":
    test_get_env_vars()
    test_run_job()
    test_upload_to_huggingface()