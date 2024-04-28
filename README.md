## 🖥️ Setup

1. Download Blender. If you're on Linux, set it up with this script:

```bash
bash install_blender_linux.sh
```

2. If you're on a headless Linux server, install Xorg and start it:

```bash
sudo apt-get install xserver-xorg -y && \
  sudo python3 start_x_server.py start
```

3. Install the Python dependencies. Note that Python >3.8 is required:

```bash
pip install -r requirements.txt && pip install -e .
```

## 📸 Usage

### 🐥 Minimal Example

After setup, we can start to render objects using the `batch.py` script:

```bash
python3 batch.py
```

After running this, you should see 10 zip files located in `./renders`:

Finally, we also have a `metadata.json` file, which contains metadata about the object and scene:

```json
{
  "animation_count": 0,
  "armature_count": 0,
  "edge_count": 2492,
  "file_identifier": "https://github.com/mattdeitke/objaverse-xl-test-files/blob/ead0bed6a76012452273bbe18d12e4d68a881956/example.abc",
  "file_size": 108916,
  "lamp_count": 1,
  "linked_files": [],
  "material_count": 0,
  "mesh_count": 3,
  "missing_textures": {
    "count": 0,
    "file_path_to_color": {},
    "files": []
  },
  "object_count": 8,
  "poly_count": 984,
  "random_color": null,
  "save_uid": "0fde27a0-99f0-5029-8e20-be9b8ecabb59",
  "scene_size": {
    "bbox_max": [
      4.999998569488525,
      6.0,
      1.0
    ],
    "bbox_min": [
      -4.999995231628418,
      -6.0,
      -1.0
    ]
  },
  "sha256": "879bc9d2d85e4f3866f0cfef41f5236f9fff5f973380461af9f69cdbed53a0da",
  "shape_key_count": 0,
  "vert_count": 2032
}
```

### 🎛 Configuration

Inside of `batch.py` there is a `render_objects` function that provides various parameters allowing for customization during the rendering process:

- `render_dir: str = "./renders"`: The directory where the objects will be rendered. Default is `"./renders"`.
- `download_dir: Optional[str] = None`: The directory where the objects will be downloaded. Thanks to fsspec, we support writing files to many file systems. To use it, simply use the prefix of your filesystem before the path. For example hdfs://, s3://, http://, gcs://, or ssh://. Some of these file systems require installing an additional package (for example s3fs for s3, gcsfs for gcs, fsspec/sshfs for ssh). Start [here](https://github.com/rom1504/img2dataset#file-system-support) for more details on fsspec. If None, the objects will be deleted after they are rendered.
- `processes: Optional[int] = None`: The number of processes to utilize for downloading the objects. If left as `None` (default), it will default to `multiprocessing.cpu_count() * 3`.
- `save_repo_format: Optional[Literal["zip", "tar", "tar.gz", "files"]] = None`: If specified, the GitHub repository will be deleted post rendering each object from it. Available options are `"zip"`, `"tar"`, and `"tar.gz"`. If `None` (default), no action is taken.
- `render_timeout: int = 300`: Maximum number of seconds to await completion of the rendering job. Default is `300` seconds.
- `gpu_devices: Optional[Union[int, List[int]]] = None`: Specifies GPU device(s) for rendering. If an `int`, the GPU device is randomly chosen from `0` to `gpu_devices - 1`. If a `List[int]`, a GPU device is randomly chosen from the list. If `0`, the CPU is used. If `None` (default), all available GPUs are utilized.

To tweak the objects that you want to render, go into `batch.py` and update the `get_example_objects` function.

#### Example

To render objects using a custom configuration:

```bash
python3 batch.py --render_dir s3://bucket/render/directory
```
