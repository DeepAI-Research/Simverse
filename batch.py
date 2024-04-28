import glob
import json
import multiprocessing
import os
import platform
import random
import subprocess
import tempfile
import time
import zipfile
from functools import partial
from typing import Any, Dict, List, Literal, Optional, Union

import fire
import fsspec
import GPUtil
import pandas as pd
from loguru import logger

import objaverse.xl as oxl
from objaverse.utils import get_uid_from_str


def log_processed_object(csv_filename: str, *args) -> None:
    """Log when an object is done being used.

    Args:
        csv_filename (str): Name of the CSV file to save the logs to.
        *args: Arguments to save to the CSV file.

    Returns:
        None
    """
    args = ",".join([str(arg) for arg in args])
    # log that this object was rendered successfully
    # saving locally to avoid excessive writes to the cloud
    dirname = os.path.expanduser(f"~/.objaverse/logs/")
    os.makedirs(dirname, exist_ok=True)
    with open(os.path.join(dirname, csv_filename), "a", encoding="utf-8") as f:
        f.write(f"{time.time()},{args}\n")


def zipdir(path: str, ziph: zipfile.ZipFile) -> None:
    """Zip up a directory with an arcname structure.

    Args:
        path (str): Path to the directory to zip.
        ziph (zipfile.ZipFile): ZipFile handler object to write to.

    Returns:
        None
    """
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            # this ensures the structure inside the zip starts at folder/
            arcname = os.path.join(os.path.basename(root), file)
            ziph.write(os.path.join(root, file), arcname=arcname)


def handle_found_object(
    local_path: str,
    file_identifier: str,
    sha256: str,
    metadata: Dict[str, Any],
    render_dir: str,
    gpu_devices: Union[int, List[int]],
    render_timeout: int,
    successful_log_file: Optional[str] = "handle-found-object-successful.csv",
    failed_log_file: Optional[str] = "handle-found-object-failed.csv",
    width: int = 1920,
    height: int = 1080
) -> bool:
    """Called when an object is successfully found and downloaded.

    Here, the object has the same sha256 as the one that was downloaded with
    Objaverse-XL. If None, the object will be downloaded, but nothing will be done with
    it.

    Args:
        local_path (str): Local path to the downloaded 3D object.
        file_identifier (str): File identifier of the 3D object.
        sha256 (str): SHA256 of the contents of the 3D object.
        render_dir (str): Directory where the objects will be rendered.
        gpu_devices (Union[int, List[int]]): GPU device(s) to use for rendering. If
            an int, the GPU device will be randomly selected from 0 to gpu_devices - 1.
            If a list, the GPU device will be randomly selected from the list.
            If 0, the CPU will be used for rendering.
        render_timeout (int): Number of seconds to wait for the rendering job to
            complete.
        successful_log_file (str): Name of the log file to save successful renders to.
        failed_log_file (str): Name of the log file to save failed renders to.

    Returns: True if the object was rendered successfully, False otherwise.
    """
    save_uid = get_uid_from_str(file_identifier)
    args = f"--object_path '{local_path}' --width {width} --height {height}"

    # get the GPU to use for rendering
    using_gpu: bool = True
    gpu_i = 0
    if isinstance(gpu_devices, int) and gpu_devices > 0:
        num_gpus = gpu_devices
        gpu_i = random.randint(0, num_gpus - 1)
    elif isinstance(gpu_devices, list):
        gpu_i = random.choice(gpu_devices)
    elif isinstance(gpu_devices, int) and gpu_devices == 0:
        using_gpu = False
    else:
        raise ValueError(
            f"gpu_devices must be an int > 0, 0, or a list of ints. Got {gpu_devices}."
        )

    # find the "renders" directory in same folder as this script
    scripts_dir = os.path.dirname(os.path.realpath(__file__))

    # get the target directory for the rendering job
    target_directory = os.path.join(scripts_dir, "renders")
    os.makedirs(target_directory, exist_ok=True)
    args += f" --output_dir {target_directory}"

    # if we are on macOS, then application_path is /Applications/Blender.app/Contents/MacOS/Blender
    if platform.system() == "Darwin":
        application_path = "/Applications/Blender.app/Contents/MacOS/Blender"
    else:
        application_path = "./blender/blender"

    # check if application_path exists
    if not os.path.exists(application_path):
        raise FileNotFoundError(f"Blender not found at {application_path}.")

    # if we are on linux, then application_path is /usr/bin/blender
    # https://builder.blender.org/download/daily/archive/blender-4.1.1-stable+v41.e1743a0317bc-linux.x86_64-release.tar.xz
    # get the command to run
    command = f"{application_path} --background --python blendgen/main.py -- {args}"
    print(command)
    if using_gpu:
        command = f"export DISPLAY=:0.{gpu_i} && {command}"

    # render the object (put in dev null)
    subprocess.run(
        ["bash", "-c", command],
        timeout=render_timeout,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # check that the renders were saved successfully
    video_files = glob.glob(os.path.join(target_directory, "*.mp4"))
    if (
        (len(video_files) != 1)
    ):
        logger.error(
            f"Found object {file_identifier} was not rendered successfully!"
        )
        if failed_log_file is not None:
            log_processed_object(
                failed_log_file,
                file_identifier,
                sha256,
            )
        return False

    # log that this object was rendered successfully
    if successful_log_file is not None:
        log_processed_object(successful_log_file, file_identifier, sha256)

    return True


def handle_new_object(
    local_path: str,
    metadata: Dict[str, Any],
    file_identifier: str,
    sha256: str,
    log_file: str = "handle-new-object.csv",
) -> None:
    """Called when a new object is found.

    Here, the object is not used in Objaverse-XL, but is still downloaded with the
    repository. The object may have not been used because it does not successfully
    import into Blender. If None, the object will be downloaded, but nothing will be
    done with it.

    Args:
        local_path (str): Local path to the downloaded 3D object.
        file_identifier (str): The file identifier of the new 3D object.
        sha256 (str): SHA256 of the contents of the 3D object.
        log_file (str): Name of the log file to save the handle_new_object logs to.

    Returns:
        None
    """
    # log the new object
    log_processed_object(log_file, file_identifier, sha256)


def handle_modified_object(
    local_path: str,
    metadata: Dict[str, Any],
    file_identifier: str,
    new_sha256: str,
    old_sha256: str,
    render_dir: str,
    gpu_devices: Union[int, List[int]],
    render_timeout: int,
    width: int = 1920,
    height: int = 1080
) -> None:
    """Called when a modified object is found and downloaded.

    Here, the object is successfully downloaded, but it has a different sha256 than the
    one that was downloaded with Objaverse-XL. This is not expected to happen very
    often, because the same commit hash is used for each repo. If None, the object will
    be downloaded, but nothing will be done with it.

    Args:
        local_path (str): Local path to the downloaded 3D object.
        file_identifier (str): File identifier of the 3D object.
        new_sha256 (str): SHA256 of the contents of the newly downloaded 3D object.
        old_sha256 (str): Expected SHA256 of the contents of the 3D object as it was
            when it was downloaded with Objaverse-XL.
        render_dir (str): Directory where the objects will be rendered.
        gpu_devices (Union[int, List[int]]): GPU device(s) to use for rendering. If
            an int, the GPU device will be randomly selected from 0 to gpu_devices - 1.
            If a list, the GPU device will be randomly selected from the list.
            If 0, the CPU will be used for rendering.
        render_timeout (int): Number of seconds to wait for the rendering job to
            complete.

    Returns:
        None
    """
    success = handle_found_object(
        local_path=local_path,
        file_identifier=file_identifier,
        metadata=metadata,
        sha256=new_sha256,
        render_dir=render_dir,
        gpu_devices=gpu_devices,
        render_timeout=render_timeout,
        successful_log_file=None,
        failed_log_file=None,
        width=width,
        height=height
    )

    if success:
        log_processed_object(
            "handle-modified-object-successful.csv",
            file_identifier,
            old_sha256,
            new_sha256,
        )
    else:
        log_processed_object(
            "handle-modified-object-failed.csv",
            file_identifier,
            old_sha256,
            new_sha256,
        )


def handle_missing_object(
    file_identifier: str,
    sha256: str,
    log_file: str = "handle-missing-object.csv",
) -> None:
    """Called when an object that is in Objaverse-XL is not found.

    Here, it is likely that the repository was deleted or renamed. If None, nothing
    will be done with the missing object.

    Args:
        file_identifier (str): File identifier of the 3D object.
        sha256 (str): SHA256 of the contents of the original 3D object.
        log_file (str): Name of the log file to save missing renders to.

    Returns:
        None
    """
    # log the missing object
    log_processed_object(log_file, file_identifier, sha256)


def get_example_objects() -> pd.DataFrame:
    """Returns a DataFrame of example objects to use for debugging."""
    return pd.read_json("example-objects.json", orient="records")


def render_objects(
    render_dir: str = "./",
    download_dir: Optional[str] = None,
    processes: Optional[int] = None,
    save_repo_format: Optional[Literal["zip", "tar", "tar.gz", "files"]] = None,
    render_timeout: int = 300,
    gpu_devices: Optional[Union[int, List[int]]] = None,
    width=1920,
    height=1080,
) -> None:
    """Renders objects in the Objaverse-XL dataset with Blender

    Args:
        render_dir (str, optional): Directory where the objects will be rendered.
        download_dir (Optional[str], optional): Directory where the objects will be
            downloaded. If None, the objects will not be downloaded. Defaults to None.
        processes (Optional[int], optional): Number of processes to use for downloading
            the objects. If None, defaults to multiprocessing.cpu_count() * 3. Defaults
            to None.
        save_repo_format (Optional[Literal["zip", "tar", "tar.gz", "files"]], optional):
            If not None, the GitHub repo will be deleted after rendering each object
            from it.
        render_timeout (int, optional): Number of seconds to wait for the rendering job
            to complete. Defaults to 300.
        gpu_devices (Optional[Union[int, List[int]]], optional): GPU device(s) to use
            for rendering. If an int, the GPU device will be randomly selected from 0 to
            gpu_devices - 1. If a list, the GPU device will be randomly selected from
            the list. If 0, the CPU will be used for rendering. If None, all available
            GPUs will be used. Defaults to None.

    Returns:
        None
    """
    if platform.system() not in ["Linux", "Darwin"]:
        raise NotImplementedError(
            f"Platform {platform.system()} is not supported. Use Linux or MacOS."
        )
    if download_dir is None and save_repo_format is not None:
        raise ValueError(
            f"If {save_repo_format=} is not None, {download_dir=} must be specified."
        )
    if download_dir is not None and save_repo_format is None:
        logger.warning(
            f"GitHub repos will not save. While {download_dir=} is specified, {save_repo_format=} None."
        )

    # get the gpu devices to use
    parsed_gpu_devices: Union[int, List[int]] = 0
    if gpu_devices is None:
        parsed_gpu_devices = len(GPUtil.getGPUs())
    logger.info(f"Using {parsed_gpu_devices} GPU devices for rendering.")

    if processes is None:
        processes = multiprocessing.cpu_count() * 3

    # get the objects to render
    objects = get_example_objects()
    objects.iloc[0]["fileIdentifier"]
    objects = objects.copy()
    logger.info(f"Provided {len(objects)} objects to render.")

    # get the already rendered objects
    fs, path = fsspec.core.url_to_fs(render_dir)
    try:
        zip_files = fs.glob(os.path.join(path, "renders", "*.zip"), refresh=True)
    except TypeError:
        # s3fs may not support refresh depending on the version
        zip_files = fs.glob(os.path.join(path, "renders", "*.zip"))

    saved_ids = set(zip_file.split("/")[-1].split(".")[0] for zip_file in zip_files)
    logger.info(f"Found {len(saved_ids)} objects already rendered.")

    # filter out the already rendered objects
    objects["saveUid"] = objects["fileIdentifier"].apply(get_uid_from_str)
    objects = objects[~objects["saveUid"].isin(saved_ids)]
    objects = objects.reset_index(drop=True)
    logger.info(f"Rendering {len(objects)} new objects.")

    # shuffle the objects
    objects = objects.sample(frac=1).reset_index(drop=True)

    oxl.get_annotations(download_dir='./')

    oxl.download_objects(
        objects=objects,
        processes=processes,
        save_repo_format=save_repo_format,
        download_dir=download_dir,
        handle_found_object=partial(
            handle_found_object,
            render_dir=render_dir,
            gpu_devices=parsed_gpu_devices,
            render_timeout=render_timeout,
            width=width,
            height=height,
        ),
        handle_new_object=handle_new_object,
        handle_modified_object=partial(
            handle_modified_object,
            render_dir=render_dir,
            gpu_devices=parsed_gpu_devices,
            render_timeout=render_timeout,
            width=width,
            height=height,
        ),
        handle_missing_object=handle_missing_object,
    )


if __name__ == "__main__":
    fire.Fire(render_objects)
