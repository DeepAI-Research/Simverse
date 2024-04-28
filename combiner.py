import json
import os
import random
import argparse

datasets = [
    "animals-pets.json",
    "cars-vehicles.json",
    "characters-creatures.json",
    "electronics-gadgets.json",
    "fashion-style.json",
    "food-drink.json",
    "furniture-home.json",
    "music.json",
    "nature-plants.json",
    "news-politics.json",
    "people.json",
    "science-technology.json",
    "sports-fitness.json",
    "weapons-military.json"
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

# TODO: load the datasets into a dictionary of lists keyed by the dataset name
# Our goal is to randomly get one of the entries, weighted by the length of that dataset so that we don't overrepresent one dataset with less entries over another with more entries

dataset_dict = {}
for dataset in datasets:
    # get the current path of this file
    current_path = os.path.dirname(os.path.realpath(__file__))
    dataset_path = os.path.join('datasets', dataset)
    dataset_full_path = os.path.join(current_path, dataset_path)
    print(f"Loading {dataset_full_path}")
    if os.path.exists(dataset_full_path):
        dataset_data = read_json_file(dataset_full_path)
        # print the length of dataset_data
        print(f"Loaded {len(dataset_data)} entries from {dataset}")
        dataset_dict[dataset] = dataset_data
    else:
        print(f"Dataset file {dataset_path} not found")
    
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
        
        # TODO: get a random entry from the datasets dictionary
        # and add it to the combination
        # also add a "from" field to the combination to indicate which dataset the entry came from
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
                'description': random.choice(orientation['descriptions']),
                'instruction': random.choice(orientation['instructions'])
            },
            'framing': {
                'name': framing['name'],
                'fov': framing['fov'],
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
