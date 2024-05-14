import json

# Read the combinations.json file
with open('combinations.json', 'r') as file:
    combinations = json.load(file)

# Create an array to store the converted objects
captions = []

# Iterate over each object in combinations
for i, obj in enumerate(combinations):
    # Create a new object with the desired format
    caption_obj = {
        'path': f'/videos/{i}.mp4',
        'cap': [obj['caption']]
    }
    captions.append(caption_obj)

# Write the captions array to captions.json file
with open('captions.json', 'w') as file:
    json.dump(captions, file, indent=2)