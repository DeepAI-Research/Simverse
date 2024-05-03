import json
import os
import random
import argparse

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
parser.add_argument('--max_number_of_objects', type=int, default=3, help='Maximum number of objects to randomly select')
args = parser.parse_args()

# Path to the JSON file
camera_file_path = args.camera_file_path

max_number_of_objects = args.max_number_of_objects

# Load the data
camera_data = read_json_file(camera_file_path)

background_data = {}

object_map = {}
category_map = {}

dataset_dict = {}
background_dict = {}
# TODO: This is slow!
for dataset in datasets:
    # get the current path of this file
    current_path = os.path.dirname(os.path.realpath(__file__))
    dataset_path = os.path.join('datasets', dataset + '.json')
    dataset_full_path = os.path.join(current_path, '../', dataset_path)
    print(f"Loading {dataset_full_path}")
    if os.path.exists(dataset_full_path):
        dataset_data = read_json_file(dataset_full_path)
        local_count = 0
        
        # TODO: SLOW
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
    
# Seed the random number generator for reproducibility
if args.seed is not None:
    random.seed(args.seed)

dataset_names = list(dataset_dict.keys())
dataset_weights = [len(dataset_dict[name]) for name in dataset_names]

background_names = list(background_dict.keys())
background_weights = [len(background_dict[name]) for name in background_names]
    
def generate_combinations(camera_data, count):
    combinations = []
    
    # Generate combinations on the fly up to the specified count
    for _ in range(count):
        orientation = random.choice(camera_data['orientations'])
        framing = random.choice(camera_data['framings'])
        animation = random.choice(camera_data['animations'])
        
        chosen_dataset = random.choices(dataset_names, weights=dataset_weights)[0]
        
        # randomly generate max_number_of_objects
        number_of_objects = random.randint(1, max_number_of_objects)
        
        objects = []
        for _ in range(number_of_objects):
            object = random.choice(dataset_dict[chosen_dataset])
            objects.append(object)
        
        chosen_background = random.choices(background_names, weights=background_weights)[0]
        # get the keys from the chosen background
        background_keys = list(background_dict[chosen_background].keys())        
        background_id = random.choice(background_keys)
        background = background_dict[chosen_background][background_id]
        background['id'] = background_id
        background['from'] = chosen_background
        object['from'] = chosen_dataset
        combination = {
            'object': object,
            'background': background,
            'orientation': orientation,
            'framing': framing,
            'animation': animation
        }
        combinations.append(combination)

    return combinations

# Generate combinations
combinations = generate_combinations(camera_data, args.count)

# Write to JSON file
with open('combinations.json', 'w') as f:
    json.dump(combinations, f, indent=4)

print("Combinations have been successfully written to combinations.json")
