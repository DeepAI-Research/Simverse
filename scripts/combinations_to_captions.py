import json
import os
import argparse


def main(json_file, video_folder=None):
    # Load the combinations.json file
    with open(json_file, "r") as f:
        data = json.load(f)

    combinations = data.get("combinations", [])

    captions = []

    if video_folder:
        # List and sort all .mp4 and .png files in the video folder based on numerical index
        video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]
        image_files = [f for f in os.listdir(video_folder) if f.endswith(".png")]

        video_files.sort(key=lambda x: int(os.path.splitext(x)[0].split("_")[0]))
        image_files.sort(key=lambda x: int(os.path.splitext(x)[0].split("_")[0]))

        # Debugging: Print files count and sorted lists
        print(f"Found {len(video_files)} video files.")
        print(f"Sorted video files: {video_files}")
        print(f"Found {len(image_files)} image files.")
        print(f"Sorted image files: {image_files}")

        # Process each combination, ensuring we do not exceed the number of available videos or images
        for i, obj in enumerate(combinations):
            if i >= len(video_files) and i >= len(image_files):
                print(
                    f"Warning: Only {len(video_files)} videos and {len(image_files)} images found. Stopping at index {i}."
                )
                break

            # Access the 'caption' field
            caption = obj.get("caption")

            # Ensure the required field is present
            if caption:
                # Create a new object with the desired format
                caption_obj = {
                    "cap": [caption],
                }
                if i < len(video_files):
                    caption_obj["path"] = f"{video_folder}/{video_files[i]}"
                if i < len(image_files):
                    caption_obj["path"] = f"{video_folder}/{image_files[i]}"

                captions.append(caption_obj)
            else:
                print(f"Missing caption in combination at index {i}: {obj}")

    else:
        # Process each combination without video or image paths
        for i, obj in enumerate(combinations):
            # Access the 'caption' field
            caption = obj.get("caption")

            # Ensure the required field is present
            if caption:
                # Create a new object with the desired format
                caption_obj = {"cap": [caption]}
                captions.append(caption_obj)
            else:
                print(f"Missing caption in combination at index {i}: {obj}")

    # Write the captions array to captions.json file
    with open("captions.json", "w") as out_f:
        json.dump(captions, out_f, indent=2)


# Run the script with the required arguments
# python scripts/combinations_to_captions.py --json_file ./combinations.json [--video_folder ./renders]
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert combinations to captions format."
    )
    parser.add_argument(
        "--json_file", type=str, required=True, help="Path to combinations.json"
    )
    parser.add_argument("--video_folder", type=str, help="Path to videos folder")
    args = parser.parse_args()

    main(args.json_file, args.video_folder)
