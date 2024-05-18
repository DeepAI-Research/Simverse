import os
import sys
import tempfile

current_dir = os.path.dirname(os.path.abspath(__file__))
combiner_path = os.path.join(current_dir, "../")
sys.path.append(combiner_path)

from simian.utils import upload_to_huggingface, get_env_vars

def test_upload_to_huggingface():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file
        test_file = "test.txt"
        test_file_path = os.path.join(temp_dir, test_file)
        with open(test_file_path, "w") as f:
            f.write("Test content")

        # Read environment variables from .env file
        env_vars = get_env_vars()
        hf_token = env_vars.get("HF_TOKEN") or os.getenv("HF_TOKEN")
        repo_id = env_vars.get("HF_REPO_ID") or os.getenv("HF_REPO_ID")
        repo_path = env_vars.get("HF_PATH") or os.getenv("HF_PATH")

        # Check if the required environment variables are set
        assert hf_token is not None, "HF_TOKEN is not set in .env file"
        assert repo_id is not None, "HF_REPO_ID is not set in .env file"
        assert repo_path is not None, "HF_PATH is not set in .env file"

        # Call the upload_to_huggingface function
        upload_to_huggingface(temp_dir)

        # Check if the file exists in the Hugging Face repository
        from huggingface_hub import HfApi
        api = HfApi(token=hf_token)
        file_exists = api.file_exists(repo_id=repo_id, filename=os.path.join(repo_path, test_file), repo_type="dataset")
        assert file_exists, f"File {test_file} was not uploaded to the Hugging Face repository"
        # delete the file
        api.delete_file(repo_id=repo_id, path_in_repo=os.path.join(repo_path, test_file), repo_type="dataset")
        assert not api.file_exists(repo_id=repo_id, filename=os.path.join(repo_path, test_file), repo_type="dataset"), f"File {test_file} was not deleted from the Hugging Face repository"
        
if __name__ == "__main__":
    test_upload_to_huggingface()