import json
import os
import sys
import argparse

from celery import chord

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

from simian.utils import check_imports
from simian.worker import render_object, notify_completion

check_imports()

def render_objects(
    start_index,
    end_index,
    start_frame=0,
    end_frame=65,
    width=1920,
    height=1080,
    output_dir="./renders",
    hdri_path="./backgrounds",
):
    combinations = []
    # read combinations.json
    with open("combinations.json", "r") as file:
        combinations = json.load(file)
        combinations = combinations["combinations"]

    # make sure end_index is less than the number of combinations
    end_index = min(end_index, len(combinations))

    print(f"Rendering objects from {start_index} to {end_index}")

    tasks = []
    for i in range(start_index, end_index):
        print(f"Queueing {i}")
        combination = combinations[i]
        tasks.append(
            render_object.s(
                combination_index=i,
                combination=combination,
                width=width,
                height=height,
                output_dir=output_dir,
                hdri_path=hdri_path,
                start_frame=start_frame,
                end_frame=end_frame,
            )
        )

    job = chord(tasks)(notify_completion.s())
    result = job.get()
    print("All tasks have been completed!")


def main():
    parser = argparse.ArgumentParser(
        description="Automate the rendering of objects using Celery."
    )
    parser.add_argument(
        "--start_index",
        type=int,
        default=0,
        help="Starting index for rendering from the combinations list.",
    )
    parser.add_argument(
        "--end_index",
        type=int,
        default=100,
        help="Ending index for rendering from the combinations list.",
    )
    parser.add_argument(
        "--start_frame",
        type=int,
        default=0,
        help="Starting frame number for the animation. Defaults to 0.",
    )
    parser.add_argument(
        "--end_frame",
        type=int,
        default=65,
        help="Ending frame number for the animation. Defaults to 65.",
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
        "--output_dir",
        type=str,
        default="./renders",
        help="Directory to save rendered outputs. Defaults to './renders'.",
    )
    parser.add_argument(
        "--hdri_path",
        type=str,
        default="./backgrounds",
        help="Directory containing HDRI files for rendering. Defaults to './backgrounds'.",
    )

    args = parser.parse_args()

    render_objects(
        start_index=args.start_index,
        end_index=args.end_index,
        start_frame=args.start_frame,
        end_frame=args.end_frame,
        width=args.width,
        height=args.height,
        output_dir=args.output_dir,
        hdri_path=args.hdri_path,
    )


if __name__ == "__main__":
    main()
