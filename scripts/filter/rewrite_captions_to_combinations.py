import json

def update_combinations_with_new_captions():
    # Load the original combinations file
    with open('./combinations_processed.json', 'r') as f:
        combinations = json.load(f)

    # Load the processed captions file
    with open('./get_captions_processed.json', 'r') as f:
        processed_captions = json.load(f)

    # Create a dictionary of processed captions indexed by their index
    processed_captions_dict = {item['index']: item['caption'] for item in processed_captions}

    # Update the combinations
    updated_count = 0
    for combination in combinations['combinations']:
        index = combination['index']
        if index in processed_captions_dict:
            combination['caption'] = processed_captions_dict[index]
            updated_count += 1
        else:
            print(f"No matching processed caption found for index {index}")

    # Write the updated combinations back to the file
    with open('combinations_updated.json', 'w') as f:
        json.dump(combinations, f, indent=4)

    print(f"Combinations JSON has been updated. {updated_count} captions were replaced.")

if __name__ == "__main__":
    update_combinations_with_new_captions()