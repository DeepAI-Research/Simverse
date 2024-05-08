import json
from unittest.mock import patch, mock_open
import pytest
import random
from simian.combiner import read_json_file, generate_caption, generate_combinations


def test_read_json_file():
    # Mock the open function and json.load
    test_data = {"key": "value"}
    with patch(
        "builtins.open", mock_open(read_data=json.dumps(test_data))
    ) as mock_file, patch("json.load", return_value=test_data) as mock_json_load:
        result = read_json_file("dummy_path.json")
        mock_file.assert_called_once_with("dummy_path.json", "r")
        mock_json_load.assert_called()
        assert (
            result == test_data
        ), "The read_json_file function did not return the expected data"


def test_generate_caption():
    # Setup test data for generating a caption
    combination = {
        "objects": [
            {"name": "Object1", "description": "A cool object"},
            {"name": "Object2", "description": "Another cool object"},
        ],
        "background": {"name": "Beach"},
        "stage": {"material": {"name": "Sand"}},
        "orientation": {"descriptions": ["Object1 in front of Object2"]},
        "framing": {"descriptions": ["Close up of Object1 and Object2"]},
    }
    with patch(
        "random.choice", side_effect=lambda x: x[0]
    ):  # Always choose the first element
        caption = generate_caption(combination)
        assert (
            "Object1" in caption and "Object2" in caption and "Beach" in caption
        ), "Caption does not include all elements"


def test_generate_combinations():
    # Mock dependencies and inputs
    camera_data = {
        "orientations": ["Orientation1"],
        "framings": ["Framing1"],
        "animations": ["Animation1"],
    }
    with patch(
        "combiner.read_json_file", return_value={"models": {}, "backgrounds": {}}
    ), patch("random.choice", side_effect=lambda x: x[0]), patch(
        "random.choices", side_effect=lambda x, weights: [x[0]]
    ), patch(
        "random.randint", return_value=1
    ):  # Return 1 for number of objects
        combinations = generate_combinations(camera_data, 1)
        assert len(combinations) == 1, "Should generate exactly one combination"
        assert (
            combinations[0]["index"] == 0
        ), "Index of the generated combination should be 0"


# Run tests if this file is executed as a script
if __name__ == "__main__":
    test_read_json_file()
    test_generate_caption()
    test_generate_combinations()
