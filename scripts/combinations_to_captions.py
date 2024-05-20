import json
import os
import argparse

def main(json_file, video_folder):
    # Load the combinations.json file
    with open(json_file, 'r') as f:
        data = json.load(f)

    combinations = data.get('combinations', [])

    # List and sort all .mp4 video files in the video folder based on numerical index
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]
    video_files.sort(key=lambda x: int(os.path.splitext(x)[0]))

    # Debugging: Print video files count and sorted list
    print(f"Found {len(video_files)} video files.")
    print(f"Sorted video files: {video_files}")

    # Create an array to store the converted objects
    captions = []

    # Process each combination, ensuring we do not exceed the number of available videos
    for i, obj in enumerate(combinations):
        if i >= len(video_files):
            print(f"Warning: Only {len(video_files)} videos found. Stopping at video index {i}.")
            break

        # Access the 'caption' field
        caption = obj.get('caption')
        
        # Ensure the required field is present
        if caption:
            # Create a new object with the desired format
            caption_obj = {
                'path': f'{video_folder}/{video_files[i]}',
                'cap': [caption]
            }
            captions.append(caption_obj)
        else:
            print(f"Missing caption in combination at index {i}: {obj}")

    # Write the captions array to captions.json file
    with open('captions.json', 'w') as out_f:
        json.dump(captions, out_f, indent=2)

# Run the script with the required arguments
# python scripts/combinations_to_captions.py --json_file ./combinations.json --video_folder ./renders
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert combinations to captions format.')
    parser.add_argument('--json_file', type=str, required=True, help='Path to combinations.json')
    parser.add_argument('--video_folder', type=str, required=True, help='Path to videos folder')
    args = parser.parse_args()

    main(args.json_file, args.video_folder)
