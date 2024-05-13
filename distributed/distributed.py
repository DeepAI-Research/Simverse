import os
import sys

import fire
from celery import Celery

# Get the directory of the currently executing script
current_dir = os.path.dirname(os.path.abspath(__file__))

# if the directory is simian, remove that
if current_dir.endswith("simian"):
    current_dir = os.path.dirname(current_dir)

# Append the simian directory to sys.path
simian_path = os.path.join(current_dir)
sys.path.append(simian_path)

from distributed.utils import get_redis_values
from distributed.worker import render_object
from simian.utils import check_imports

check_imports()

app = Celery("tasks", broker=get_redis_values())

def render_objects(start_index, end_index, width, height, output_dir, hdri_path):
    print(f"Rendering objects from {start_index} to {end_index}")
    for i in range(start_index, end_index):
        print(f"Rendering object {i}")
        render_object.delay(i, width, height, output_dir, hdri_path)


if __name__ == "__main__":
    fire.Fire(render_objects)
