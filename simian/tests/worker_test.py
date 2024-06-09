import json
import sys
from unittest.mock import patch

from ..worker import run_job


@patch("..worker.subprocess.run")
def test_run_job(mock_subprocess_run):
    combination_index = 0
    combination = {"objects": []}
    width = 1920
    height = 1080
    output_dir = "test_output"
    hdri_path = "test_hdri"
    start_frame = 0
    end_frame = 10

    run_job(
        combination_index,
        combination,
        width,
        height,
        output_dir,
        hdri_path,
        start_frame,
        end_frame,
    )

    combination_str = json.dumps(combination)
    combination_str = '"' + combination_str.replace('"', '\\"') + '"'

    command = f"{sys.executable} -m simian.render -- --width {width} --height {height} --combination_index {combination_index}"
    command += f" --output_dir {output_dir}"
    command += f" --hdri_path {hdri_path}"
    command += f" --start_frame {start_frame} --end_frame {end_frame}"
    command += f" --combination {combination_str}"

    mock_subprocess_run.assert_called_once_with(["bash", "-c", command], check=False)


if __name__ == "__main__":
    # test_run_job()
    pass
