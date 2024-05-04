import multiprocessing
import os
import platform
import subprocess
from typing import List, Literal, Optional, Union

import fire
import GPUtil
import pandas as pd
from loguru import logger

# if we are on macOS, then application_path is /Applications/Blender.app/Contents/MacOS/Blender
if platform.system() == "Darwin":
    application_path = "/Applications/Blender.app/Contents/MacOS/Blender"
else:
    application_path = "./blender/blender"

def get_combination_objects() -> pd.DataFrame:
    """Returns a DataFrame of example objects to use for debugging."""
    combinations = pd.read_json("combinations.json", orient="records")
    return combinations


def render_objects(
    download_dir: Optional[str] = None,
    processes: Optional[int] = None,
    save_repo_format: Optional[Literal["zip", "tar", "tar.gz", "files"]] = None,
    render_timeout: int = 300,
    gpu_devices: Optional[Union[int, List[int]]] = None,
    width=1920,
    height=1080,
    start_index: int = 0,
    end_index: int = 9,
    start_frame: int = 1,
    end_frame: int = 25,
) -> None:
    """Renders objects in the Objaverse dataset with Blender

    Args:
        download_dir (Optional[str], optional): Directory where the objects will be
            downloaded. If None, the objects will not be downloaded. Defaults to None.
        processes (Optional[int], optional): Number of processes to use for downloading
            the objects. If None, defaults to multiprocessing.cpu_count() * 3. Defaults
            to None.
        save_repo_format (Optional[Literal["zip", "tar", "tar.gz", "files"]], optional):
            If not None, the GitHub repo will be deleted after rendering each object
            from it.
        render_timeout (int, optional): Number of seconds to wait for the rendering job
            to complete. Defaults to 300.
        gpu_devices (Optional[Union[int, List[int]]], optional): GPU device(s) to use
            for rendering. If an int, the GPU device will be randomly selected from 0 to
            gpu_devices - 1. If a list, the GPU device will be randomly selected from
            the list. If 0, the CPU will be used for rendering. If None, all available
            GPUs will be used. Defaults to None.

    Returns:
        None
    """
    if platform.system() not in ["Linux", "Darwin"]:
        raise NotImplementedError(
            f"Platform {platform.system()} is not supported. Use Linux or MacOS."
        )
    if download_dir is None and save_repo_format is not None:
        raise ValueError(
            f"If {save_repo_format=} is not None, {download_dir=} must be specified."
        )
    if download_dir is not None and save_repo_format is None:
        logger.warning(
            f"GitHub repos will not save. While {download_dir=} is specified, {save_repo_format=} None."
        )

    # get the gpu devices to use
    parsed_gpu_devices: Union[int, List[int]] = 0
    if gpu_devices is None:
        parsed_gpu_devices = len(GPUtil.getGPUs())
    logger.info(f"Using {parsed_gpu_devices} GPU devices for rendering.")

    if processes is None:
        processes = multiprocessing.cpu_count() * 3

    for i in range(start_index, end_index):        
        args = f"--width {width} --height {height} --combination_index {i} --start_frame {start_frame} --end_frame {end_frame}"

        # find the "renders" directory in same folder as this script
        scripts_dir = os.path.dirname(os.path.realpath(__file__))

        # get the target directory for the rendering job
        target_directory = os.path.join(scripts_dir, "../", "renders")
        os.makedirs(target_directory, exist_ok=True)
        args += f" --output_dir {target_directory}"
        
        background_path = os.path.join(scripts_dir, "../", "backgrounds")
        args += f" --background_path {background_path}"

        # check if application_path exists
        if not os.path.exists(application_path):
            raise FileNotFoundError(f"Blender not found at {application_path}.")

        # if we are on linux, then application_path is /usr/bin/blender
        # https://builder.blender.org/download/daily/archive/blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release.tar.xz
        # get the command to run
        command = f"{application_path} --background --python simian/render.py -- {args}"
        print(command)

        # render the object (put in dev null)
        subprocess.run(
            ["bash", "-c", command],
            timeout=render_timeout,
            check=False
            # pipe the output to the console
        )
        

if __name__ == "__main__":
    # 
    fire.Fire(render_objects)
