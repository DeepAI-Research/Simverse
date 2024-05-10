import os
import subprocess
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

from simian.utils import get_blender_path
from distributed.worker import render_object
from simian.utils import check_imports

check_imports()


redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
app = Celery("tasks", broker=redis_url)


@app.task(name="render_object", acks_late=True, reject_on_worker_lost=True)
def render_object(
    combination_index=0,
    width=1920,
    height=1080,
    output_dir="./renders",
    hdri_path="./backgrounds",
):
    args = f"--width {width} --height {height} --combination_index {combination_index}"
    args += f" --output_dir {output_dir}"
    args += f" --hdri_path {hdri_path}"

    command = f"{get_blender_path()} --background --python simian/render.py -- {args}"
    subprocess.run(["bash", "-c", command], timeout=10000, check=False)


def render_objects(start_index, end_index, width, height, output_dir, hdri_path):
    print(f"Rendering objects from {start_index} to {end_index}")
    for i in range(start_index, end_index):
        print(f"Rendering object {i}")
        render_object.delay(i, width, height, output_dir, hdri_path)


if __name__ == "__main__":
    fire.Fire(render_objects)
