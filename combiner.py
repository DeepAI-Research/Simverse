import json
import random
import argparse

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
        
        combination = {
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
