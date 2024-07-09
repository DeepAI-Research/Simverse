import json
import glob
import re

def combine_json_files(file_pattern):
    combined_data = []
    
    # Get all files matching the pattern
    files = glob.glob(file_pattern)
    
    for file_path in files:
        with open(file_path, 'r') as file:
            content = file.read()
            
            # Remove any leading/trailing square brackets from the entire file
            content = content.strip().strip('[]')
            
            # Split the content into individual JSON objects
            json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content)
            
            for json_str in json_objects:
                try:
                    json_obj = json.loads(json_str)
                    combined_data.append(json_obj)
                except json.JSONDecodeError:
                    print(f"Warning: Skipping invalid JSON object in {file_path}")

    return combined_data

def write_combined_json(output_file, data):
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

# Usage
file_pattern = 'get_captions_processed.json'  # Adjust this pattern as needed
# file_pattern = 'get_captions_processed*.json'  # Adjust this pattern as needed
output_file = 'combined_captions.json'

combined_data = combine_json_files(file_pattern)
write_combined_json(output_file, combined_data)

print(f"Combined JSON written to {output_file}")