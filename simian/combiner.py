import json
import math
import os
import random
import argparse
import re
import sys

# Get the directory of the currently executing script
current_dir = os.path.dirname(os.path.abspath(__file__))

# if the directory is simian, remove that
if current_dir.endswith("simian"):
    current_dir = os.path.dirname(current_dir)

# Append the simian directory to sys.path
simian_path = os.path.join(current_dir)
sys.path.append(simian_path)

from simian.transform import determine_relationships, adjust_positions


def read_json_file(file_path):
    """
    Read a JSON file and return the data as a dictionary.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Data from the JSON file.
    """
    with open(file_path, "r") as file:
        return json.load(file)


def parse_args():
    """
    Parse command line arguments using argparse.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Generate random camera combinations.")
    parser.add_argument(
        "--count", type=int, default=10, help="Number of combinations to generate"
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Seed for the random number generator"
    )
    parser.add_argument(
        "--max_number_of_objects",
        type=int,
        default=5,
        help="Maximum number of objects to randomly select",
    )
    parser.add_argument(
        "--camera_file_path",
        type=str,
        default="data/camera_data.json",
        help="Path to the JSON file containing camera data",
    )
    parser.add_argument(
        "--object_data_path",
        type=str,
        default="data/object_data.json",
        help="Path to the JSON file containing object data",
    )
    parser.add_argument(
        "--texture_data_path",
        type=str,
        default="datasets/texture_data.json",
        help="Path to the JSON file containing texture data",
    )
    parser.add_argument(
        "--datasets_path",
        type=str,
        default="data/datasets.json",
        help="Path to the file which lists all the datasets to use",
    )
    parser.add_argument(
        "--cap3d_captions_path",
        type=str,
        default="datasets/cap3d_captions.json",
        help="Path to the JSON file containing captions data",
    )
    parser.add_argument(
        "--simdata_path",
        type=str,
        default="datasets",
        help="Path to the simdata directory",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="combinations.json",
        help="Path to the output file",
    )
    parser.add_argument(
        "--stage_data_path",
        type=str,
        default="data/stage_data.json",
        help="Path to the JSON file containing stage data",
    )
    return parser.parse_args()


datasets = read_json_file(parse_args().datasets_path)
object_data = read_json_file(parse_args().object_data_path)
captions_data = read_json_file(parse_args().cap3d_captions_path)
stage_data = read_json_file(parse_args().stage_data_path)
texture_data = read_json_file(parse_args().texture_data_path)
camera_data = read_json_file(parse_args().camera_file_path)

models = datasets["models"]
dataset_dict = {}
object_map = {}
category_map = {}

for dataset in models:
    current_path = os.path.dirname(os.path.realpath(__file__))
    dataset_path = os.path.join(parse_args().simdata_path, dataset + ".json")
    dataset_full_path = os.path.join(current_path, "../", dataset_path)
    print(f"Loading {dataset_full_path}")
    if os.path.exists(dataset_full_path):
        dataset_data = read_json_file(dataset_full_path)
        local_count = 0

        for object in dataset_data:
            object_id = object["uid"]
            categories = object["categories"]

            if object_id not in object_map:
                object_map[object_id] = object
                local_count += 1

            for category in categories:
                if category not in category_map:
                    category_map[category] = set()
                category_map[category].add(object_id)

        print(
            f"Loaded {local_count} unique entries out of {len(dataset_data)} from {dataset}"
        )
        dataset_dict[dataset] = dataset_data
    else:
        print(f"Dataset file {dataset_path} not found")

# count the total length of all entries
total_length = 0

for dataset in dataset_dict:
    total_length += len(dataset_dict[dataset])
print(f"Total number of objects: {total_length}")

backgrounds = datasets["backgrounds"]
background_data = {}
background_dict = {}

for background in backgrounds:
    # get the current path of this file
    current_path = os.path.dirname(os.path.realpath(__file__))
    hdri_path = os.path.join(parse_args().simdata_path, background + ".json")
    background_full_path = os.path.join(current_path, "../", hdri_path)
    print(f"Loading {background_full_path}")
    if os.path.exists(background_full_path):
        background_data = read_json_file(background_full_path)
        print(f"Loaded {len(background_data)} from {background}")
        background_dict[background] = background_data
    else:
        print(f"Dataset file {hdri_path} not found")

total_length = 0
for background in background_dict:
    total_length += len(background_dict[background])
print(f"Total number of backgrounds: {total_length}")

dataset_names = list(dataset_dict.keys())
dataset_weights = [len(dataset_dict[name]) for name in dataset_names]

background_names = list(background_dict.keys())
background_weights = [len(background_dict[name]) for name in background_names]


def generate_stage_captions(combination):
    """
    Generate captions for the stage based on the combination data.

    Args:
        combination (dict): Combination data.

    Returns:
        list: List of stage captions.
    """
    stage_data = read_json_file("data/stage_data.json")
    background_prefix = random.choice(stage_data["background_names"])
    floor_prefix = random.choice(stage_data["material_names"])
    background_name = combination["background"]["name"]
    floor_material_name = combination["stage"]["material"]["name"]

    # remove all numbers and trim
    floor_material_name = "".join(
        [i for i in floor_material_name if not i.isdigit()]
    ).strip()
    background_name = (
        "".join([i for i in background_name if not i.isdigit()])
        .strip()
        .replace("#", "")
        .replace("_", " ")
        .replace("(", "")
        .replace(")", "")
    )
    caption_parts = []
    caption_parts.append(f"The {background_prefix} is {background_name}.")
    caption_parts.append(f"The {floor_prefix} is {floor_material_name}.")
    return caption_parts


def generate_orientation_caption(camera_data, combination):
    """
    Generate a caption for the camera orientation based on the combination data.

    Args:
        camera_data (dict): Camera data.
        combination (dict): Combination data.

    Returns:
        str: Orientation caption.
    """
    pitch_labels = camera_data["orientation"]["labels"]["pitch"]
    yaw_labels = camera_data["orientation"]["labels"]["yaw"]

    closest_pitch_label = min(
        pitch_labels.keys(),
        key=lambda x: abs(int(x) - int(combination["orientation"]["pitch"])),
    )
    closest_yaw_label = min(
        yaw_labels.keys(),
        key=lambda x: abs(int(x) - int(combination["orientation"]["yaw"])),
    )

    # Replace the placeholders in the camera text with the closest matching labels
    orientation_text = random.choice(camera_data["orientation"]["descriptions"])
    orientation_text = orientation_text.replace(
        "<pitch>", random.choice(pitch_labels[closest_pitch_label])
    ).replace("<degrees>", str(combination["orientation"]["pitch"]))
    orientation_text = orientation_text.replace(
        "<yaw>", random.choice(yaw_labels[closest_yaw_label])
    ).replace("<degrees>", str(combination["orientation"]["yaw"]))

    return orientation_text


def generate_object_name_description_captions(combination):
    """
    Generate captions for object names and descriptions based on the combination data.

    Args:
        combination (dict): Combination data.

    Returns:
        str: Object name and description captions.
    """
    object_name_descriptions = []
    # for each object in the scene
    for obj in combination["objects"]:
        # get the object name and description
        object_name = obj["name"]
        object_description = obj["description"]

        # get the relationship between the object name and description
        object_name_description_relationship = random.choice(
            object_data["name_description_relationship"]
        )

        object_name_description_relationship = (
            object_name_description_relationship.replace("<name>", object_name)
        )
        object_name_description_relationship = (
            object_name_description_relationship.replace(
                "<description>", object_description
            )
        )

        # get the scale factor and scale name
        object_scale_description = random.choice(
            object_data["scale_description_relationship"]
        )
        object_scale_description = object_scale_description.replace(
            "<name>", object_name
        )
        object_scale_description = object_scale_description.replace(
            "<scale_factor>", str(obj["scale"]["factor"])
        )
        object_scale_description = object_scale_description.replace(
            "<scale_name>", obj["scale"]["name_synonym"]
        )

        object_name_descriptions.append(object_name_description_relationship)
        object_name_descriptions.append(object_scale_description)

    # randomize order of object_descriptions
    random.shuffle(object_name_descriptions)
    # join the object descriptions
    object_name_descriptions = " ".join(object_name_descriptions)
    return object_name_descriptions


def generate_relationship_captions(combination):
    """
    Generate captions for object relationships based on the combination data.

    Args:
        combination (dict): Combination data.

    Returns:
        list: List of relationship captions.
    """
    THRESHOLD_RELATIONSHIPS = len(combination["objects"])

    adjusted_objects = adjust_positions(
        combination["objects"], combination["orientation"]["yaw"]
    )
    relationships = determine_relationships(adjusted_objects, object_data)

    # Write relationships into the JSON file with combination["objects"]["relationships"]
    for i, obj in enumerate(combination["objects"]):
        if "relationships" not in obj:
            obj["relationships"] = []
        if i < len(relationships):
            obj["relationships"] = relationships[i]

    selected_relationships = []

    if THRESHOLD_RELATIONSHIPS != 1:
        selected_relationships = random.sample(relationships, THRESHOLD_RELATIONSHIPS)

    return selected_relationships


def generate_fov_caption(combination):
    """
    Generate a caption for the field of view (FOV) based on the combination data.

    Args:
        combination (dict): Combination data.

    Returns:
        str: FOV caption.
    """
    fov_templates = {
        "degrees": [
            "The camera has a <fov> degree field of view.",
            "The camera has a <fov> degree FOV.",
            "The field of view is <fov> degrees.",
            "Set the fov of the camera to <fov> degrees.",
            "Set the FOV of the camera to <fov>°",
        ],
        "mm": [
            "The camera has a <mm> mm focal length.",
            "The camera has a <mm> mm focal length.",
            "The focal length is <mm> mm.",
            "Set the focal length of the camera to <mm> mm.",
        ],
    }

    fov = combination["framing"]["fov"]

    # FOV is stored as degrees in the framing data
    fov_types = "degrees", "mm"

    # Select a random FOV type
    fov_type = random.choice(fov_types)

    # Select a random FOV template
    fov_template = random.choice(fov_templates[fov_type])

    # Replace the <fov> placeholder with the FOV value
    fov_template = fov_template.replace("<fov>", str(fov))

    # Convert FOV to focal length
    focal_length = 35 / (2 * math.tan(math.radians(fov) / 2))
    fov_caption = fov_template.replace("<mm>", str(focal_length))

    if fov_type == "degrees":
        fov_caption += f" ({focal_length:.2f} mm focal length)"

    return fov_caption


def generate_postprocessing_caption(combination):
    """
    Generate a caption for postprocessing based on the combination data.

    Args:
        combination (dict): Combination data.

    Returns:
        str: Postprocessing caption.
    """
    postprocessing = combination["postprocessing"]

    caption_parts = []

    # Bloom
    if postprocessing["bloom"]["type"] != "none":
        bloom_caption = f"The bloom effect is set to {postprocessing['bloom']['type']} with a threshold of {postprocessing['bloom']['threshold']:.2f}, intensity of {postprocessing['bloom']['intensity']:.2f}, and radius of {postprocessing['bloom']['radius']:.2f}."
        caption_parts.append(bloom_caption)

    # SSAO
    if postprocessing["ssao"]["type"] != "none":
        ssao_caption = f"The screen space ambient occlusion (SSAO) effect is set to {postprocessing['ssao']['type']} with a distance of {postprocessing['ssao']['distance']:.2f} and factor of {postprocessing['ssao']['factor']:.2f}."
        caption_parts.append(ssao_caption)

    # SSRR
    if postprocessing["ssrr"]["type"] != "none":
        ssrr_caption = f"The screen space reflections (SSRR) effect is set to {postprocessing['ssrr']['type']} with a maximum roughness of {postprocessing['ssrr']['max_roughness']:.2f} and thickness of {postprocessing['ssrr']['thickness']:.2f}."
        caption_parts.append(ssrr_caption)

    # Motion Blur
    if postprocessing["motionblur"]["type"] != "none":
        motionblur_caption = f"The motion blur effect is set to {postprocessing['motionblur']['type']} with a shutter speed of {postprocessing['motionblur']['shutter_speed']:.2f}."
        caption_parts.append(motionblur_caption)

    return " ".join(caption_parts)


def generate_framing_caption(camera_data, combination):
    """
    Generate a caption for framing based on the camera data and combination data.

    Args:
        camera_data (dict): Camera data.
        combination (dict): Combination data.

    Returns:
        str: Framing caption.
    """
    framing = combination["framing"]
    framing_name = framing["name"]

    # Find the matching framing in camera_data
    matching_framing = next(
        (f for f in camera_data["framings"] if f["name"] == framing_name), None
    )

    if matching_framing:
        framing_description = random.choice(matching_framing["descriptions"])
        framing_description = framing_description.replace("<fov>", str(framing["fov"]))
        framing_description = framing_description.replace(
            "<coverage_factor>", str(framing["coverage_factor"])
        )
        return framing_description
    else:
        return ""
    

def generate_animation_captions(combination):
    """
    Generate captions for camera animations based on the combination data.
    This is based on speed_factor

    Args:
        combination (dict): Combination data.

    Returns:
        list: List of animation captions.
    """

    """
    "animation": {
        "name": "tilt_down",
        "keyframes": [
            {
                "Camera": {
                    "rotation": [
                        15,
                        0,
                        0
                    ]
                }
            },
            {
                "Camera": {
                    "rotation": [
                        -15,
                        0,
                        0
                    ]
                }
            }
        ],
        "speed_factor": 1.2154695988360353
    },
    """
    animation = combination["animation"]
    animation_name = animation["name"]
    speed_factor = animation["speed_factor"]

    animation_data = camera_data["animations"]
    matching_animation = next(
        (a for a in animation_data if a["name"] == animation_name), None
    )

    if matching_animation:
        animation_description = random.choice(matching_animation["descriptions"])
        animation_description = animation_description.replace(
            "<speed_factor>", str(speed_factor)
        )
        return [animation_description]
    
    return []


def generate_caption(combination):
    """
    Generate a complete caption based on the combination data.

    Args:
        combination (dict): Combination data.

    Returns:
        str: Complete caption.
    """
    caption_parts = []

    # Add object name and description captions to the caption
    object_name_descriptions = generate_object_name_description_captions(combination)
    caption_parts.append(object_name_descriptions)

    # Add the camera orientation to the caption
    orientation_text = generate_orientation_caption(camera_data, combination)
    caption_parts.append(orientation_text)

    fov_caption = generate_fov_caption(combination)
    caption_parts.append(fov_caption)

    framing_caption = generate_framing_caption(camera_data, combination)
    caption_parts.append(framing_caption)

    postprocessing_caption = generate_postprocessing_caption(combination)
    caption_parts.append(postprocessing_caption)

    # Add the stage caption
    stage_captions = generate_stage_captions(combination)
    caption_parts.extend(stage_captions)

    animation_captions = generate_animation_captions(combination)
    caption_parts.extend(animation_captions)

    # Add the relationship captions
    selected_relationships = generate_relationship_captions(combination)
    caption_parts.extend(selected_relationships)

    # Randomize the caption parts order
    caption_parts = random.sample(caption_parts, len(caption_parts))

    # Trim the caption parts
    caption = (
        " ".join(caption_parts)
        .replace("..", ".")
        .replace("  ", " ")
        .replace(" .", ".")
        .replace(" ,", ",")
        .replace(",.", ".")
        .replace(".,", ",")
    )
    caption = re.sub(r"\.(?=[a-zA-Z])", ". ", caption)  # Add space after period
    caption = caption.strip()  # Remove leading and trailing whitespace

    return caption


def generate_postprocessing(camera_data):
    """
    Generate postprocessing settings based on the camera data.

    Args:
        camera_data (dict): Camera data.

    Returns:
        dict: Postprocessing settings.
    """
    postprocessing = {}

    bloom_data = camera_data["postprocessing"]["bloom"]

    bloom_threshold = random.uniform(
        bloom_data["threshold_min"], bloom_data["threshold_max"]
    )
    bloom_intensity = random.uniform(
        bloom_data["intensity_min"], bloom_data["intensity_max"]
    )
    bloom_radius = random.uniform(bloom_data["radius_min"], bloom_data["radius_max"])

    bloom_type = "none"
    bloom_types = bloom_data["types"]
    for t in bloom_types.keys():
        if (
            bloom_intensity >= bloom_types[t]["intensity_min"]
            and bloom_intensity <= bloom_types[t]["intensity_max"]
        ):
            bloom_type = t
            break

    postprocessing["bloom"] = {
        "threshold": bloom_threshold,
        "intensity": bloom_intensity,
        "radius": bloom_radius,
        "type": bloom_type,
    }

    ssao_data = camera_data["postprocessing"]["ssao"]
    ssao_distance = random.uniform(ssao_data["distance_min"], ssao_data["distance_max"])
    ssao_factor = random.uniform(ssao_data["factor_min"], ssao_data["factor_max"])

    ssao_type = "none"
    for t in ssao_data["types"].keys():
        if (
            ssao_factor >= ssao_data["types"][t]["factor_min"]
            and ssao_factor <= ssao_data["types"][t]["factor_max"]
        ):
            ssao_type = t
            break

    postprocessing["ssao"] = {
        "distance": ssao_distance,
        "factor": ssao_factor,
        "type": ssao_type,
    }

    ssrr_data = camera_data["postprocessing"]["ssrr"]
    ssrr_max_roughness = random.uniform(
        ssrr_data["min_max_roughness"], ssrr_data["max_max_roughness"]
    )
    ssrr_thickness = random.uniform(
        ssrr_data["min_thickness"], ssrr_data["max_thickness"]
    )

    ssrr_type = "none"
    for t in ssrr_data["types"].keys():
        if (
            ssrr_max_roughness >= ssrr_data["types"][t]["max_roughness_min"]
            and ssrr_max_roughness <= ssrr_data["types"][t]["max_roughness_max"]
        ):
            ssrr_type = t
            break

    postprocessing["ssrr"] = {
        "max_roughness": ssrr_max_roughness,
        "thickness": ssrr_thickness,
        "type": ssrr_type,
    }

    motionblur_data = camera_data["postprocessing"]["motionblur"]
    motionblur_shutter_speed = random.uniform(
        motionblur_data["shutter_speed_min"], motionblur_data["shutter_speed_max"]
    )

    motionblur_type = "none"
    for t in motionblur_data["types"].keys():
        if (
            motionblur_shutter_speed >= motionblur_data["types"][t]["shutter_speed_min"]
            and motionblur_shutter_speed
            <= motionblur_data["types"][t]["shutter_speed_max"]
        ):
            motionblur_type = t
            break

    postprocessing["motionblur"] = {
        "shutter_speed": motionblur_shutter_speed,
        "type": motionblur_type,
    }
    return postprocessing


def generate_orientation(camera_data, objects, background):
    """
    Generate camera orientation based on the camera data, objects, and background.

    Args:
        camera_data (dict): Camera data.
        objects (list): List of objects in the scene.
        background (dict): Background information.

    Returns:
        dict: Camera orientation.
    """
    orientation_data = camera_data["orientation"]

    # Roll a number between orientation['yaw_min'] and orientation['yaw_max']
    yaw = random.randint(orientation_data["yaw_min"], orientation_data["yaw_max"])
    pitch = random.randint(orientation_data["pitch_min"], orientation_data["pitch_max"])

    # Check if the camera is going to be occluded by the objects
    # If so, re-roll the orientation until a non-occluded orientation is found
    while True:
        occluded = False
        for obj in objects[1:]:
            # Calculate the vector from the camera to the object
            # calculate the position of the camera on the unit circle from yaw
            camera_x = math.cos(math.radians(yaw))
            camera_y = math.sin(math.radians(yaw))

            camera_vector = [camera_x, camera_y, 0]

            # get the position of the object
            object_position = obj["transformed_position"]

            # normalize the object position, account for divisino by 0
            object_position = [
                a / max(1e-6, sum([b**2 for b in object_position])) ** 0.5
                for a in object_position
            ]

            # if the magnitude of the object position is 0, ignore it
            if sum([a**2 for a in object_position]) < 0.001:
                continue

            # dot product of the camera vector and the object position
            dot_product = sum([a * b for a, b in zip(camera_vector, object_position)])

            # calculate an angle padding on both sides of the object to use as a threshold
            angle = math.radians(15)
            # set the theshold to the dot product - cos of the angle
            threshold = math.cos(angle)

            if dot_product > threshold:
                occluded = True
                break

        if not occluded:
            break

        # Re-roll the orientation if occluded and try again
        yaw = random.randint(orientation_data["yaw_min"], orientation_data["yaw_max"])
        pitch = random.randint(
            orientation_data["pitch_min"], orientation_data["pitch_max"]
        )

    orientation = {
        "yaw": yaw,
        "pitch": pitch,
    }

    return orientation


def generate_framing(camera_data):
    """
    Generate camera framing based on the camera data.

    Args:
        camera_data (dict): Camera data.

    Returns:
        dict: Camera framing.
    """
    # Get the min_fov and max_fov across all framings
    fov_min = min([f["fov_min"] for f in camera_data["framings"]])
    fov_max = max([f["fov_max"] for f in camera_data["framings"]])

    # Randomly roll an FOV value between FOV_min and FOV_max
    fov = random.uniform(fov_min, fov_max)

    # Find the corresponding framing
    framing = None
    for f in camera_data["framings"]:
        if fov >= f["fov_min"] and fov <= f["fov_max"]:
            framing = f
            break

    # Derive a coverage_factor between coverage_factor_min and coverage_factor_max
    coverage_factor = random.uniform(
        framing["coverage_factor_min"], framing["coverage_factor_max"]
    )

    framing = {
        "fov": fov,
        "coverage_factor": coverage_factor,
        "name": framing["name"],
    }
    return framing


def generate_animation(camera_data):
    """
    Generate camera animation based on the camera data.

    Args:
        camera_data (dict): Camera data.

    Returns:
        dict: Camera animation.
    """
    animation = random.choice(camera_data["animations"])
    animation = animation.copy()
    animation["speed_factor"] = random.uniform(0.5, 2.0)
    animation.pop("descriptions", None)
    print(animation)
    return animation


def generate_objects():
    """
    Generate a list of random objects.

    Returns:
        list: List of generated objects.
    """
    chosen_dataset = random.choices(dataset_names, weights=dataset_weights)[0]

    # Randomly generate max_number_of_objects
    max_number_of_objects = parse_args().max_number_of_objects
    number_of_objects = random.randint(1, max_number_of_objects)

    object_scales = object_data["scales"]

    # "scales": {
    #     "tiny": {
    #         "names": [
    #             "tiny",
    #             "mini",
    #             "miniscule",
    #             "minature",
    #             "petite",
    #             "extra small"
    #         ],
    #         "factor": 0.4
    #     },
    # }

    keys = object_scales.keys()

    objects = []
    positions_taken = set()
    for i in range(number_of_objects):
        object = random.choice(dataset_dict[chosen_dataset])
        scale_key = random.choice(list(keys))
        scale = {
            "factor": object_scales[scale_key]["factor"],
            "name": scale_key,
            "name_synonym": object_scales[scale_key]["names"][
                random.randint(0, len(object_scales[scale_key]["names"]) - 1)
            ],
        }

        placement = 5
        if i > 0:
            placement = random.choice(
                [i for i in range(1, 9) if i not in positions_taken]
            )
        positions_taken.add(placement)

        object = {
            "name": object["name"],
            "uid": object["uid"],
            "description": object["description"],
            "placement": placement,
            "from": chosen_dataset,
            "scale": scale,
        }

        if object["uid"] in captions_data:
            description = captions_data[object["uid"]]
            object["description"] = description

        objects.append(object)

    return objects


def generate_background():
    """
    Generate a random background.

    Returns:
        dict: Generated background.
    """
    chosen_background = random.choices(background_names, weights=background_weights)[0]
    # Get the keys from the chosen background
    background_keys = list(background_dict[chosen_background].keys())
    background_id = random.choice(background_keys)
    bg = background_dict[chosen_background][background_id]

    background = {
        "name": bg["name"],
        "url": bg["url"],
        "id": background_id,
        "from": chosen_background,
    }

    return background


def generate_stage():
    """
    Generate a random stage.

    Returns:
        dict: Generated stage.
    """
    texture_names = list(texture_data.keys())
    texture_weights = [len(texture_data[name]["maps"]) for name in texture_names]
    chosen_texture = random.choices(texture_names, weights=texture_weights)[0]
    maps = texture_data[chosen_texture]["maps"]

    material = {
        "name": texture_data[chosen_texture]["name"],
        "maps": maps,
    }
    stage = {
        "material": material,
        "uv_scale": [random.uniform(0.8, 1.2), random.uniform(0.8, 1.2)],
        "uv_rotation": random.uniform(0, 360),
    }
    return stage


def generate_combinations(camera_data, count, seed):
    """
    Generate random combinations of camera settings, objects, background, and stage.

    Args:
        camera_data (dict): Camera data.
        count (int): Number of combinations to generate.
        seed (int): Seed for the random number generator.

    Returns:
        dict: Generated combinations data.
    """
    if seed is None:
        seed = -1
    random.seed(seed)

    combinations = []

    # Generate combinations on the fly up to the specified count
    for i in range(count):
        objects = generate_objects()
        background = generate_background()

        # Calculate the transformed positions of the objects
        adjusted_objects = adjust_positions(objects, random.randint(0, 360))
        for obj, adjusted_obj in zip(objects, adjusted_objects):
            obj["transformed_position"] = adjusted_obj["transformed_position"]

        orientation = generate_orientation(camera_data, objects, background)

        framing = generate_framing(camera_data)

        postprocessing = generate_postprocessing(camera_data)

        animation = generate_animation(camera_data) # speed is between 0.5 and 2

        stage = generate_stage()

        combination = {
            "index": i,
            "objects": objects,
            "background": background,
            "orientation": orientation,
            "framing": framing,
            "animation": animation,
            "stage": stage,
            "postprocessing": postprocessing,
        }

        combination["caption"] = generate_caption(combination)

        combinations.append(combination)

    data = {"seed": seed, "count": count, "combinations": combinations}

    return data


# Generate combinations
combinations = generate_combinations(camera_data, parse_args().count, parse_args().seed)

# Write to JSON file
with open(parse_args().output_path, "w") as f:
    json.dump(combinations, f, indent=4)

print(f"Combinations have been successfully written to {parse_args().output_path}")
