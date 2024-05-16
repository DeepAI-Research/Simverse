import json
import os
import argparse

def main(json_file, video_folder, output_folder):
    # Load the combinations.json file
    with open(json_file, 'r') as f:
        data = json.load(f)

    combinations = data.get('combinations', [])

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Process each combination
    for obj in combinations:
        # Access the 'caption' field
        caption = obj.get('caption')
        index = obj.get('index')

        # Ensure the required fields are present
        if caption and index is not None:
            output_caption_file = os.path.join(output_folder, f"{index}.txt")
            
            # Write the caption to a file
            with open(output_caption_file, 'w') as out_f:
                out_f.write(caption)
        else:
            print(f"Missing caption or index in combination: {obj}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process combinations to captions.')
    parser.add_argument('--json_file', type=str, required=True, help='Path to combinations.json')
    parser.add_argument('--video_folder', type=str, required=True, help='Path to videos folder')
    parser.add_argument('--output_folder', type=str, required=True, help='Path to output captions folder')
    args = parser.parse_args()

    main(args.json_file, args.video_folder, args.output_folder)
