import os
import sys
import json
import argparse
import math
from unittest.mock import patch, mock_open
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

# Mock arguments with absolute paths
mock_args = {
    "count": 2,
    "seed": 42,
    "max_number_of_objects": 5,
    "camera_file_path": os.path.join(project_root, "data/camera_data.json"),
    "object_data_path": os.path.join(project_root, "data/object_data.json"),
    "texture_data_path": os.path.join(project_root, "datasets/texture_data.json"),
    "datasets_path": os.path.join(project_root, "data/datasets.json"),
    "cap3d_captions_path": os.path.join(project_root, "datasets/cap3d_captions.json"),
    "simdata_path": os.path.join(project_root, "datasets"),
    "output_path": os.path.join(project_root, "combinations.json"),  # Corrected path
    "stage_data_path": os.path.join(project_root, "data/stage_data.json"),
}


def mock_parse_args(*args, **kwargs):
    return argparse.Namespace(**mock_args)


# Mock parse_args globally before importing simian.combiner
with patch("argparse.ArgumentParser.parse_args", new=mock_parse_args):
    from simian.combiner import (
        read_json_file,
        generate_combinations,
        generate_stage_captions,
        generate_orientation_caption,
        generate_object_name_description_captions,
        generate_relationship_captions,
        generate_fov_caption,
        generate_postprocessing_caption,
        generate_framing_caption,
        flatten_descriptions,
        generate_animation_captions,
        generate_postprocessing,
        generate_orientation,
        generate_framing,
        generate_animation,
        generate_objects,
        generate_background,
        generate_stage,
        flatten_descriptions,
        speed_factor_to_percentage,
    )


# Test function for generate_postprocessing_caption
def test_generate_postprocessing_caption():
    combination = {
        "postprocessing": {
            "bloom": {"type": "medium"},
            "ssao": {"type": "high"},
            "ssrr": {"type": "none"},
            "motionblur": {"type": "medium"},
        }
    }

    # Read the camera data from the file
    with open(mock_args["camera_file_path"], "r") as file:
        camera_data = json.load(file)

    # Mock the random.choice function to return predefined descriptions
    random_choices = [
        "medium bloom effect",
        "high ssao effect",
        "no ssrr effect",
        "medium motion blur"
    ]

    # Patch random.choice to return values from random_choices
    original_random_choice = random.choice
    random.choice = lambda x: random_choices.pop(0)

    # Patch random.randint to return specific values for predictable output
    original_random_randint = random.randint
    random.randint = lambda a, b: 0 if a == 1 and b == 4 else 3

    try:
        actual_caption = generate_postprocessing_caption(combination, camera_data)

        # Since the patched randint will pop 0 items, all parts should be in the actual caption
        expected_parts = [
            "medium bloom effect",
            "high ssao effect",
            "no ssrr effect",
            "medium motion blur"
        ]

        for part in expected_parts:
            assert part in actual_caption, f"Missing expected part in caption: {part}"

        print("============ Test Passed: test_generate_postprocessing_caption ============")
    finally:
        # Restore the original random functions
        random.choice = original_random_choice
        random.randint = original_random_randint


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


data_dir = os.path.join(project_root, "data")
datasets_dir = os.path.join(project_root, "datasets")

object_data = read_json_file(os.path.join(data_dir, "object_data.json"))
stage_data = read_json_file(os.path.join(data_dir, "stage_data.json"))
texture_data = read_json_file(os.path.join(datasets_dir, "texture_data.json"))
camera_data = read_json_file(os.path.join(data_dir, "camera_data.json"))
datasets_data = read_json_file(os.path.join(data_dir, "datasets.json"))
cap3d_captions_data = read_json_file(os.path.join(datasets_dir, "cap3d_captions.json"))


def test_combination_caption():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "../combinations.json")

    with open(file_path, "r") as file:
        data = json.load(file)

    first_combination = data["combinations"][0]

    required_combination_fields = [
        "index",
        "objects",
        "background",
        "orientation",
        "framing",
        "animation",
        "stage",
        "postprocessing",
        "caption",
    ]

    required_object_fields = [
        "name",
        "uid",
        "description",
        "placement",
        "from",
        "scale",
        "transformed_position",
        "relationships",
    ]

    required_scale_fields = ["factor", "name", "name_synonym"]

    required_background_fields = ["name", "url", "id", "from"]
    required_orientation_fields = ["yaw", "pitch"]
    required_framing_fields = ["fov", "coverage_factor", "name"]
    required_animation_fields = ["name", "keyframes", "speed_factor"]
    required_stage_fields = ["material", "uv_scale", "uv_rotation"]
    required_material_fields = ["name", "maps"]
    required_postprocessing_fields = ["bloom", "ssao", "ssrr", "motionblur"]
    required_bloom_fields = ["threshold", "intensity", "radius", "type"]
    required_ssao_fields = ["distance", "factor", "type"]
    required_ssrr_fields = ["max_roughness", "thickness", "type"]
    required_motionblur_fields = ["shutter_speed", "type"]

    def assert_fields_exist(data, required_fields, parent_key=""):
        for field in required_fields:
            assert field in data, f"Missing field: {parent_key}{field}"

    # Check combination level fields
    assert_fields_exist(first_combination, required_combination_fields)

    # Check objects fields
    for obj in first_combination["objects"]:
        assert_fields_exist(obj, required_object_fields)
        assert_fields_exist(obj["scale"], required_scale_fields)

    # Check background fields
    assert_fields_exist(first_combination["background"], required_background_fields)

    # Check orientation fields
    assert_fields_exist(first_combination["orientation"], required_orientation_fields)

    # Check framing fields
    assert_fields_exist(first_combination["framing"], required_framing_fields)

    # Check animation fields
    assert_fields_exist(first_combination["animation"], required_animation_fields)

    # Check stage fields
    assert_fields_exist(first_combination["stage"], required_stage_fields)
    assert_fields_exist(
        first_combination["stage"]["material"], required_material_fields
    )

    # Check postprocessing fields
    assert_fields_exist(
        first_combination["postprocessing"], required_postprocessing_fields
    )
    assert_fields_exist(
        first_combination["postprocessing"]["bloom"], required_bloom_fields
    )
    assert_fields_exist(
        first_combination["postprocessing"]["ssao"], required_ssao_fields
    )
    assert_fields_exist(
        first_combination["postprocessing"]["ssrr"], required_ssrr_fields
    )
    assert_fields_exist(
        first_combination["postprocessing"]["motionblur"], required_motionblur_fields
    )

    print("============ Test Passed: test_first_object_requirements ============")


def test_generate_combinations():
    """
    Test the generate_combinations function.
    """
    # Prepare mock data for camera_data and a small count
    camera_data = {
        "orientation": {
            "yaw_min": 0,
            "yaw_max": 180,
            "pitch_min": -90,
            "pitch_max": 90,
        },
        "framings": [
            {
                "name": "wide",
                "fov_min": 30,
                "fov_max": 60,
                "coverage_factor_min": 1,
                "coverage_factor_max": 2,
                "descriptions": [
                    "Wide framing with FOV <fov> and coverage factor <coverage_factor>."
                ],
            }
        ],
        "animations": [
            {
                "name": "zoom_in",
                "types": {
                    "slow": {"min": 0.5, "max": 1.0, "descriptions": ["Slow zoom in."]},
                    "fast": {"min": 1.0, "max": 2.0, "descriptions": ["Fast zoom in."]},
                },
            }
        ],
        "postprocessing": {
            "bloom": {
                "threshold_min": 0,
                "threshold_max": 1,
                "intensity_min": 0,
                "intensity_max": 1,
                "radius_min": 0,
                "radius_max": 10,
                "types": {"low": {"intensity_min": 0, "intensity_max": 1}},
            },
            "ssao": {
                "distance_min": 0,
                "distance_max": 1,
                "factor_min": 0,
                "factor_max": 1,
                "types": {"low": {"factor_min": 0, "factor_max": 1}},
            },
            "ssrr": {
                "min_max_roughness": 0,
                "max_max_roughness": 1,
                "min_thickness": 0,
                "max_thickness": 1,
                "types": {"low": {"max_roughness_min": 0, "max_roughness_max": 1}},
            },
            "motionblur": {
                "shutter_speed_min": 0,
                "shutter_speed_max": 1,
                "types": {"low": {"shutter_speed_min": 0, "shutter_speed_max": 1}},
            },
        },
    }
    count = 2
    seed = 42  # Add seed argument
    combinations = generate_combinations(camera_data, count, seed)
    assert (
        len(combinations["combinations"]) == count
    ), "generate_combinations did not create the correct number of combinations."
    for combination in combinations["combinations"]:
        assert (
            combination["orientation"]["yaw"] <= 180
        ), "Yaw is out of the specified range."
        assert (
            combination["orientation"]["pitch"] <= 90
        ), "Pitch is out of the specified range."
        print("============ Test Passed: test_generate_combinations ============")


def test_generate_stage_captions():
    combination = {
        "background": {"name": "Forest"},
        "stage": {"material": {"name": "Grass"}},
    }

    with patch("simian.combiner.read_json_file", return_value=stage_data):
        captions = generate_stage_captions(combination)

        # Extract background and material prefixes from captions
        background_prefixes = stage_data["background_names"]
        material_prefixes = stage_data["material_names"]

        background_caption_found = any(
            f"The {prefix} is Forest." in captions for prefix in background_prefixes
        )
        material_caption_found = any(
            f"The {prefix} is Grass." in captions for prefix in material_prefixes
        )

        assert (
            background_caption_found
        ), "Stage caption did not include correct background prefix."
        assert (
            material_caption_found
        ), "Stage caption did not include correct material prefix."

        print("============ Test Passed: test_generate_stage_captions ============")


def test_generate_orientation_caption():
    combination = {"orientation": {"pitch": 15, "yaw": 90}}

    with patch("simian.combiner.read_json_file", return_value=camera_data):
        caption = generate_orientation_caption(camera_data, combination)

        # Extract pitch and yaw labels from the camera_data
        pitch_labels = camera_data["orientation"]["labels"]["pitch"]
        yaw_labels = camera_data["orientation"]["labels"]["yaw"]

        # Ensure the correct pitch and yaw values exist in the labels
        correct_pitch_label = pitch_labels.get("15", [])
        correct_yaw_label = yaw_labels.get("90", [])

        # Replace <degrees> placeholder with the actual yaw value
        correct_pitch_label = [
            label.replace("<degrees>", str(combination["orientation"]["pitch"]))
            for label in correct_pitch_label
        ]
        correct_yaw_label = [
            label.replace("<degrees>", str(combination["orientation"]["yaw"]))
            for label in correct_yaw_label
        ]

        # Print statements for debugging
        print("Correct pitch label:", correct_pitch_label)
        print("Correct yaw label:", correct_yaw_label)
        print("Generated caption:", caption)

        # Check if any of the correct pitch and yaw labels are in the caption
        pitch_caption_found = any(label in caption for label in correct_pitch_label)
        yaw_caption_found = any(label in caption for label in correct_yaw_label)

        assert (
            pitch_caption_found
        ), "Orientation caption does not include correct pitch label."
        assert (
            yaw_caption_found
        ), "Orientation caption does not include correct yaw label."

        print(
            "============ Test Passed: test_generate_orientation_caption ============"
        )


def test_generate_object_name_description_captions():
    combination = {
        "objects": [
            {
                "name": "Box",
                "description": "A simple box",
                "scale": {
                    "factor": 0.75,
                    "name": "small-medium",
                    "name_synonym": "medium-small",
                },
            }
        ]
    }

    with patch("simian.combiner.read_json_file", return_value=object_data):
        captions = generate_object_name_description_captions(combination)

        # Extract the expected relationship template from the object_data
        expected_relationship_templates = object_data["name_description_relationship"]

        # Construct possible expected captions
        expected_captions = [
            template.replace("<name>", "Box").replace("<description>", "A simple box")
            for template in expected_relationship_templates
        ]

        # Check if any of the expected captions are in the generated caption
        caption_found = any(
            expected_caption in captions for expected_caption in expected_captions
        )

        assert caption_found, "Object name description caption is incorrect."

        print(
            "============ Test Passed: test_generate_object_name_description_captions ============"
        )


def test_generate_relationship_captions():
    combination = {
        "objects": [{"name": "Box"}, {"name": "Ball"}],
        "orientation": {"yaw": 0},
    }

    with patch(
        "simian.combiner.adjust_positions",
        return_value=[
            {"transformed_position": [0, 0]},
            {"transformed_position": [1, 0]},
        ],
    ):
        with patch(
            "simian.combiner.determine_relationships", return_value=["Box is near Ball"]
        ):
            captions = generate_relationship_captions(combination)
            print("Generated captions:", captions)  # Add this line for debugging
            assert "Box is near Ball" in captions, "Relationship caption is incorrect."

    print("============ Test Passed: test_generate_relationship_captions ============")


def test_generate_fov_caption():
    combination = {"framing": {"fov": 45}}

    with patch("random.choice", side_effect=["degrees", "The camera has a <fov> degree field of view."]):
        caption = generate_fov_caption(combination)

        # Extract the FOV templates from the function (hardcoded here for simplicity)
        fov_templates_degrees = [
            "The camera has a <fov> degree field of view.",
            "The camera has a <fov> degree FOV.",
            "The field of view is <fov> degrees.",
            "Set the fov of the camera to <fov> degrees.",
            "Set the FOV of the camera to <fov>°",
        ]
        fov_templates_mm = [
            "The camera has a <mm> mm focal length.",
            "The focal length is <mm> mm.",
            "Set the focal length of the camera to <mm> mm.",
        ]

        # Construct possible expected captions
        expected_captions_degrees = [
            template.replace("<fov>", "45") for template in fov_templates_degrees
        ]
        focal_length = 35 / (2 * math.tan(math.radians(45) / 2))  # Calculate the focal length
        expected_captions_mm = [
            template.replace("<mm>", str(focal_length)) for template in fov_templates_mm
        ]

        # Check if any of the expected captions are in the generated caption
        caption_found_degrees = any(
            expected_caption in caption
            for expected_caption in expected_captions_degrees
        )
        caption_found_mm = any(
            expected_caption in caption for expected_caption in expected_captions_mm
        )

        assert caption_found_degrees or caption_found_mm, "FOV caption is incorrect."
    print("============ Test Passed: test_generate_fov_caption ============")


def test_generate_postprocessing():
    camera_data = {
        "postprocessing": {
            "bloom": {
                "threshold_min": 0.1,
                "threshold_max": 0.9,
                "intensity_min": 0.1,
                "intensity_max": 0.9,
                "radius_min": 0.1,
                "radius_max": 0.9,
                "types": {
                    "type1": {"intensity_min": 0.1, "intensity_max": 0.5},
                    "type2": {"intensity_min": 0.6, "intensity_max": 0.9},
                },
            },
            # Add similar data for ssao, ssrr, and motionblur
        }
    }

    with patch("random.uniform", side_effect=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]):
        postprocessing = generate_postprocessing(camera_data)

        assert postprocessing["bloom"]["threshold"] == 0.3
        assert postprocessing["bloom"]["intensity"] == 0.4
        assert postprocessing["bloom"]["radius"] == 0.5
        assert postprocessing["bloom"]["type"] == "type1"

        # Add similar assertions for ssao, ssrr, and motionblur
    print("============ Test Passed: test_generate_postprocessing ============")


def test_generate_framing_caption():
    combination = {"framing": {"name": "wide", "fov": 45, "coverage_factor": 1}}

    with patch("simian.combiner.read_json_file", return_value=camera_data):
        caption = generate_framing_caption(camera_data, combination)

        # Extract the framing descriptions from the camera_data
        framing_templates = [
            f["descriptions"] for f in camera_data["framings"] if f["name"] == "wide"
        ][0]

        # Construct possible expected captions
        expected_captions = [
            template.replace("<fov>", "45").replace("<coverage_factor>", "1")
            for template in framing_templates
        ]

        # Check if any of the expected captions are in the generated caption
        caption_found = any(
            expected_caption in caption for expected_caption in expected_captions
        )

        assert caption_found, "Framing caption is incorrect."

    print("============ Test Passed: test_generate_framing_caption ============")


def test_flatten_descriptions():
    descriptions = [["part1", "part2"], ["part3", "part4"], "part5"]
    flat_descriptions = flatten_descriptions(descriptions)
    assert flat_descriptions == [
        "part1",
        "part2",
        "part3",
        "part4",
        "part5",
    ], "Flatten descriptions is incorrect."
    print("============ Test Passed: test_flatten_descriptions ============")


def test_generate_animation_captions():
    combination = {"animation": {"speed_factor": 1.5}}

    captions = generate_animation_captions(combination)

    # Extract the animation descriptions from the camera_data
    animation_types = camera_data["animation_speed"]["types"]
    expected_captions = []
    for details in animation_types.values():
        if details["min"] <= combination["animation"]["speed_factor"] <= details["max"]:
            expected_captions.extend(details["descriptions"])

    # Flatten the expected_captions list
    flat_expected_captions = flatten_descriptions(expected_captions)

    # Check if any of the expected captions are in the generated caption
    speed_factor_str = speed_factor_to_percentage(
        combination["animation"]["speed_factor"]
    )
    caption_found = any(
        expected_caption.replace("<animation_speed_value>", speed_factor_str)
        in captions
        for expected_caption in flat_expected_captions
    ) or any(
        expected_caption.replace(
            "<animation_speed_value>", f"{combination['animation']['speed_factor']}x"
        )
        in captions
        for expected_caption in flat_expected_captions
    )

    assert caption_found, "Animation caption is incorrect."

    print("============ Test Passed: test_generate_animation_captions ============")


def test_generate_postprocessing():
    camera_data = {
        "postprocessing": {
            "bloom": {
                "threshold_min": 0,
                "threshold_max": 1,
                "intensity_min": 0,
                "intensity_max": 1,
                "radius_min": 0,
                "radius_max": 10,
                "types": {"low": {"intensity_min": 0, "intensity_max": 1}},
            },
            "ssao": {
                "distance_min": 0,
                "distance_max": 1,
                "factor_min": 0,
                "factor_max": 1,
                "types": {"low": {"factor_min": 0, "factor_max": 1}},
            },
            "ssrr": {
                "min_max_roughness": 0,
                "max_max_roughness": 1,
                "min_thickness": 0,
                "max_thickness": 1,
                "types": {"low": {"max_roughness_min": 0, "max_roughness_max": 1}},
            },
            "motionblur": {
                "shutter_speed_min": 0,
                "shutter_speed_max": 1,
                "types": {"low": {"shutter_speed_min": 0, "shutter_speed_max": 1}},
            },
        }
    }
    postprocessing = generate_postprocessing(camera_data)
    assert "bloom" in postprocessing, "Postprocessing generation is incorrect."
    assert "ssao" in postprocessing, "Postprocessing generation is incorrect."
    assert "ssrr" in postprocessing, "Postprocessing generation is incorrect."
    assert "motionblur" in postprocessing, "Postprocessing generation is incorrect."
    print("============ Test Passed: test_generate_postprocessing ============")


def test_generate_orientation():
    camera_data = {
        "orientation": {"yaw_min": 0, "yaw_max": 180, "pitch_min": -90, "pitch_max": 90}
    }
    objects = [{"transformed_position": [0, 0]}, {"transformed_position": [1, 0]}]
    background = {"name": "Sky"}
    with patch("simian.combiner.adjust_positions", return_value=objects):
        orientation = generate_orientation(camera_data, objects, background)
        assert orientation["yaw"] <= 180, "Orientation yaw is out of range."
        assert orientation["pitch"] <= 90, "Orientation pitch is out of range."
    print("============ Test Passed: test_generate_orientation ============")


def test_generate_framing():
    camera_data = {
        "framings": [
            {
                "name": "wide",
                "fov_min": 30,
                "fov_max": 60,
                "coverage_factor_min": 1,
                "coverage_factor_max": 2,
            }
        ]
    }
    framing = generate_framing(camera_data)
    assert framing["fov"] >= 30, "FOV is out of range."
    assert framing["fov"] <= 60, "FOV is out of range."
    assert framing["name"] == "wide", "Framing name is incorrect."
    print("============ Test Passed: test_generate_framing ============")


def test_generate_animation():
    camera_data = {
        "animations": [{"name": "zoom_in", "keyframes": [{"start": 0, "end": 1}]}]
    }
    animation = generate_animation(camera_data)
    assert animation["name"] == "zoom_in", "Animation name is incorrect."
    assert "speed_factor" in animation, "Animation speed_factor is missing."
    print("============ Test Passed: test_generate_animation ============")


def test_generate_objects():
    with patch("simian.combiner.random.choices", return_value=["dataset1"]):
        with patch("simian.combiner.random.randint", return_value=1):
            with patch(
                "simian.combiner.dataset_dict",
                {"dataset1": [{"name": "Box", "uid": "123", "description": "A box"}]},
            ):
                with patch("simian.combiner.captions_data", {"123": "A simple box"}):
                    objects = generate_objects()
                    assert len(objects) == 1, "Objects generation is incorrect."
                    assert objects[0]["name"] == "Box", "Object name is incorrect."
    print("============ Test Passed: test_generate_objects ============")


def test_generate_background():
    with patch("simian.combiner.random.choices", return_value=["background1"]):
        with patch(
            "simian.combiner.background_dict",
            {"background1": {"id1": {"name": "Sky", "url": "sky_url"}}},
        ):
            background = generate_background()
            assert background["name"] == "Sky", "Background name is incorrect."
            assert background["url"] == "sky_url", "Background url is incorrect."
    print("============ Test Passed: test_generate_background ============")


def test_generate_stage():
    with patch("simian.combiner.random.choices", return_value=["texture1"]):
        with patch(
            "simian.combiner.texture_data",
            {"texture1": {"name": "Brick", "maps": {"diffuse": "brick_diffuse"}}},
        ):
            stage = generate_stage()
            assert (
                stage["material"]["name"] == "Brick"
            ), "Stage material name is incorrect."
            assert "uv_scale" in stage, "Stage uv_scale is missing."
            assert "uv_rotation" in stage, "Stage uv_rotation is missing."
    print("============ Test Passed: test_generate_stage ============")


if __name__ == "__main__":
    test_read_json_file()
    test_combination_caption()
    test_generate_combinations()
    test_generate_stage_captions()
    test_generate_orientation_caption()
    test_generate_object_name_description_captions()
    test_generate_relationship_captions()
    test_generate_fov_caption()
    test_generate_framing_caption()
    test_flatten_descriptions()
    test_generate_animation_captions()
    test_generate_postprocessing()
    test_generate_postprocessing_caption()
    test_generate_orientation()
    test_generate_framing()
    test_generate_animation()
    test_generate_objects()
    test_generate_background()
    test_generate_stage()
    print("============ ALL TESTS PASSED ============")
