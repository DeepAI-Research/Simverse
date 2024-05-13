import json
import os
import sys

import fire
from celery import Celery

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

from simian.utils import get_combination_objects, get_redis_values, check_imports
from simian.worker import render_object

check_imports()

app = Celery("tasks", broker=get_redis_values())

def render_objects(start_index, end_index, frame_start=0, frame_end=65, width=1920, height=1080, output_dir="./renders", hdri_path="./backgrounds"):
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
        render_object.delay(i, combination, width, height, output_dir, hdri_path)

if __name__ == "__main__":
    fire.Fire(render_objects)
