import json
import os
import sys
import argparse

from celery import Celery

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

from simian.utils import get_combination_objects, get_redis_values, check_imports
from simian.worker import render_object

check_imports()

app = Celery("tasks", broker=get_redis_values())

def render_objects(start_index, end_index, start_frame=0, end_frame=65, width=1920, height=1080, output_dir="./renders", hdri_path="./backgrounds"):
    print(f"Rendering objects from {start_index} to {end_index}")
    
    # read combinations.json
    with open('combinations.json', 'r') as file:
        combinations = json.load(file)
        
    combinations = combinations["combinations"]
    
    # make sure end_index is less than the number of combinations
    end_index = min(end_index, len(combinations))
    
    for i in range(start_index, end_index):
        print(f"Queueing {i}")
        combination = combinations[i]
        render_object.delay(i, combination, width, height, start_frame, end_frame, output_dir, hdri_path)

def main():
    parser = argparse.ArgumentParser(description="Automate the rendering of objects using Celery.")
    parser.add_argument("--start_index", type=int, help="Starting index for rendering from the combinations list.")
    parser.add_argument("--end_index", type=int, help="Ending index for rendering from the combinations list.")
    parser.add_argument("--start_frame", type=int, default=0, help="Starting frame number for the animation. Defaults to 0.")
    parser.add_argument("--end_frame", type=int, default=65, help="Ending frame number for the animation. Defaults to 65.")
    parser.add_argument("--width", type=int, default=1920, help="Width of the rendering in pixels. Defaults to 1920.")
    parser.add_argument("--height", type=int, default=1080, help="Height of the rendering in pixels. Defaults to 1080.")
    parser.add_argument("--output_dir", type=str, default="./renders", help="Directory to save rendered outputs. Defaults to './renders'.")
    parser.add_argument("--hdri_path", type=str, default="./backgrounds", help="Directory containing HDRI files for rendering. Defaults to './backgrounds'.")

    args = parser.parse_args()

    render_objects(
        start_index=args.start_index,
        end_index=args.end_index,
        start_frame=args.start_frame,
        end_frame=args.end_frame,
        width=args.width,
        height=args.height,
        output_dir=args.output_dir,
        hdri_path=args.hdri_path
    )

if __name__ == "__main__":
    main()
