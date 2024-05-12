import json
import os
import random
import argparse
import re
from simian.transform import determine_relationships, adjust_positions


def read_json_file(file_path):
    """
    Read a JSON file and return the data as a dictionary.
    """
    with open(file_path, "r") as file:
        return json.load(file)


# Setup argparse for command line arguments
def parse_args():
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


def generate_caption(combination):
    background_name = combination["background"]["name"]
    floor_material_name = combination["stage"]["material"]["name"]

    objects = combination["objects"]

    positions_taken = set()

    for object in objects:
        if object == objects[0]:
            object["placement"] = 4
            positions_taken.add(4)
        else:
            rand_placement = [i for i in range(0, 9) if i not in positions_taken]
            object["placement"] = random.choice(rand_placement)
            positions_taken.add(rand_placement[0])

        object_id = object["uid"]

        object_scales = object_data["scales"]

        keys = object_scales.keys()
        # choose a key randomly
        scale_key = random.choice(list(keys))

        object["scale"] = {
            "factor": object_scales[scale_key]["factor"] * random.uniform(0.9, 1.0),
            "name": scale_key,
            "name_synonym": object_scales[scale_key]["names"][
                random.randint(0, len(object_scales[scale_key]["names"]) - 1)
            ],
        }

        if object_id in captions_data:
            description = captions_data[object_id]
            object["description"] = description

    caption_parts = []

    ", ".join(
        [
            (
                obj["name"] + ", " + obj["description"]
                if obj["description"] is not None
                else obj["name"]
            )
            for obj in combination["objects"]
        ]
    )

    object_descriptions = []

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
        object_descriptions.append(object_name_description_relationship)

    # randomize order of object_descriptions
    random.shuffle(object_descriptions)
    # join the object descriptions
    object_descriptions = " ".join(object_descriptions)
    caption_parts.append(object_descriptions)

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
    caption_parts.append(orientation_text)

    # TODO: Add DOF to caption

    # TODO: Add framing to caption

    # TODO: Add postprocessing to caption

    # framing_text = random.choice(camera_data["framing"]["descriptions"])
    # framing_text = framing_text.replace("<objects>", object_names)
    # caption_parts.append(framing_text)
    stage_data = read_json_file("data/stage_data.json")

    background_prefix = random.choice(stage_data["background_names"])
    floor_prefix = random.choice(stage_data["material_names"])

    # remove all numbers and trim
    floor_material_name = "".join(
        [i for i in floor_material_name if not i.isdigit()]
    ).strip()
    background_name = "".join([i for i in background_name if not i.isdigit()]).strip()

    caption_parts.append(f"The {background_prefix} is {background_name}.")
    caption_parts.append(f"The {floor_prefix} is {floor_material_name}.")

    THRESHOLD_RELATIONSHIPS = len(combination["objects"])

    adjusted_objects = adjust_positions(
        combination["objects"], combination["orientation"]["yaw"]
    )
    relationships = determine_relationships(adjusted_objects, object_data)

    # write relationships into the json file with combination["objects"]["relationships"]
    # TODO: This code is bad
    for i, obj in enumerate(combination["objects"]):
        # TODO: Added this but we probably need to check if the object has a relationships key
        if i < len(relationships):
            obj["relationships"] = relationships[i]

    selected_relationships = []  # Initialize it as an empty list

    if THRESHOLD_RELATIONSHIPS != 1:
        selected_relationships = random.sample(relationships, THRESHOLD_RELATIONSHIPS)

    caption_parts.extend(selected_relationships)

    # randomize the caption parts order
    caption_parts = random.sample(caption_parts, len(caption_parts))

    caption = " ".join(caption_parts).replace("..", ".")
    caption = re.sub(r"\.(?=[a-zA-Z])", ". ", caption)

    return caption.strip()


def generate_postprocessing(camera_data):
    postprocessing = {}

    bloom_data = camera_data["postprocessing"]["bloom"]
    # TODO: Generate post processing
    bloom_threshold = random.uniform(
        bloom_data["threshold_min"], bloom_data["threshold_max"]
    )
    bloom_intensity = random.uniform(
        bloom_data["intensity_min"], bloom_data["intensity_max"]
    )
    bloom_radius = random.uniform(bloom_data["radius_min"], bloom_data["radius_max"])

    # get the type from bloom_data["types"] and the description from bloom_data["types"]<type>["descriptions"] which corresponds to the intensity we rolled
    # iterate bloom_data["types"] and find the entry where intensity_min <= bloom_intensity <= intensity_max
    bloom_type = "none"
    bloom_types = bloom_data["types"]
    # bloom_data["types"] are objects, get the keys
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


def generate_orientation(camera_data):
    orientation_data = camera_data["orientation"]

    # roll a number between orientation['yaw_min'] and orientation['yaw_max']
    yaw = random.randint(orientation_data["yaw_min"], orientation_data["yaw_max"])
    pitch = random.randint(orientation_data["pitch_min"], orientation_data["pitch_max"])

    # TODO: check if the camera is going to be occluded by the object
    # if so, re-roll the orientation

    # first, get the object positions for all objects that are not the first object in 0,0
    # then compute the vector from 0,0 to object pos
    # to get the arc angle, we need to get the bounding sphere of the object
    # calculate the angle between the vector and the bounding sphere
    # use this as the epsilon for the occlusion check
    # if the value of the normalized vector to the camera is dot product with the normalized vector to the object is greater than the epsilon, then the object is occluding the camera
    # re-roll the orientation if this is the case

    orientation = {
        "yaw": yaw,
        "pitch": pitch,
    }

    return orientation


def generate_framing(camera_data):
    # get the min_fov and max_fov across all framings
    fov_min = min([f["fov_min"] for f in camera_data["framings"]])
    fov_max = max([f["fov_max"] for f in camera_data["framings"]])

    # Randomly roll an FOV value between FOV_min and FOV_max
    fov = random.uniform(fov_min, fov_max)

    # find the corresponding framing
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
    animation = random.choice(camera_data["animations"])
    animation = animation.copy()
    animation.pop("descriptions", None)
    return animation


def generate_objects():
    chosen_dataset = random.choices(dataset_names, weights=dataset_weights)[0]

    # randomly generate max_number_of_objects
    max_number_of_objects = parse_args().max_number_of_objects
    number_of_objects = random.randint(1, max_number_of_objects)

    object_scales = object_data["scales"]
    keys = object_scales.keys()

    objects = []
    positions_taken = set()
    for _ in range(number_of_objects):
        object = random.choice(dataset_dict[chosen_dataset])
        scale_key = random.choice(list(keys))
        scale = {
            "factor": object_scales[scale_key]["factor"] * random.uniform(0.9, 1.0),
            "name": scale_key,
            "name_synonym": object_scales[scale_key]["names"][
                random.randint(0, len(object_scales[scale_key]["names"]) - 1)
            ],
        }

        object = {
            "name": object["name"],
            "uid": object["uid"],
            "description": object["description"],
            "placement": len(objects) == 0
            and 5
            or random.choice([i for i in range(1, 9) if i not in positions_taken]),
            "from": chosen_dataset,
            "scale": scale,
        }

        if object_id in captions_data:
            description = captions_data[object_id]
            object["description"] = description

        objects.append(object)

    return objects


def generate_background():
    chosen_background = random.choices(background_names, weights=background_weights)[0]
    # get the keys from the chosen background
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
    if seed is not None:
        random.seed(seed)

    combinations = []

    # Generate combinations on the fly up to the specified count
    for i in range(count):
        orientation = generate_orientation(camera_data)

        framing = generate_framing(camera_data)

        postprocessing = generate_postprocessing(camera_data)

        animation = generate_animation(camera_data)

        objects = generate_objects()

        background = generate_background()

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
