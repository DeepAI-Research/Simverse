import json
import logging
import os
import sys
import subprocess
import time
import random
import shutil
from huggingface_hub import HfApi
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def run_job(
    combination_indeces: List[Any],
    combinations: List[Dict],
    width: int,
    height: int,
    output_dir: str,
    hdri_path: str,
    start_frame: int = 0,
    end_frame: int = 65
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
    str_combinations = []
    for combination in combinations:
        str_combination = json.dumps(combination)
        str_combination = '"' + str_combination.replace('"', '\\"') + '"'
        str_combinations.append(str_combination)

    output_dir = output_dir + str(time.time())

    os.makedirs(output_dir, exist_ok=True)

    batch_size = len(combination_indeces)
    for i in range(batch_size):

        args = f"--width {width} --height {height} --combination_index {combination_indeces[i]}"
        args += f" --output_dir {output_dir}"
        args += f" --hdri_path {hdri_path}"
        args += f" --start_frame {start_frame} --end_frame {end_frame}"
        args += f" --combination {str_combinations[i]}"

        command = f"{sys.executable} -m simian.render -- {args}"
        logger.info(f"Worker running: {command}")

        subprocess.run(["bash", "-c", command], check=True)



    api = HfApi(token=os.getenv("HF_TOKEN"))
    # Upload the directory using distributaur
    api.upload_folder(
        folder_path=output_dir,
        repo_id=os.getenv("HF_REPO_ID"),
        repo_type="dataset",
    )
        
    return "Task done"




# only run this is this file was started by celery or run directly
# check if celery is in sys.argv, it could be sys.argv[0] but might not be
    
if __name__ == "__main__" or any("celery" in arg for arg in sys.argv):
    from distributaur.distributaur import create_from_config

    distributaur = create_from_config()
    distributaur.register_function(run_job)

    celery = distributaur.app

