import json
import multiprocessing
import os
import platform
import subprocess
import sys
import argparse
from typing import Optional

# Append Simian to sys.path before importing from package
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))


def render_objects(
    processes: Optional[int] = None,
    render_timeout: int = 3000,
    width: int = 1920,
    height: int = 1080,
    start_index: int = 0,
    end_index: int = -1,
    start_frame: int = 1,
    end_frame: int = 65,
) -> None:
    """
    Automates the rendering of objects using Blender based on predefined combinations.

    This function orchestrates the rendering of multiple objects within a specified range
    from the combinations DataFrame. It allows for configuration of rendering dimensions,
    use of specific GPU devices, and selection of frames for animation sequences.

    Args:
        processes (Optional[int]): Number of processes to use for multiprocessing.
            Defaults to three times the number of CPU cores.
        render_timeout (int): Maximum time in seconds for a single rendering process.
        width (int): Width of the rendering in pixels.
        height (int): Height of the rendering in pixels.
        start_index (int): Starting index for rendering from the combinations DataFrame.
        end_index (int): Ending index for rendering from the combinations DataFrame.
        start_frame (int): Starting frame number for the animation.
        end_frame (int): Ending frame number for the animation.

    Raises:
        NotImplementedError: If the operating system is not supported.
        FileNotFoundError: If Blender is not found at the specified path.

    Returns:
        None
    """
    # Set the number of processes to three times the number of CPU cores if not specified.
    if processes is None:
        processes = multiprocessing.cpu_count() * 3

    scripts_dir = os.path.dirname(os.path.realpath(__file__))
    target_directory = os.path.join(scripts_dir, "../", "renders")
    hdri_path = os.path.join(scripts_dir, "../", "backgrounds")

    # make sure renders directory exists
    os.makedirs(target_directory, exist_ok=True)

    if end_index == -1:

        # get the length of combinations.json
        with open(os.path.join(scripts_dir, "../", "combinations.json"), "r") as file:
            data = json.load(file)
            combinations_data = data["combinations"]
            num_combinations = len(combinations_data)

        end_index = num_combinations

    # Loop over each combination index to set up and run the rendering process.
    for i in range(start_index, end_index):
        args = f"--width {width} --height {height} --combination_index {i} --start_frame {start_frame} --end_frame {end_frame} --output_dir {target_directory} --hdri_path {hdri_path}"

        # Construct and print the Blender command line.
        command = f"{sys.executable} simian/render.py -- {args}"

        print("This is the command: ", command)

        # Execute the rendering command with a timeout.
        subprocess.run(["bash", "-c", command], timeout=render_timeout, check=False)


def main():
    parser = argparse.ArgumentParser(
        description="Automate the rendering of objects using Blender."
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=None,
        help="Number of processes to use for multiprocessing. Defaults to three times the number of CPU cores.",
    )
    parser.add_argument(
        "--render_timeout",
        type=int,
        default=3000,
        help="Maximum time in seconds for a single rendering process. Defaults to 3000.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Width of the rendering in pixels. Defaults to 1920.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Height of the rendering in pixels. Defaults to 1080.",
    )
    parser.add_argument(
        "--start_index",
        type=int,
        default=0,
        help="Starting index for rendering from the combinations DataFrame. Defaults to 0.",
    )
    parser.add_argument(
        "--end_index",
        type=int,
        default=-1,
        help="Ending index for rendering from the combinations DataFrame. Defaults to -1.",
    )
    parser.add_argument(
        "--start_frame",
        type=int,
        default=1,
        help="Starting frame number for the animation. Defaults to 1.",
    )
    parser.add_argument(
        "--end_frame",
        type=int,
        default=65,
        help="Ending frame number for the animation. Defaults to 65.",
    )

    args = parser.parse_args()

    render_objects(
        processes=args.processes,
        render_timeout=args.render_timeout,
        width=args.width,
        height=args.height,
        start_index=args.start_index,
        end_index=args.end_index,
        start_frame=args.start_frame,
        end_frame=args.end_frame,
    )


if __name__ == "__main__":
    main()
