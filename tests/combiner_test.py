import os
import sys
import json
from unittest.mock import patch, mock_open

current_dir = os.path.dirname(os.path.abspath(__file__))
# Append the combiner directory to sys.path
combiner_path = os.path.join(current_dir, "../")
sys.path.append(combiner_path)

import random

# Assuming the existence of a file combiner.py with the mentioned functions
from simian.combiner import read_json_file, generate_caption, generate_combinations

def test_read_json_file():
    # Mocking opening a file and reading JSON data
    mock_data = '{"name": "example", "type": "test"}'
    with patch("builtins.open", mock_open(read_data=mock_data)) as mocked_file:
        result = read_json_file("dummy_path.json")
        mocked_file.assert_called_once_with("dummy_path.json", "r")
        assert result == json.loads(mock_data), "read_json_file did not return expected dictionary."

def test_generate_caption():
    # Provide a sample input for generate_caption, including the 'uid' key
    combination = {
        "objects": [
            {
                "name": "Cube",
                "description": "A simple geometric shape",
                "uid": "12345"  # Unique identifier for the object
            }
        ],
        "background": {"name": "Beach"},
        "stage": {"material": {"name": "Sand"}},
        "orientation": {"pitch": 15, "yaw": 30}
    }
    caption = generate_caption(combination)
    assert "Cube" in caption, "Caption does not include object name."
    assert "Beach" in caption, "Caption does not include background name."
    assert "Sand" in caption, "Caption does not include material name."


def test_generate_combinations():
    # Prepare mock data for camera_data and a small count
    camera_data = {
        "orientation": {"yaw_min": 0, "yaw_max": 180, "pitch_min": -90, "pitch_max": 90},
        "framings": [{"name": "wide"}],
        "animations": [{"name": "zoom_in"}]
    }
    combinations = generate_combinations(camera_data, 2)
    assert len(combinations) == 2, "generate_combinations did not create the correct number of combinations."
    for combination in combinations:
        assert combination['orientation']['yaw'] <= 180, "Yaw is out of the specified range."
        assert combination['orientation']['pitch'] <= 90, "Pitch is out of the specified range."

if __name__ == "__main__":
    test_read_json_file()
    test_generate_caption()
    test_generate_combinations()
    print("All tests passed")
