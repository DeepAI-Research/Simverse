import json

def filter_combinations(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    original_count = len(data['combinations'])
    filtered_combinations = []

    for combination in data['combinations']:
        placements = [obj['placement'] for obj in combination['objects']]
        if len(placements) != len(set(placements)):
            filtered_combinations.append(combination)

    data['combinations'] = filtered_combinations
    data['count'] = len(filtered_combinations)

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Original combinations: {original_count}")
    print(f"Filtered combinations: {len(filtered_combinations)}")
    print(f"Removed {original_count - len(filtered_combinations)} combinations")
    print(f"Updated JSON saved to {file_path}")

# Usage
file_path = './combinations.json'  # Replace with your actual file path
filter_combinations(file_path)