# import json
# import re
# import os
# import random
# import argparse
# from typing import List, Dict, Tuple, Optional, Any, Set


# datasets = [
#     "animals-pets", "cars-vehicles", "characters-creatures",
#     "electronics-gadgets", "fashion-style", "food-drink",
#     "furniture-home", "music", "nature-plants",
#     "news-politics", "people", "science-technology",
#     "sports-fitness", "weapons-military"
# ]
# backgrounds = ["hdri_data"]


# def read_json_file(file_path: str) -> Dict:
#     """
#     Reads a JSON file and returns its contents as a dictionary.

#     Args:
#         file_path (str): Path to the JSON file.

#     Returns:
#         Dict: Parsed JSON file as a dictionary.
#     """
#     with open(file_path, 'r') as file:
#         return json.load(file)


# # Setup argparse for command line arguments
# parser = argparse.ArgumentParser(description='Generate random camera combinations.')
# parser.add_argument('--count', type=int, default=10, help='Number of combinations to generate')
# parser.add_argument('--seed', type=int, default=None, help='Seed for the random number generator')
# parser.add_argument('--camera_file_path', type=str, default='data/camera_data.json', help='Path to the JSON file containing camera data')
# parser.add_argument('--max_number_of_objects', type=int, default=5, help='Maximum number of objects to randomly select')
# args = parser.parse_args()

# # Path to the JSON file
# camera_file_path = args.camera_file_path

# # Assign the maximum number of objects to be used in each combination from the command line argument
# max_number_of_objects = args.max_number_of_objects

# # Load the data
# camera_data = read_json_file(camera_file_path)

# # Holds data loaded from background JSON files.
# background_data: Dict[str, Any] = {}

# # Holds material data, possibly loaded from JSON files.
# material_data: Dict[str, Any] = {}

# # Maps object IDs to object data.
# object_map: Dict[str, Any] = {}

# # Maps category names to sets of object IDs.
# category_map: Dict[str, Set[str]] = {}

# # Holds data for each dataset, where each dataset name maps to a list of objects.
# dataset_dict: Dict[str, List[Dict[str, Any]]] = {}

# # Holds data for each background, where each background name maps to its details.
# background_dict: Dict[str, Dict[str, Any]] = {}


# def read_json_file(file_path: str) -> Dict:
#     """
#     Reads a JSON file and returns its contents as a dictionary.

#     Args:
#         file_path (str): Path to the JSON file.

#     Returns:
#         Dict: Parsed JSON file as a dictionary.
#     """
#     with open(file_path, 'r') as file:
#         return json.load(file)


# captions_file_path = 'datasets/cap3d_captions.json'
# captions_data = read_json_file(captions_file_path)

# # Iterate over each dataset listed in the datasets array
# for dataset in datasets:
#     # Get the current script directory to construct the full path to the dataset file
#     current_path = os.path.dirname(os.path.realpath(__file__))
#     # Construct the relative path to the dataset JSON file
#     dataset_path = os.path.join('datasets', dataset + '.json')
#     # Create the full path to the dataset JSON file
#     dataset_full_path = os.path.join(current_path, '../', dataset_path)
#     # Output the dataset file being loaded for user feedback
#     print(f"Loading {dataset_full_path}")

#     # Check if the dataset file exists at the specified path
#     if os.path.exists(dataset_full_path):
#         # Load the dataset data from the JSON file
#         dataset_data = read_json_file(dataset_full_path)
#         # Initialize a counter to keep track of unique objects loaded
#         local_count = 0
        
#         # Iterate through each object in the dataset
#         for object in dataset_data:
#             object_id = object['uid']  # Unique identifier of the object
#             categories = object['categories']  # Categories that the object belongs to
            
#             # Check if the object_id is not already in the object_map
#             if object_id not in object_map:
#                 # Add the object to the map and increment the unique counter
#                 object_map[object_id] = object
#                 local_count += 1
            
#             # Iterate through each category the object belongs to
#             for category in categories:
#                 # If the category hasn't been seen before, initialize it in the category_map
#                 if category not in category_map:
#                     category_map[category] = set()
#                 # Add the object ID to the set of objects associated with this category
#                 category_map[category].add(object_id)
        
#         # After loading all objects, report how many unique entries were loaded
#         print(f"Loaded {local_count} unique entries out of {len(dataset_data)} from {dataset}")
#         # Store the entire dataset data in a dictionary keyed by the dataset name
#         dataset_dict[dataset] = dataset_data
#     else:
#         # If the dataset file does not exist, report it as not found
#         print(f"Dataset file {dataset_path} not found")

# # Count the total length of all entries
# total_length = 0
# for dataset in dataset_dict:
#     total_length += len(dataset_dict[dataset])
# print(f"Total number of objects: {total_length}")     

# for background in backgrounds:
#     # Get the current path of this file
#     current_path = os.path.dirname(os.path.realpath(__file__))
#     background_path = os.path.join('datasets', background + '.json')
#     background_full_path = os.path.join(current_path, '../', background_path)
#     print(f"Loading {background_full_path}")
#     if os.path.exists(background_full_path):
#         background_data = read_json_file(background_full_path)
        
#         print(f"Loaded {len(background_data)} from {background}")
#         background_dict[background] = background_data
#     else:
#         print(f"Dataset file {background_path} not found")
        
# total_length = 0
# for background in background_dict:
#     total_length += len(background_dict[background])
# print(f"Total number of backgrounds: {total_length}")

# # Load material_data
# texture_data = read_json_file('datasets/texture_data.json')

# # Seed the random number generator for reproducibility
# if args.seed is not None:
#     random.seed(args.seed)


# def extract_names_and_weights(data_dict: dict, count_key: Optional[str] = None) -> Tuple[List[str], List[int]]:
#     """
#     Extracts names and their corresponding weights from a dictionary.
#     The weights are determined by the length of the list in each entry or by the length of a specified sub-key.

#     Args:
#         - data_dict (dict): The dictionary from which to extract data.
#         - count_key (str, optional): The sub-key to use for counting weights. Defaults to None.

#     Returns:
#         Tuple[List[str], List[int]]: A tuple containing two lists: names and corresponding weights.
#     """
#     names = list(data_dict.keys())
#     if count_key:
#         weights = [len(data_dict[name][count_key]) for name in names]
#     else:
#         weights = [len(data_dict[name]) for name in names]
#     return names, weights


# # Use the function to get names and weights
# dataset_names, dataset_weights = extract_names_and_weights(dataset_dict)
# background_names, background_weights = extract_names_and_weights(background_dict)
# texture_names, texture_weights = extract_names_and_weights(texture_data, 'maps')


# def generate_caption(combination: dict) -> str:
#     """
#     Generates a descriptive caption based on the combination of scene elements provided.

#     This function constructs a narrative description by combining information about the objects,
#     their spatial arrangement, background settings, and additional metadata such as textures
#     and materials. It uses randomness to select specific descriptions and to arrange these
#     elements in a variable order, ensuring that each generated caption is unique. The caption
#     integrates detailed descriptions of object placements, background and floor characteristics,
#     and dynamic relationships among the objects based on their positions.

#     Args:
#         combination (dict): A dictionary containing all elements of the scene, including objects,
#                             backgrounds, orientations, and other settings that contribute to the
#                             final scene composition.

#     Returns:
#         str: A string that provides a coherent narrative description of the scene, integrating
#              various elements of the combination in a human-readable format.
#     """
        
#     # Extract object names from the combination's object list
#     object_names = [obj['name'] for obj in combination['objects']]

#     # Retrieve names for background and floor material from the combination
#     background_name = combination["background"]["name"]
#     floor_material_name = combination["stage"]["material"]["name"]

#     # Randomly choose between descriptions or instructions for camera orientation text
#     camera_data = random.choice(["descriptions", "instructions"])
#     camera_text = random.choice(combination["orientation"][camera_data])

#     # A list of objects from the combination to place in the scene
#     objects = combination["objects"]
    
#     # A set to track positions already taken to avoid overlap
#     positions_taken = set()
    
#     # Loop through each object to set their placement, position, and rotation offsets
#     for object in combination['objects']:        
#         if object == objects[0]:  # Assign a fixed position to the first object for consistency
#             object['placement'] = 5
#             positions_taken.add(5)
#         else:  # For other objects, choose a random position that's not already taken
#             object['placement'] = random.choice([i for i in range(1, 9) if i not in positions_taken])

#         # Generate random position and rotation offsets for each object
#         position_offset = [random.uniform(-0.3, 0.3), random.uniform(-0.1, 0.1), 0]
#         rotation_offset = [random.uniform(-3, 3), random.uniform(-3, 3), 0]
#         object["position_offset"] = position_offset
#         object["rotation_offset"] = rotation_offset
        
#         # Load object scale data from an external JSON file
#         object_data = read_json_file('data/object_data.json')
#         object_scales = object_data["scales"]
#         scale_key = random.choice(list(object_scales.keys()))  # Randomly select a scale key
#         object["distance_modifier"] = random.uniform(1.6, 2.2)
#         object["scale"] = {
#             "factor": object_scales[scale_key]["factor"] * random.uniform(0.9, 1.0),
#             "name": scale_key,
#             "name_synonym": object_scales[scale_key]["names"][random.randint(0, len(object_scales[scale_key]["names"]) - 1)]
#         }

#         # Add a description to the object if it exists in the caption data
#         if object["uid"] in captions_data:
#             description = captions_data[object["uid"]]
#             object['description'] = description

#     # Retrieve prefixes and suffixes for object names from the object data to vary the textual output
#     object_name_prefixes = object_data["name_prefixes"]
#     object_name_suffixes = object_data["name_suffixes"]

#     # Select a random prefix and suffix from the available options to use in forming the caption
#     random_object_name_prefix = random.choice(object_name_prefixes)
#     random_object_name_suffix = random.choice(object_name_suffixes)

#     # Concatenate all object names into a single string, separated by commas for inclusion in the caption
#     object_names = ', '.join([obj['name'] for obj in combination['objects']])

#     # Compile a list of descriptions for each object, handling cases where the description may be missing
#     # object_descriptions = ', '.join(obj['description'] if obj['description'] is not None else "" for obj in combination['objects'])

#     # Create a combined list of object names and descriptions, formatted as 'name, description' for each object
#     object_name_descriptions = ', '.join([obj['name'] + ", " + obj['description'] if obj['description'] is not None else obj['name'] for obj in combination['objects']])

#     # Check if the placeholder '<objects>' is not present in the camera text
#     if "<objects>" not in camera_text:
#         # If '<objects>' is missing, append a random object name prefix to end of the camera text for variety
#         camera_text = camera_text.strip() + " " + random_object_name_prefix

#     # Replace the first occurrence of '<objects>' in the camera text with the descriptive names of all objects
#     camera_text = camera_text.replace("<objects>", object_name_descriptions, 1)

#     # Replace any remaining '<objects>' placeholders in the camera text with a random object name suffix
#     camera_text = camera_text.replace("<objects>", random_object_name_suffix)

#     # Randomly select a framing description type and retrieve a framing text entry from the combination
#     framing_data = random.choice(["descriptions", "instructions"])
#     framing_text = random.choice(combination["framing"][framing_data])

#     # Replace the '<objects>' placeholder in the framing text with the names of all objects
#     framing_text = framing_text.replace("<objects>", object_names)

#     # Collect the modified camera and framing texts into a list for final caption assembly
#     caption_parts = [camera_text, framing_text]

#     # Load additional stage data related to the scene's setting
#     stage_data = read_json_file('data/stage_data.json')

#     # Retrieve lists of floor material and background names from the stage data
#     floor_material_names = stage_data["material_names"]
#     background_names = stage_data["background_names"]

#     # Randomly choose a prefix from the background names list
#     background_prefix = random.choice(background_names)
#     # Randomly choose a prefix from the floor material names list
#     floor_prefix = random.choice(floor_material_names)

#     # Remove any numeric characters from the floor material name and background name for clarity
#     floor_material_name = ''.join([i for i in floor_material_name if not i.isdigit()]).strip()
#     background_name = ''.join([i for i in background_name if not i.isdigit()]).strip()

#     # Randomly decide whether to add a descriptive sentence about the background
#     if random.random() < 0.3:
#         caption_parts.append(f"The {background_prefix} is {background_name}.")

#     # Randomly decide whether to add a descriptive sentence about the floor material
#     if random.random() < 0.2:
#         caption_parts.append(f"The {floor_prefix} is {floor_material_name}.")

#     # Retrieve relationship descriptions from object data for spatial positioning narratives
#     to_the_left = object_data["relationships"]["to_the_left"]
#     to_the_right = object_data["relationships"]["to_the_right"]
#     in_front_of = object_data["relationships"]["in_front_of"]
#     behind = object_data["relationships"]["behind"]

#     # Initialize an empty list to hold relationship-based sentences between objects
#     relationships = []
    
#     for i, obj1 in enumerate(combination['objects']):
#         for j, obj2 in enumerate(combination['objects']):
#             if i != j:
#                 row_diff = (obj1['placement'] - 1) // 3 - (obj2['placement'] - 1) // 3
#                 col_diff = (obj1['placement'] - 1) % 3 - (obj2['placement'] - 1) % 3
                
#                 if row_diff == 0 and col_diff == -1:
#                     relationships.append(f"{obj1['name']} {random.choice(to_the_left)} {obj2['name']}.")
#                     relationships.append(f"{obj2['name']} {random.choice(to_the_right)} {obj1['name']}.")
#                 elif row_diff == 0 and col_diff == 1:
#                     relationships.append(f"{obj1['name']} {random.choice(to_the_right)} {obj2['name']}.")
#                     relationships.append(f"{obj2['name']} {random.choice(to_the_left)} {obj1['name']}.")
#                 elif row_diff == -1 and col_diff == 0:
#                     relationships.append(f"{obj1['name']} {random.choice(in_front_of)} {obj2['name']}.")
#                     relationships.append(f"{obj2['name']} {random.choice(behind)} {obj1['name']}.")
#                 elif row_diff == 1 and col_diff == 0:
#                     relationships.append(f"{obj1['name']} {random.choice(behind)} {obj2['name']}.")
#                     relationships.append(f"{obj2['name']} {random.choice(in_front_of)} {obj1['name']}.")
#                 elif row_diff == -1 and col_diff == -1:
#                     relationships.append(f"{obj1['name']} {random.choice(to_the_left)} and {random.choice(in_front_of)} {obj2['name']}.")
#                     relationships.append(f"{obj2['name']} {random.choice(to_the_right)} and {random.choice(behind)} {obj1['name']}.")
#                 elif row_diff == -1 and col_diff == 1:
#                     relationships.append(f"{obj1['name']} {random.choice(to_the_right)} and {random.choice(in_front_of)} {obj2['name']}.")
#                     relationships.append(f"{obj2['name']} {random.choice(to_the_left)} and {random.choice(behind)} {obj1['name']}.")
#                 elif row_diff == 1 and col_diff == -1:
#                     relationships.append(f"{obj1['name']} {random.choice(to_the_left)} and {random.choice(behind)} {obj2['name']}.")
#                     relationships.append(f"{obj2['name']} {random.choice(to_the_right)} and {random.choice(in_front_of)} {obj1['name']}.")
#                 elif row_diff == 1 and col_diff == 1:
#                     relationships.append(f"{obj1['name']} {random.choice(to_the_right)} and {random.choice(behind)} {obj2['name']}.")
#                     relationships.append(f"{obj2['name']} {random.choice(to_the_left)} and {random.choice(in_front_of)} {obj1['name']}.")
    
#     selected_relationships = random.sample(relationships, len(combination['objects']) - 1)
#     caption_parts.extend(selected_relationships)

#     # randomize the caption parts order
#     caption_parts = random.sample(caption_parts, len(caption_parts))
    
#     caption = " ".join(caption_parts).replace('..', '.')
#     caption = re.sub(r'\.(?=[a-zA-Z])', '. ', caption)

#     return caption.strip()


# def generate_combinations(camera_data: Dict[str, List[Dict[str, Any]]], count: int) -> List[Dict[str, Any]]:
#     """
#     Generates a list of scene combinations based on provided camera data and a specified count.

#     Each combination includes a selection of objects, backgrounds, and other scene elements
#     like orientation, framing, and animation settings. The function applies random variations
#     to these elements to create unique scene setups.

#     Args:
#         - camera_data (dict): Contains lists of possible orientations, framings, and animations.
#         - count (int): Number of combinations to generate.

#     Returns:
#         list: A list of dictionaries, each representing a unique scene combination.
#     """
#     combinations = []
    
#     # Loop through the number of combinations to be generated
#     for i in range(count):
#         # Randomly select elements for scene configuration
#         orientation = random.choice(camera_data['orientations'])
#         framing = random.choice(camera_data['framings'])
#         animation = random.choice(camera_data['animations'])

#         # Choose a dataset based on weighted probabilities
#         chosen_dataset = random.choices(dataset_names, weights=dataset_weights)[0]
        
#         # Determine a random number of objects to include in the scene
#         number_of_objects = random.randint(1, max_number_of_objects)
        
#         objects = []
#         # Collect the chosen number of objects from the selected dataset
#         for _ in range(number_of_objects):
#             object = random.choice(dataset_dict[chosen_dataset])
#             object['from'] = chosen_dataset
#             objects.append(object)
        
#         # Choose a background based on weighted probabilities
#         chosen_background = random.choices(background_names, weights=background_weights)[0]
#         background_keys = list(background_dict[chosen_background].keys())
#         background_id = random.choice(background_keys)
#         background = background_dict[chosen_background][background_id]
#         background['id'] = background_id
#         background['from'] = chosen_background
        
#         # Select a texture for the scene
#         chosen_texture = random.choices(texture_names, weights=texture_weights)[0]
        
#         # Apply random offsets to framing and orientation to introduce variability
#         framing["position_offset"] = [random.uniform(-0.1, 0.1) for _ in range(3)]
#         framing["rotation_offset"] = [random.uniform(-1, 1) for _ in range(3)]
#         orientation["position_offset"] = [random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), 0]
#         orientation["rotation_offset"] = [random.uniform(-1, 1), random.uniform(-1, 1), 0]
        
#         # Set up the stage with material, scale, and rotation properties
#         stage = {
#             'material': texture_data[chosen_texture],
#             'uv_scale': [random.uniform(0.8, 1.2) for _ in range(2)],
#             'uv_rotation': random.uniform(0, 360),
#         }
        
#         # Create the combination dictionary
#         combination = {
#             'index': i,
#             'objects': objects,
#             'background': background,
#             'orientation': orientation,
#             'framing': framing,
#             'animation': animation,
#             'stage': stage,
#         }
        
#         caption = generate_caption(combination)
#         combination['caption'] = caption
        
#         # remove description and instructions from framing, animation and orientation
#         framing = framing.copy()
        
#         framing.pop("descriptions", None)
#         framing.pop("instructions", None)
        
#         orientation = orientation.copy()
#         orientation.pop("descriptions", None)    
#         orientation.pop("instructions", None)
        
#         animation = animation.copy()
#         animation.pop("descriptions", None)
#         animation.pop("instructions", None)
        
#         combination["orientation"] = orientation
#         combination["framing"] = framing
#         combination["animation"] = animation
        
#         combinations.append(combination)

#     return combinations


# # Generate combinations
# combinations = generate_combinations(camera_data, args.count)


# # Write to JSON file
# with open('combinations.json', 'w') as f:
#     json.dump(combinations, f, indent=4)

# print("Combinations have been successfully written to combinations.json")


