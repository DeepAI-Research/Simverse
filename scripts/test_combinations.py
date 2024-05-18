import json

def find_duplicate_placements(combinations):
    """
    Find combinations with duplicate placements.

    Args:
        combinations (list): List of combination data.

    Returns:
        list: List of index numbers with duplicate placements.
    """
    indices_with_duplicates = []

    for combination in combinations:
        index = combination["index"]
        placements = [obj["placement"] for obj in combination["objects"]]
        if len(placements) != len(set(placements)):
            indices_with_duplicates.append(index)

    return indices_with_duplicates

# Load combinations.json file
with open('combinations.json', 'r') as file:  # Adjust the path as needed
    data = json.load(file)

# Find indices with duplicate placements
duplicates = find_duplicate_placements(data["combinations"])

print("Indices with duplicate placements:", duplicates)

