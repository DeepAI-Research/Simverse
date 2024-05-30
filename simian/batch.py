import json
import multiprocessing
import os
import subprocess
import sys
import argparse
from typing import Optional

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
    if processes is None:
        processes = multiprocessing.cpu_count() * 3

    scripts_dir = os.path.dirname(os.path.realpath(__file__))
    target_directory = os.path.join(scripts_dir, "../", "renders")
    hdri_path = os.path.join(scripts_dir, "../", "backgrounds")

    os.makedirs(target_directory, exist_ok=True)

    if end_index == -1:
        with open(os.path.join(scripts_dir, "../", "combinations.json"), "r") as file:
            data = json.load(file)
            combinations_data = data["combinations"]
            num_combinations = len(combinations_data)
        end_index = num_combinations

    for i in range(start_index, end_index):
        args = [
            sys.executable, 
            os.path.join(scripts_dir, "render.py"),
            "--width", str(width),
            "--height", str(height),
            "--combination_index", str(i),
            "--start_frame", str(start_frame),
            "--end_frame", str(end_frame),
            "--output_dir", target_directory,
            "--hdri_path", hdri_path,
            "--combination_file", "combinations.json"  # Add this line
        ]

        print("This is the command: ", " ".join(args))
        subprocess.run(args, timeout=render_timeout, check=False)

def main():
    parser = argparse.ArgumentParser(description="Automate the rendering of objects using Blender.")
    parser.add_argument("--processes", type=int, default=None, help="Number of processes to use for multiprocessing.")
    parser.add_argument("--render_timeout", type=int, default=3000, help="Maximum time in seconds for a single rendering process.")
    parser.add_argument("--width", type=int, default=1920, help="Width of the rendering in pixels.")
    parser.add_argument("--height", type=int, default=1080, help="Height of the rendering in pixels.")
    parser.add_argument("--start_index", type=int, default=0, help="Starting index for rendering from the combinations DataFrame.")
    parser.add_argument("--end_index", type=int, default=-1, help="Ending index for rendering from the combinations DataFrame.")
    parser.add_argument("--start_frame", type=int, default=1, help="Starting frame number for the animation.")
    parser.add_argument("--end_frame", type=int, default=65, help="Ending frame number for the animation.")
    
    args = parser.parse_args()
    render_objects(
        processes=args.processes,
        render_timeout=args.render_timeout,
        width=args.width,
        height=args.height,
        start_index=args.start_index,
        end_index=args.end_index,
        start_frame=args.start_frame,
        end_frame=args.end_frame
    )

if __name__ == "__main__":
    main()
