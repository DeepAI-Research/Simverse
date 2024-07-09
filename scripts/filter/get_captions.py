import json

# Load the existing combinations.json file
with open('./combinations_processed.json', 'r') as file:
    data = json.load(file)

# Initialize a list to store the extracted captions
captions_list = []

# Extract captions for each combination
for combination in data['combinations']:
    captions = {
        'index': combination['index'],
        'objects_caption': combination.get('objects_caption', ''),
        'background_caption': combination.get('background_caption', ''),
        'orientation_caption': combination.get('orientation_caption', ''),
        'framing_caption': combination.get('framing_caption', ''),
        'animation_caption': combination.get('animation_caption', ''),
        'stage_caption': combination.get('stage_caption', ''),
        'postprocessing_caption': combination.get('postprocessing_caption', ''),
        'caption': combination.get('caption', '')
    }
    captions_list.append(captions)

# Determine the number of files needed
max_rows_per_file = 500
num_files = (len(captions_list) + max_rows_per_file - 1) // max_rows_per_file

# Save the extracted captions to multiple JSON files
for i in range(num_files):
    start_index = i * max_rows_per_file
    end_index = start_index + max_rows_per_file
    file_data = captions_list[start_index:end_index]
    with open(f'get_captions_{i + 1}.json', 'w') as file:
        json.dump(file_data, file, indent=4)

print(f"Captions extracted and saved to {num_files} files.")
