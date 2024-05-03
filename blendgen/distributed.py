import os
import platform
import subprocess
import sys

import fire
import pandas as pd
from celery import Celery

def check_imports():
    # what was the CLI command used to run this script?
    application_path = sys.argv[0]
    print("Application path")
    print(application_path)
    # read from requirements.txt
    with open("requirements.txt", "r") as f:
        requirements = f.readlines()
    for requirement in requirements:
        requirement = requirement.split(">=")[0].split("==")[0].split("@")[0].strip()
        try:
            __import__(requirement)
        except ImportError:
            print(f"Installing {requirement}")
            subprocess.run(["bash", "-c", f"{sys.executable} -m pip install {requirement}"])

check_imports()

# Get the directory of the currently executing script
current_dir = os.path.dirname(os.path.abspath(__file__))

# if the directory is blendgen, remove that
if current_dir.endswith("blendgen"):
    current_dir = os.path.dirname(current_dir)  

# Append the blendgen directory to sys.path
blendgen_path = os.path.join(current_dir)
sys.path.append(blendgen_path)

# if we are on macOS, then application_path is /Applications/Blender.app/Contents/MacOS/Blender
if platform.system() == "Darwin":
    application_path = "/Applications/Blender.app/Contents/MacOS/Blender"
else:
    application_path = "./blender/blender"

def get_combination_objects() -> pd.DataFrame:
    """Returns a DataFrame of example objects to use for debugging."""
    combinations = pd.read_json("combinations.json", orient="records")
    return combinations

from blendgen.worker import render_object

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
app = Celery('tasks', broker=redis_url)

@app.task(name='render_object', acks_late=True, reject_on_worker_lost=True)
def render_object(combination_index=0, width=1920, height=1080, output_dir="./renders", background_path="./backgrounds"):
    args = f"--width {width} --height {height} --combination_index {combination_index}"
    args += f" --output_dir {output_dir}"
    args += f" --background_path {background_path}"

    command = f"{application_path} --background --python blendgen/main.py -- {args}"
    subprocess.run(["bash", "-c", command], timeout=10000, check=False)

def render_objects(start_index, end_index, width, height, output_dir, background_path):
    print(f"Rendering objects from {start_index} to {end_index}")
    for i in range(start_index, end_index):
        print(f"Rendering object {i}")
        render_object.delay(i, width, height, output_dir, background_path)

if __name__ == "__main__":
    fire.Fire(render_objects)