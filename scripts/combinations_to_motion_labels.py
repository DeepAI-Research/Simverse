# combinations_to_labels.py
import json
import os
import argparse

def main(json_file):
    # Load the combinations.json file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    combinations = data.get('combinations', [])
    
    # Create a list to store the labels
    labels = []
    
    # Process each combination, ensuring we do not exceed the number of available videos
    for i, obj in enumerate(combinations):
        # Access the 'animation' field
        animation = obj.get('animation')
        
        # Use a default motion value of "NONE" if 'animation' field is missing
        if animation:
            # Extract the 'motion' value, using "NONE" as default if missing
            motion = animation.get('name', "NONE")
        else:
            motion = "NONE"
        
        # Convert the motion value to the appropriate enum label
        label = motion.upper()
        labels.append(label)
    
    # Write the labels to labels.txt file
    with open('labels.txt', 'w') as out_f:
        for i, label in enumerate(labels):
            out_f.write(f"{i}.mp4 {label}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert combinations to labels format.')
    parser.add_argument('--json_file', type=str, default="combinations.json", required=False, help='Path to combinations.json')
    args = parser.parse_args()

    main(args.json_file)