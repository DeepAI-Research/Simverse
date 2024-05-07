import platform
import subprocess
import sys
import os
import ssl

from celery import Celery
import pandas as pd

ssl._create_default_https_context = ssl._create_unverified_context


def check_imports() -> None:
    """
    Checks and installs required Python packages specified in the requirements.txt file.
    
    Args:
        None
    
    Returns:
        None
    """
    with open("requirements.txt", "r") as f:
        requirements = f.readlines()
    for requirement in requirements:
        try:
            __import__(requirement)
        except ImportError:
            print(f"Installing {requirement}")
            subprocess.run(["bash", "-c", f"{sys.executable} -m pip install {requirement}"])

check_imports()

# Get the directory of the currently executing script
current_dir = os.path.dirname(os.path.abspath(__file__))

# if the directory is simian, remove that
if current_dir.endswith("simian"):
    current_dir = os.path.dirname(current_dir)  

# Append the simian directory to sys.path
simian_path = os.path.join(current_dir)
sys.path.append(simian_path)

# if we are on macOS, then application_path is /Applications/Blender.app/Contents/MacOS/Blender
if platform.system() == "Darwin":
    application_path = "/Applications/Blender.app/Contents/MacOS/Blender"
else:
    application_path = "./blender/blender"


def get_combination_objects() -> pd.DataFrame:
    """
    Returns a DataFrame of example objects to use for debugging.
    
    Args:
    - None
    
    Returns:
    - pd.DataFrame: DataFrame of example objects.
    """
    combinations = pd.read_json("combinations.json", orient="records")
    return combinations


redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
app = Celery('tasks', broker=redis_url)


@app.task(name='render_object', acks_late=True, reject_on_worker_lost=True)
def render_object(
    combination_index: int,
    width: int,
    height: int,
    output_dir: str,
    background_path: str
) -> None:
    """
    Renders a 3D object based on the provided combination index and settings.

    Args:
    - combination_index (int): The index of the camera combination to use.
    - width (int): The width of the rendered output.
    - height (int): The height of the rendered output.
    - output_dir (str): The directory where the rendered video will be saved.
    - background_path (str): The path to the background HDRs.
    
    Returns:
    - None
    """
    args = f"--width {width} --height {height} --combination_index {combination_index}"
    args += f" --output_dir {output_dir}"
    args += f" --background_path {background_path}"

    command = f"{application_path} --background --python simian/render.py -- {args}"
    subprocess.run(["bash", "-c", command], timeout=10000, check=False)