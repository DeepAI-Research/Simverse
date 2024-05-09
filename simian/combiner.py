import json
import os
import random
import argparse
import re


# Function to read data from a JSON file
def read_json_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


# Setup argparse for command line arguments
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
    "--simdata_path", type=str, default="datasets", help="Path to the simdata directory"
)
parser.add_argument(
    "--output_path",
    type=str,
    default="combinations.json",
    help="Path to the output file",
)
args = parser.parse_args()

# Path to the JSON file
max_number_of_objects = args.max_number_of_objects
camera_data = read_json_file(args.camera_file_path)
captions_data = read_json_file(args.cap3d_captions_path)
object_data = read_json_file(args.object_data_path)
texture_data = read_json_file(args.texture_data_path)
datasets = read_json_file(args.datasets_path)

models = datasets["models"]
backgrounds = datasets["backgrounds"]

background_data = {}
material_data = {}
object_map = {}
category_map = {}
dataset_dict = {}
background_dict = {}


def read_json_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


for dataset in models:
    current_path = os.path.dirname(os.path.realpath(__file__))
    dataset_path = os.path.join(args.simdata_path, dataset + ".json")
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

for background in backgrounds:
    # get the current path of this file
    current_path = os.path.dirname(os.path.realpath(__file__))
    background_path = os.path.join(args.simdata_path, background + ".json")
    background_full_path = os.path.join(current_path, "../", background_path)
    print(f"Loading {background_full_path}")
    if os.path.exists(background_full_path):
        background_data = read_json_file(background_full_path)

        print(f"Loaded {len(background_data)} from {background}")
        background_dict[background] = background_data
    else:
        print(f"Dataset file {background_path} not found")

total_length = 0
for background in background_dict:
    total_length += len(background_dict[background])
print(f"Total number of backgrounds: {total_length}")

# Seed the random number generator for reproducibility
if args.seed is not None:
    random.seed(args.seed)

dataset_names = list(dataset_dict.keys())
dataset_weights = [len(dataset_dict[name]) for name in dataset_names]

background_names = list(background_dict.keys())
background_weights = [len(background_dict[name]) for name in background_names]

texture_names = list(texture_data.keys())
texture_weights = [len(texture_data[name]["maps"]) for name in texture_names]


def generate_caption(combination):
    object_names = [obj["name"] for obj in combination["objects"]]

    background_name = combination["background"]["name"]
    floor_material_name = combination["stage"]["material"]["name"]

    objects = combination["objects"]

    positions_taken = set()

    for object in objects:
        if object == objects[0]:
            object["placement"] = 5
            positions_taken.add(5)
        else:
            object["placement"] = random.choice(
                [i for i in range(1, 9) if i not in positions_taken]
            )
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

    object_name_descriptions = ", ".join(
        [
            obj["name"] + ", " + obj["description"]
            if obj["description"] is not None
            else obj["name"]
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

    # TODO: Omit the background for any angle > 30 degrees
    # omit the floor for any angle < 15 degrees (i.e. 0 to tilted upward)
    # mad libs the background and floor from data

    caption_parts.append(f"The {background_prefix} is {background_name}.")
    caption_parts.append(f"The {floor_prefix} is {floor_material_name}.")

    to_the_left = object_data["relationships"]["to_the_left"]
    to_the_right = object_data["relationships"]["to_the_right"]
    in_front_of = object_data["relationships"]["in_front_of"]
    behind = object_data["relationships"]["behind"]

    relationships = []
    for i, obj1 in enumerate(combination["objects"]):
        for j, obj2 in enumerate(combination["objects"]):
            if i != j:
                row_diff = (obj1["placement"] - 1) // 3 - (obj2["placement"] - 1) // 3
                col_diff = (obj1["placement"] - 1) % 3 - (obj2["placement"] - 1) % 3

                if row_diff == 0 and col_diff == -1:
                    relationships.append(
                        f"{obj1['name']} {random.choice(to_the_left)} {obj2['name']}."
                    )
                    relationships.append(
                        f"{obj2['name']} {random.choice(to_the_right)} {obj1['name']}."
                    )
                elif row_diff == 0 and col_diff == 1:
                    relationships.append(
                        f"{obj1['name']} {random.choice(to_the_right)} {obj2['name']}."
                    )
                    relationships.append(
                        f"{obj2['name']} {random.choice(to_the_left)} {obj1['name']}."
                    )
                elif row_diff == -1 and col_diff == 0:
                    relationships.append(
                        f"{obj1['name']} {random.choice(in_front_of)} {obj2['name']}."
                    )
                    relationships.append(
                        f"{obj2['name']} {random.choice(behind)} {obj1['name']}."
                    )
                elif row_diff == 1 and col_diff == 0:
                    relationships.append(
                        f"{obj1['name']} {random.choice(behind)} {obj2['name']}."
                    )
                    relationships.append(
                        f"{obj2['name']} {random.choice(in_front_of)} {obj1['name']}."
                    )
                elif row_diff == -1 and col_diff == -1:
                    relationships.append(
                        f"{obj1['name']} {random.choice(to_the_left)} and {random.choice(in_front_of)} {obj2['name']}."
                    )
                    relationships.append(
                        f"{obj2['name']} {random.choice(to_the_right)} and {random.choice(behind)} {obj1['name']}."
                    )
                elif row_diff == -1 and col_diff == 1:
                    relationships.append(
                        f"{obj1['name']} {random.choice(to_the_right)} and {random.choice(in_front_of)} {obj2['name']}."
                    )
                    relationships.append(
                        f"{obj2['name']} {random.choice(to_the_left)} and {random.choice(behind)} {obj1['name']}."
                    )
                elif row_diff == 1 and col_diff == -1:
                    relationships.append(
                        f"{obj1['name']} {random.choice(to_the_left)} and {random.choice(behind)} {obj2['name']}."
                    )
                    relationships.append(
                        f"{obj2['name']} {random.choice(to_the_right)} and {random.choice(in_front_of)} {obj1['name']}."
                    )
                elif row_diff == 1 and col_diff == 1:
                    relationships.append(
                        f"{obj1['name']} {random.choice(to_the_right)} and {random.choice(behind)} {obj2['name']}."
                    )
                    relationships.append(
                        f"{obj2['name']} {random.choice(to_the_left)} and {random.choice(in_front_of)} {obj1['name']}."
                    )

    selected_relationships = random.sample(
        relationships, len(combination["objects"]) - 1
    )
    caption_parts.extend(selected_relationships)

    # randomize the caption parts order
    caption_parts = random.sample(caption_parts, len(caption_parts))

    caption = " ".join(caption_parts).replace("..", ".")
    caption = re.sub(r"\.(?=[a-zA-Z])", ". ", caption)

    return caption.strip()


def generate_combinations(camera_data, count):
    combinations = []

    # Generate combinations on the fly up to the specified count
    for i in range(count):
        orientation_data = camera_data["orientation"]

        # roll a number between orientation['yaw_min'] and orientation['yaw_max']
        yaw = random.randint(orientation_data["yaw_min"], orientation_data["yaw_max"])
        pitch = random.randint(orientation_data["pitch_min"], orientation_data["pitch_max"])

        orientation = {
            "yaw": yaw,
            "pitch": pitch,
        }

        framing = random.choice(camera_data["framings"])
        
        # Randomly roll an FOV value between FOV_min and FOV_max
        fov = random.uniform(framing["fov_min"], framing["fov_max"])
        
        # Derive a coverage_factor between coverage_factor_min and coverage_factor_max
        coverage_factor = random.uniform(framing["coverage_factor_min"], framing["coverage_factor_max"])

        animation = random.choice(camera_data["animations"])

        chosen_dataset = random.choices(dataset_names, weights=dataset_weights)[0]

        # randomly generate max_number_of_objects
        number_of_objects = random.randint(1, max_number_of_objects)

        objects = []
        for _ in range(number_of_objects):
            object = random.choice(dataset_dict[chosen_dataset])
            object["from"] = chosen_dataset
            objects.append(object)

        chosen_background = random.choices(background_names, weights=background_weights)[0]
        # get the keys from the chosen background
        background_keys = list(background_dict[chosen_background].keys())
        background_id = random.choice(background_keys)
        background = background_dict[chosen_background][background_id]
        background["id"] = background_id
        background["from"] = chosen_background

        chosen_texture = random.choices(texture_names, weights=texture_weights)[0]

        stage = {
            "material": texture_data[chosen_texture],
            "uv_scale": [random.uniform(0.8, 1.2), random.uniform(0.8, 1.2)],
            "uv_rotation": random.uniform(0, 360),
        }

        combination = {
            "index": i,
            "objects": objects,
            "background": background,
            "orientation": orientation,
            "framing": framing,
            "fov": fov,
            "coverage_factor": coverage_factor,
            "animation": animation,
            "stage": stage,
        }

        caption = generate_caption(combination)
        combination["caption"] = caption

        # remove description from framing, animation and orientation
        framing = framing.copy()
        framing.pop("descriptions", None)

        animation = animation.copy()
        animation.pop("descriptions", None)

        combination["framing"] = framing
        combination["animation"] = animation

        combinations.append(combination)

    return combinations


# Generate combinations
combinations = generate_combinations(camera_data, args.count)

# Write to JSON file
with open(args.output_path, "w") as f:
    json.dump(combinations, f, indent=4)

print(f"Combinations have been successfully written to {args.output_path}")
