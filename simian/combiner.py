import json
import os
import random
import argparse
import re

datasets = [
    "animals-pets",
    "cars-vehicles",
    "characters-creatures",
    "electronics-gadgets",
    "fashion-style",
    "food-drink",
    "furniture-home",
    "music",
    "nature-plants",
    "news-politics",
    "people",
    "science-technology",
    "sports-fitness",
    "weapons-military"
]

backgrounds = ["hdri_urls"]

# Function to read data from a JSON file
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Setup argparse for command line arguments
parser = argparse.ArgumentParser(description='Generate random camera combinations.')
parser.add_argument('--count', type=int, default=10, help='Number of combinations to generate')
parser.add_argument('--seed', type=int, default=None, help='Seed for the random number generator')
parser.add_argument('--camera_file_path', type=str, default='data/camera_data.json', help='Path to the JSON file containing camera data')
parser.add_argument('--max_number_of_objects', type=int, default=5, help='Maximum number of objects to randomly select')
args = parser.parse_args()

# Path to the JSON file
camera_file_path = args.camera_file_path

max_number_of_objects = args.max_number_of_objects

# Load the data
camera_data = read_json_file(camera_file_path)

background_data = {}
material_data = {}
object_map = {}
category_map = {}
dataset_dict = {}
background_dict = {}

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

captions_file_path = 'datasets/cap3d_captions.json'
captions_data = read_json_file(captions_file_path)

for dataset in datasets:
    current_path = os.path.dirname(os.path.realpath(__file__))
    dataset_path = os.path.join('datasets', dataset + '.json')
    dataset_full_path = os.path.join(current_path, '../', dataset_path)
    print(f"Loading {dataset_full_path}")
    if os.path.exists(dataset_full_path):
        dataset_data = read_json_file(dataset_full_path)
        local_count = 0
        
        for object in dataset_data:
            object_id = object['uid']
            categories = object['categories']
            
            if object_id not in object_map:
                object_map[object_id] = object
                local_count += 1
            
            for category in categories:
                if category not in category_map:
                    category_map[category] = set()
                category_map[category].add(object_id)
        
        print(f"Loaded {local_count} unique entries out of {len(dataset_data)} from {dataset}")
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
    background_path = os.path.join('datasets', background + '.json')
    background_full_path = os.path.join(current_path, '../', background_path)
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


# load material_data
texture_data = read_json_file('datasets/texture_data.json')

# Seed the random number generator for reproducibility
if args.seed is not None:
    random.seed(args.seed)

dataset_names = list(dataset_dict.keys())
dataset_weights = [len(dataset_dict[name]) for name in dataset_names]

background_names = list(background_dict.keys())
background_weights = [len(background_dict[name]) for name in background_names]

texture_names = list(texture_data.keys())
texture_weights = [len(texture_data[name]['maps']) for name in texture_names]

def generate_caption(combination):
    object_names = [obj['name'] for obj in combination['objects']]

    background_name = combination["background"]["name"]
    floor_material_name = combination["stage"]["material"]["name"]

    camera_data = random.choice(["descriptions", "instructions"])
    camera_text = random.choice(combination["orientation"][camera_data])

    objects = combination["objects"]
    
    positions_taken = set()
    
    for object in objects:        
        if object == objects[0]:
            object['placement'] = 5
            positions_taken.add(5)
        else:
            object['placement'] = random.choice([i for i in range(1, 9) if i not in positions_taken])
        object_id = object["uid"]
        
        position_offset = [random.uniform(-0.3, 0.3), random.uniform(-0.1, 0.1), 0]
        rotation_offset = [random.uniform(-3, 3), random.uniform(-3, 3), 0]

        object["position_offset"] = position_offset
        object["rotation_offset"] = rotation_offset
        
        # read in from ./data/object_data.json
        object_data = read_json_file('data/object_data.json')
        
        object_scales = object_data["scales"]
        
        keys = object_scales.keys()
        # choose a key randomly
        scale_key = random.choice(list(keys))
        object["distance_modifier"] = random.uniform(1.6, 2.2)
        object["scale"] = {
            "factor": object_scales[scale_key]["factor"] * random.uniform(0.9, 1.0),
            "name": scale_key,
            "name_synonym": object_scales[scale_key]["names"][random.randint(0, len(object_scales[scale_key]["names"]) - 1)]
        }
        if object_id in captions_data:
            description = captions_data[object_id]
            object['description'] = description


    object_name_prefixes = object_data["name_prefixes"]
    object_name_suffixes = object_data["name_suffixes"]
    
    random_object_name_prefix = random.choice(object_name_prefixes)
    random_object_name_suffix = random.choice(object_name_suffixes)

    # join all of the names of the objects together
    object_names = ', '.join([obj['name'] for obj in combination['objects']])
    object_descriptions = ', '.join(obj['description'] if not None else "" for obj in combination['objects'])
    object_name_descriptions = ', '.join([obj['name'] + ", " + obj['description'] if obj['description'] is not None else obj['name'] for obj in combination['objects']])

    if "<objects>" not in camera_text:
        # at least one <objects> gets added to the camera text
        camera_text = camera_text.strip() + " " + random_object_name_prefix
    # replace the first <objects> with the object names
    camera_text = camera_text.replace("<objects>", object_name_descriptions, 1)
    # replace the rest of the <objects> with the object name suffix
    camera_text = camera_text.replace("<objects>", random_object_name_suffix)
   
    framing_data = random.choice(["descriptions", "instructions"])
    framing_text = random.choice(combination["framing"][framing_data])
    framing_text = framing_text.replace("<objects>", object_names)

    caption_parts = [camera_text, framing_text]
    
    stage_data = read_json_file('data/stage_data.json')
    
    floor_material_names = stage_data["material_names"]
    
    background_names = stage_data["background_names"]
    
    background_prefix = random.choice(background_names)
    floor_prefix = random.choice(floor_material_names)
    
    # remove all numbers and trim
    floor_material_name = ''.join([i for i in floor_material_name if not i.isdigit()]).strip()
    background_name = ''.join([i for i in background_name if not i.isdigit()]).strip()

    if random.random() < 0.3:
        caption_parts.append(f"The {background_prefix} is {background_name}.")

    if random.random() < 0.2:
        caption_parts.append(f"The {floor_prefix} is {floor_material_name}.")
    
    to_the_left = object_data["relationships"]["to_the_left"]
    to_the_right = object_data["relationships"]["to_the_right"]
    in_front_of = object_data["relationships"]["in_front_of"]
    behind = object_data["relationships"]["behind"]
    
    relationships = []
    for i, obj1 in enumerate(combination['objects']):
        for j, obj2 in enumerate(combination['objects']):
            if i != j:
                row_diff = (obj1['placement'] - 1) // 3 - (obj2['placement'] - 1) // 3
                col_diff = (obj1['placement'] - 1) % 3 - (obj2['placement'] - 1) % 3
                
                if row_diff == 0 and col_diff == -1:
                    relationships.append(f"{obj1['name']} {random.choice(to_the_left)} {obj2['name']}.")
                    relationships.append(f"{obj2['name']} {random.choice(to_the_right)} {obj1['name']}.")
                elif row_diff == 0 and col_diff == 1:
                    relationships.append(f"{obj1['name']} {random.choice(to_the_right)} {obj2['name']}.")
                    relationships.append(f"{obj2['name']} {random.choice(to_the_left)} {obj1['name']}.")
                elif row_diff == -1 and col_diff == 0:
                    relationships.append(f"{obj1['name']} {random.choice(in_front_of)} {obj2['name']}.")
                    relationships.append(f"{obj2['name']} {random.choice(behind)} {obj1['name']}.")
                elif row_diff == 1 and col_diff == 0:
                    relationships.append(f"{obj1['name']} {random.choice(behind)} {obj2['name']}.")
                    relationships.append(f"{obj2['name']} {random.choice(in_front_of)} {obj1['name']}.")
                elif row_diff == -1 and col_diff == -1:
                    relationships.append(f"{obj1['name']} {random.choice(to_the_left)} and {random.choice(in_front_of)} {obj2['name']}.")
                    relationships.append(f"{obj2['name']} {random.choice(to_the_right)} and {random.choice(behind)} {obj1['name']}.")
                elif row_diff == -1 and col_diff == 1:
                    relationships.append(f"{obj1['name']} {random.choice(to_the_right)} and {random.choice(in_front_of)} {obj2['name']}.")
                    relationships.append(f"{obj2['name']} {random.choice(to_the_left)} and {random.choice(behind)} {obj1['name']}.")
                elif row_diff == 1 and col_diff == -1:
                    relationships.append(f"{obj1['name']} {random.choice(to_the_left)} and {random.choice(behind)} {obj2['name']}.")
                    relationships.append(f"{obj2['name']} {random.choice(to_the_right)} and {random.choice(in_front_of)} {obj1['name']}.")
                elif row_diff == 1 and col_diff == 1:
                    relationships.append(f"{obj1['name']} {random.choice(to_the_right)} and {random.choice(behind)} {obj2['name']}.")
                    relationships.append(f"{obj2['name']} {random.choice(to_the_left)} and {random.choice(in_front_of)} {obj1['name']}.")
    
    selected_relationships = random.sample(relationships, len(combination['objects']) - 1)
    caption_parts.extend(selected_relationships)

    # randomize the caption parts order
    caption_parts = random.sample(caption_parts, len(caption_parts))
    
    caption = " ".join(caption_parts).replace('..', '.')
    caption = re.sub(r'\.(?=[a-zA-Z])', '. ', caption)

    return caption.strip()

def generate_combinations(camera_data, count):
    combinations = []
    
    # Generate combinations on the fly up to the specified count
    for i in range(count):
        orientation = random.choice(camera_data['orientations'])
        framing = random.choice(camera_data['framings'])
        animation = random.choice(camera_data['animations'])
        
        chosen_dataset = random.choices(dataset_names, weights=dataset_weights)[0]
        
        # randomly generate max_number_of_objects
        number_of_objects = random.randint(1, max_number_of_objects)
        
        objects = []
        for _ in range(number_of_objects):
            object = random.choice(dataset_dict[chosen_dataset])
            object['from'] = chosen_dataset
            objects.append(object)
        
        chosen_background = random.choices(background_names, weights=background_weights)[0]
        # get the keys from the chosen background
        background_keys = list(background_dict[chosen_background].keys())        
        background_id = random.choice(background_keys)
        background = background_dict[chosen_background][background_id]
        background['id'] = background_id
        background['from'] = chosen_background
        
        chosen_texture = random.choices(texture_names, weights=texture_weights)[0]
        
        framing["position_offset"] = [random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)]
        framing["rotation_offset"] = [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)]
        orientation["position_offset"] = [random.uniform(-0.1, 0.1), random.uniform(-.1, 0.1), 0]
        orientation["rotation_offset"] = [random.uniform(-1, 1), random.uniform(-1, 1), 0]
        
        stage = {
            'material': texture_data[chosen_texture],
            'uv_scale': [random.uniform(0.8, 1.2), random.uniform(0.8, 1.2)],
            'uv_rotation': random.uniform(0, 360),
        }
        
        combination = {
            'index': i,
            'objects': objects,
            'background': background,
            'orientation': orientation,
            'framing': framing,
            'animation': animation,
            'stage': stage,
        }
        
        caption = generate_caption(combination)
        combination['caption'] = caption
        
        # remove description and instructions from framing, animation and orientation
        framing = framing.copy()
        
        framing.pop("descriptions", None)
        framing.pop("instructions", None)
        
        orientation = orientation.copy()
        orientation.pop("descriptions", None)    
        orientation.pop("instructions", None)
        
        animation = animation.copy()
        animation.pop("descriptions", None)
        animation.pop("instructions", None)
        
        combination["orientation"] = orientation
        combination["framing"] = framing
        combination["animation"] = animation
        
        combinations.append(combination)

    return combinations

# Generate combinations
combinations = generate_combinations(camera_data, args.count)

# Write to JSON file
with open('combinations.json', 'w') as f:
    json.dump(combinations, f, indent=4)

print("Combinations have been successfully written to combinations.json")
