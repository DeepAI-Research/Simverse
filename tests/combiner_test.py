import os
import sys
import json
from unittest.mock import patch, mock_open

current_dir = os.path.dirname(os.path.abspath(__file__))
combiner_path = os.path.join(current_dir, "../")
sys.path.append(combiner_path)

from simian.combiner import (
    read_json_file, generate_caption, generate_combinations, 
    generate_stage_captions, generate_orientation_caption,
    generate_object_scale_description_captions, generate_object_name_description_captions,
    generate_relationship_captions, generate_fov_caption, generate_postprocessing_caption,
    generate_framing_caption, flatten_descriptions, generate_animation_captions,
    generate_postprocessing, generate_orientation, generate_framing, generate_animation,
    generate_objects, generate_background, generate_stage
)


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


# Paths to the JSON files
data_dir = os.path.join(current_dir, "../data")
object_data_path = os.path.join(data_dir, "object_data.json")
stage_data_path = os.path.join(data_dir, "stage_data.json")
texture_data_path = os.path.join(data_dir, "texture_data.json")
camera_data_path = os.path.join(data_dir, "camera_data.json")
datasets_path = os.path.join(data_dir, "datasets.json")


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
                "uid": "12345",  # Unique identifier for the object
            }
        ],
        "background": {"name": "Beach"},
        "stage": {"material": {"name": "Sand"}},
        "orientation": {"pitch": 15, "yaw": 30},
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
        "orientation": {
            "yaw_min": 0,
            "yaw_max": 180,
            "pitch_min": -90,
            "pitch_max": 90,
        },
        "framings": [{"name": "wide"}],
        "animations": [{"name": "zoom_in"}],
    }
    combinations = generate_combinations(camera_data, 2)
    assert (
        len(combinations) == 2
    ), "generate_combinations did not create the correct number of combinations."
    for combination in combinations:
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
        "stage": {"material": {"name": "Grass"}}
    }

    with patch('simian.combiner.read_json_file', return_value=stage_data):
        captions = generate_stage_captions(combination)
        
        # Extract background and material prefixes from captions
        background_prefixes = stage_data["background_names"]
        material_prefixes = stage_data["material_names"]

        background_caption_found = any(f"The {prefix} is Forest." in captions for prefix in background_prefixes)
        material_caption_found = any(f"The {prefix} is Grass." in captions for prefix in material_prefixes)

        assert background_caption_found, "Stage caption did not include correct background prefix."
        assert material_caption_found, "Stage caption did not include correct material prefix."
        
        print("============ Test Passed: test_generate_stage_captions ============")


def test_generate_orientation_caption():
    combination = {"orientation": {"pitch": 15, "yaw": 90}}
    
    with patch('simian.combiner.read_json_file', return_value=camera_data):
        caption = generate_orientation_caption(camera_data, combination)
        
        # Extract pitch and yaw labels from the camera_data
        pitch_labels = camera_data["orientation"]["labels"]["pitch"]
        yaw_labels = camera_data["orientation"]["labels"]["yaw"]

        # Find the correct labels for the given pitch and yaw
        correct_pitch_label = pitch_labels["15"]
        correct_yaw_label = yaw_labels["90"]

        # Check if any of the correct pitch and yaw labels are in the caption
        pitch_caption_found = any(label in caption for label in correct_pitch_label)
        yaw_caption_found = any(label in caption for label in correct_yaw_label)

        assert pitch_caption_found, "Orientation caption does not include correct pitch label."
        assert yaw_caption_found, "Orientation caption does not include correct yaw label."
        
        print("============ Test Passed: test_generate_orientation_caption ============")


def test_generate_object_scale_description_captions():
    combination = {
        "objects": [
            {"name": "Box", "scale": {"factor": 1.0, "name_synonym": "average"}}
        ]
    }
    
    with patch('simian.combiner.read_json_file', return_value=object_data):
        captions = generate_object_scale_description_captions(combination)
        
        # Extract the expected relationship template from the object_data
        expected_relationship_templates = object_data["scale_description_relationship"]

        # Construct possible expected captions
        expected_captions = [template.replace("<name>", "Box").replace("<scale_factor>", "1.0").replace("<scale_name>", "average") for template in expected_relationship_templates]

        # Check if any of the expected captions are in the generated caption
        caption_found = any(expected_caption in captions for expected_caption in expected_captions)

        assert caption_found, "Object scale description caption is incorrect."
        
        print("============ Test Passed: test_generate_object_scale_description_captions ============")


def test_generate_object_name_description_captions():
    combination = {
        "objects": [
            {"name": "Box", "description": "A simple box"}
        ]
    }
    
    with patch('simian.combiner.read_json_file', return_value=object_data):
        captions = generate_object_name_description_captions(combination)
        
        # Extract the expected relationship template from the object_data
        expected_relationship_templates = object_data["name_description_relationship"]

        # Construct possible expected captions
        expected_captions = [template.replace("<name>", "Box").replace("<description>", "A simple box") for template in expected_relationship_templates]

        # Check if any of the expected captions are in the generated caption
        caption_found = any(expected_caption in captions for expected_caption in expected_captions)

        assert caption_found, "Object name description caption is incorrect."
        
        print("============ Test Passed: test_generate_object_name_description_captions ============")


def test_generate_relationship_captions():
    combination = {
        "objects": [
            {"name": "Box"},
            {"name": "Ball"}
        ],
        "orientation": {"yaw": 0}
    }

    with patch('simian.combiner.adjust_positions', return_value=[{"transformed_position": [0, 0]}, {"transformed_position": [1, 0]}]):
        with patch('simian.combiner.determine_relationships', return_value=["Box is near Ball"]):
            captions = generate_relationship_captions(combination)
            assert "Box is near Ball" in captions, "Relationship caption is incorrect."
    
    print("============ Test Passed: test_generate_relationship_captions ============")


def test_generate_fov_caption():
    combination = {
        "framing": {"fov": 45}
    }
    
    with patch('simian.combiner.math.tan', return_value=1):
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
            "The camera has a <mm> mm focal length.",
            "The focal length is <mm> mm.",
            "Set the focal length of the camera to <mm> mm.",
        ]
        
        # Construct possible expected captions
        expected_captions_degrees = [template.replace("<fov>", "45") for template in fov_templates_degrees]
        focal_length = 35 / (2 * 1)  # Since math.tan is mocked to return 1
        expected_captions_mm = [template.replace("<mm>", str(focal_length)) for template in fov_templates_mm]

        # Check if any of the expected captions are in the generated caption
        caption_found_degrees = any(expected_caption in caption for expected_caption in expected_captions_degrees)
        caption_found_mm = any(expected_caption in caption for expected_caption in expected_captions_mm)

        assert caption_found_degrees or caption_found_mm, "FOV caption is incorrect."
    
    print("============ Test Passed: test_generate_fov_caption ============")


def test_generate_postprocessing_caption():
    combination = {
        "postprocessing": {
            "bloom": {"type": "soft", "threshold": 1.0, "intensity": 0.8, "radius": 5.0},
            "ssao": {"type": "none", "distance": 0, "factor": 0},
            "ssrr": {"type": "none", "max_roughness": 0, "thickness": 0},
            "motionblur": {"type": "none", "shutter_speed": 0}
        }
    }
    
    caption = generate_postprocessing_caption(combination)
    
    # Construct possible expected captions for the bloom effect
    bloom_caption = f"The bloom effect is set to soft with a threshold of 1.00, intensity of 0.80, and radius of 5.00."
    
    # Check if the expected bloom caption is in the generated caption
    assert bloom_caption in caption, "Postprocessing caption is incorrect."
    
    print("============ Test Passed: test_generate_postprocessing_caption ============")


def test_generate_framing_caption():
    combination = {
        "framing": {"name": "wide", "fov": 45, "coverage_factor": 1}
    }

    with patch('simian.combiner.read_json_file', return_value=camera_data):
        caption = generate_framing_caption(camera_data, combination)

        # Extract the framing descriptions from the camera_data
        framing_templates = [f["descriptions"] for f in camera_data["framings"] if f["name"] == "wide"][0]

        # Construct possible expected captions
        expected_captions = [template.replace("<fov>", "45").replace("<coverage_factor>", "1") for template in framing_templates]

        # Check if any of the expected captions are in the generated caption
        caption_found = any(expected_caption in caption for expected_caption in expected_captions)

        assert caption_found, "Framing caption is incorrect."
    
    print("============ Test Passed: test_generate_framing_caption ============")


def test_flatten_descriptions():
    descriptions = [["part1", "part2"], ["part3", "part4"], "part5"]
    flat_descriptions = flatten_descriptions(descriptions)
    assert flat_descriptions == ["part1", "part2", "part3", "part4", "part5"], "Flatten descriptions is incorrect."
    print("============ Test Passed: test_flatten_descriptions ============")


def test_generate_animation_captions():
    combination = {
        "animation": {"speed_factor": 1.5}
    }

    with patch('simian.combiner.read_json_file', return_value=camera_data):
        captions = generate_animation_captions(combination, camera_data)
        
        # Extract the animation descriptions from the camera_data
        animation_types = camera_data["animations"][-1]["types"]
        expected_captions = []
        for details in animation_types.values():
            if details["min"] <= combination["animation"]["speed_factor"] <= details["max"]:
                expected_captions.extend(details["descriptions"])

        # Check if any of the expected captions are in the generated caption
        caption_found = any(expected_caption in captions for expected_caption in expected_captions)

        assert caption_found, "Animation caption is incorrect."
    
    print("============ Test Passed: test_generate_animation_captions ============")


def test_generate_postprocessing():
    camera_data = {
        "postprocessing": {
            "bloom": {"threshold_min": 0, "threshold_max": 1, "intensity_min": 0, "intensity_max": 1, "radius_min": 0, "radius_max": 10, "types": {"soft": {"intensity_min": 0, "intensity_max": 1}}},
            "ssao": {"distance_min": 0, "distance_max": 1, "factor_min": 0, "factor_max": 1, "types": {"soft": {"factor_min": 0, "factor_max": 1}}},
            "ssrr": {"min_max_roughness": 0, "max_max_roughness": 1, "min_thickness": 0, "max_thickness": 1, "types": {"soft": {"max_roughness_min": 0, "max_roughness_max": 1}}},
            "motionblur": {"shutter_speed_min": 0, "shutter_speed_max": 1, "types": {"soft": {"shutter_speed_min": 0, "shutter_speed_max": 1}}}
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
    with patch('simian.combiner.adjust_positions', return_value=objects):
        orientation = generate_orientation(camera_data, objects, background)
        assert orientation["yaw"] <= 180, "Orientation yaw is out of range."
        assert orientation["pitch"] <= 90, "Orientation pitch is out of range."
    print("============ Test Passed: test_generate_orientation ============")


def test_generate_framing():
    camera_data = {
        "framings": [{"name": "wide", "fov_min": 30, "fov_max": 60, "coverage_factor_min": 1, "coverage_factor_max": 2}]
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
    with patch('simian.combiner.random.choices', return_value=["dataset1"]):
        with patch('simian.combiner.random.randint', return_value=1):
            with patch('simian.combiner.dataset_dict', {"dataset1": [{"name": "Box", "uid": "123", "description": "A box"}]}):
                with patch('simian.combiner.captions_data', {"123": "A simple box"}):
                    objects = generate_objects()
                    assert len(objects) == 1, "Objects generation is incorrect."
                    assert objects[0]["name"] == "Box", "Object name is incorrect."
    print("============ Test Passed: test_generate_objects ============")


def test_generate_background():
    with patch('simian.combiner.random.choices', return_value=["background1"]):
        with patch('simian.combiner.background_dict', {"background1": {"id1": {"name": "Sky", "url": "sky_url"}}}):
            background = generate_background()
            assert background["name"] == "Sky", "Background name is incorrect."
            assert background["url"] == "sky_url", "Background url is incorrect."
    print("============ Test Passed: test_generate_background ============")


def test_generate_stage():
    with patch('simian.combiner.random.choices', return_value=["texture1"]):
        with patch('simian.combiner.texture_data', {"texture1": {"name": "Brick", "maps": {"diffuse": "brick_diffuse"}}}):
            stage = generate_stage()
            assert stage["material"]["name"] == "Brick", "Stage material name is incorrect."
            assert "uv_scale" in stage, "Stage uv_scale is missing."
            assert "uv_rotation" in stage, "Stage uv_rotation is missing."
    print("============ Test Passed: test_generate_stage ============")


if __name__ == "__main__":
    test_read_json_file()
    test_generate_caption()
    test_generate_combinations()
    test_generate_stage_captions()
    test_generate_orientation_caption()
    test_generate_object_scale_description_captions()
    test_generate_object_name_description_captions()
    test_generate_relationship_captions()
    test_generate_fov_caption()
    test_generate_postprocessing_caption()
    test_generate_framing_caption()
    test_flatten_descriptions()
    test_generate_animation_captions()
    test_generate_postprocessing()
    test_generate_orientation()
    test_generate_framing()
    test_generate_animation()
    test_generate_objects()
    test_generate_background()
    test_generate_stage()
    print("============ ALL TESTS PASSED ============")
