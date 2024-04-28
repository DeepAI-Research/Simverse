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

# example of the structure one of these JSON files:
# [
    # {
    #     "uid": "2b3b6a5abe784dfe816fec5bf62542c2",
    #     "name": "Pots the Raccoon",
    #     "categories": [
    #         "animals-pets",
    #         "nature-plants"
    #     ],
    #     "description": "My attempt to make an original character in the style of Animal Crossing. Her name is Pots, a business raccoon only interested in one kind of business: GORBAGE!",
    #     "tags": [
    #         "pot",
    #         "raccoon",
    #         "garbage",
    #         "animalcrossing",
    #         "pothead",
    #         "animal"
    #     ]
    # }
# ]


# Function to read data from a JSON file
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Setup argparse for command line arguments
parser = argparse.ArgumentParser(description='Generate random camera combinations.')
parser.add_argument('--count', type=int, default=10, help='Number of combinations to generate')
parser.add_argument('--seed', type=int, default=None, help='Seed for the random number generator')
args = parser.parse_args()

# Path to the JSON file
file_path = 'ingredients.json'

# Load the data
data = read_json_file(file_path)
camera_data = data['camera']

object_map = {}
category_map = {}

dataset_dict = {}
# TODO: This is slow!
for dataset in datasets:
    # get the current path of this file
    current_path = os.path.dirname(os.path.realpath(__file__))
    dataset_path = os.path.join('datasets', dataset + '.json')
    dataset_full_path = os.path.join(current_path, dataset_path)
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
print(f"Total length of all entries: {total_length}")
    
# Seed the random number generator for reproducibility
if args.seed is not None:
    random.seed(args.seed)

def generate_combinations(camera_data, count):
    combinations = []

    # Generate combinations on the fly up to the specified count
    for _ in range(count):
        orientation = random.choice(camera_data['orientations'])
        framing = random.choice(camera_data['framings'])
        print('framing')
        print(framing)
        animation = random.choice(camera_data['animations'])
        
        description = (
            f"{random.choice(orientation['descriptions'])}. "
            f"{random.choice(framing['descriptions'])}. "
            f"{random.choice(animation['descriptions'])}."
        )
        
        instruction = (
            f"{random.choice(orientation['instructions'])}. "
            f"{random.choice(framing['instructions'])}. "
            f"{random.choice(animation['instructions'])}."
        )
        
        dataset_names = list(dataset_dict.keys())
        dataset_weights = [len(dataset_dict[name]) for name in dataset_names]
        chosen_dataset = random.choices(dataset_names, weights=dataset_weights)[0]
        object = random.choice(dataset_dict[chosen_dataset])
        print('object')
        print(object)
        
        combination = {
            'object': object,
            'from': chosen_dataset,
            'orientation': {
                'name': orientation['name'],
                'yaw': orientation['yaw'],
                'pitch': orientation['pitch'],
                'description': random.choice(orientation['descriptions']),
                'instruction': random.choice(orientation['instructions'])
            },
            'framing': {
                'name': framing['name'],
                'fov': framing['fov'],
                'distance': framing['distance'],
                'description': random.choice(framing['descriptions']),
                'instruction': random.choice(framing['instructions'])
            },
            'animation': {
                'name': animation['name'],
                'description': random.choice(animation['descriptions']),
                'instruction': random.choice(animation['instructions'])
            },
            'description': description,
            'instruction': instruction
        }
        combinations.append(combination)

    return combinations

# Generate combinations
combinations = generate_combinations(camera_data, args.count)

# Write to JSON file
with open('combinations.json', 'w') as f:
    json.dump(combinations, f, indent=4)

print("Combinations have been successfully written to combinations.json")
