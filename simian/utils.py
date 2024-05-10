import importlib
import os
import platform
import re
import subprocess
import sys
import pandas as pd


def get_combination_objects(file="combinations.json") -> pd.DataFrame:
    """
    Fetches a DataFrame of example objects from a JSON file.

    This function is used primarily for debugging purposes, where combinations
    of objects are read from a JSON file and returned as a pandas DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing example object combinations.
    """
    combinations = pd.read_json("combinations.json", orient="records")
    return combinations


def get_blender_path():
    # if we are on macOS, then application_path is /Applications/Blender.app/Contents/MacOS/Blender
    if platform.system() == "Darwin":
        application_path = "/Applications/Blender.app/Contents/MacOS/Blender"
    else:
        application_path = "./blender/blender"
    if not os.path.exists(application_path):
        raise FileNotFoundError(f"Blender not found at {application_path}.")
    return application_path


def check_imports() -> None:
    """
    Checks and installs required Python packages specified in the requirements.txt file.

    Args:
        None

    Returns:
        None
    """
    with open("requirements.txt", "r") as f:
        requirements = [
            line.strip() for line in f
        ]  # Strip newline characters and spaces

    package_name_pattern = re.compile(
        r"^\s*([\w\d\.\-_]+)"
    )  # Regex to capture the package name

    for requirement in requirements:
        if requirement:  # Ensure the requirement is not an empty string
            match = package_name_pattern.search(requirement)
            if match:
                package_name = match.group(1)
                try:
                    importlib.import_module(
                        package_name
                    )  # Import using just the package name
                except ImportError:
                    print(f"Installing {requirement}")
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", requirement],
                        check=True,  # Ensures any error in installation raises an exception
                    )
