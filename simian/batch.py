import multiprocessing
import os
import platform
import subprocess
import sys
from typing import Literal, Optional
import fire

# Append Simian to sys.path before importing from package
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

from simian.utils import get_blender_path


def render_objects(
    download_dir: Optional[str] = None,
    processes: Optional[int] = None,
    save_repo_format: Optional[Literal["zip", "tar", "tar.gz", "files"]] = None,
    render_timeout: int = 3000,
    width: int = 1920,
    height: int = 1080,
    start_index: int = 0,
    end_index: int = 9,
    start_frame: int = 1,
    end_frame: int = 25,
) -> None:
    """
    Automates the rendering of objects using Blender based on predefined combinations.

    This function orchestrates the rendering of multiple objects within a specified range
    from the combinations DataFrame. It allows for configuration of rendering dimensions,
    use of specific GPU devices, and selection of frames for animation sequences.

    Args:
        - download_dir (Optional[str]): Directory to download the objects to.
            If None, objects are not downloaded. Defaults to None.
        - processes (Optional[int]): Number of processes to use for multiprocessing.
            Defaults to three times the number of CPU cores.
        - save_repo_format (Optional[Literal["zip", "tar", "tar.gz", "files"]]):
            Format to save repositories after rendering. If None, no saving is performed.
        - render_timeout (int): Maximum time in seconds for a single rendering process.
        - width (int): Width of the rendering in pixels.
        - height (int): Height of the rendering in pixels.
        - start_index (int): Starting index for rendering from the combinations DataFrame.
        - end_index (int): Ending index for rendering from the combinations DataFrame.
        - start_frame (int): Starting frame number for the animation.
        - end_frame (int): Ending frame number for the animation.

    Raises:
        - NotImplementedError: If the operating system is not supported.
        - FileNotFoundError: If Blender is not found at the specified path.

    Returns:
        None
    """

    # Check if the operating system is supported for rendering.
    if platform.system() not in ["Linux", "Darwin"]:
        raise NotImplementedError(
            f"Rendering on {platform.system()} is not supported. Use Linux or macOS."
        )

    # Ensure download directory is specified if a save format is set.
    if download_dir is None and save_repo_format is not None:
        raise ValueError(
            f"Download directory must be specified if save_repo_format is set."
        )

    # Set the number of processes to three times the number of CPU cores if not specified.
    if processes is None:
        processes = multiprocessing.cpu_count() * 3

    # Loop over each combination index to set up and run the rendering process.
    for i in range(start_index, end_index):
        args = f"--width {width} --height {height} --combination_index {i} --start_frame {start_frame} --end_frame {end_frame}"
        scripts_dir = os.path.dirname(os.path.realpath(__file__))
        target_directory = os.path.join(scripts_dir, "../", "renders")
        os.makedirs(target_directory, exist_ok=True)
        args += f" --output_dir {target_directory}"
        hdri_path = os.path.join(scripts_dir, "../", "backgrounds")
        args += f" --hdri_path {hdri_path}"
        
        application_path = get_blender_path()
        
        # Construct and print the Blender command line.
        command = f"{application_path} --background --python simian/render.py -- {args}"
        print(command)

        # Execute the rendering command with a timeout.
        subprocess.run(["bash", "-c", command], timeout=render_timeout, check=False)


if __name__ == "__main__":
    fire.Fire(render_objects)
