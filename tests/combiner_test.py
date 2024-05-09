import os
import sys
import json
from unittest.mock import patch, mock_open

current_dir = os.path.dirname(os.path.abspath(__file__))
combiner_path = os.path.join(current_dir, "../")
sys.path.append(combiner_path)

from simian.combiner import read_json_file, generate_caption, generate_combinations

def test_read_json_file():
    """
    Test the read_json_file function.
    """
    mock_data = '{"name": "example", "type": "test"}'
    with patch("builtins.open", mock_open(read_data=mock_data)) as mocked_file:
        result = read_json_file("dummy_path.json")
        mocked_file.assert_called_once_with("dummy_path.json", "r")
        assert result == json.loads(mock_data)
        print("============ Test Passed: test_read_json_file ============")


def test_generate_caption():
    """
    Test the generate_caption function.
    """
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
    print("============ Test Passed: test_generate_caption ============")


def test_generate_combinations():
    """
    Test the generate_combinations function.
    """
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
        print("============ Test Passed: test_generate_combinations ============")


if __name__ == "__main__":
    test_read_json_file()
    test_generate_caption()
    test_generate_combinations()
    print("============ ALL TESTS PASSED ============")
