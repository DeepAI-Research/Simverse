import json

def replace_background_values(background):
    background["name"] = "<name_placeholder>"
    background["url"] = "<url_placeholder>"
    background["id"] = "<id_placeholder>"
    background["from"] = "<from_placeholder>"

def replace_map_values(maps):
    for key in maps:
        maps[key] = f"<{key.lower()}_placeholder>"

def process_combinations(data):
    for combination in data["combinations"]:
        if "background" in combination:
            replace_background_values(combination["background"])
        
        if "stage" in combination and "material" in combination["stage"]:
            material = combination["stage"]["material"]
            if "maps" in material:
                replace_map_values(material["maps"])

def main():
    input_file = "./combinations.json"
    output_file = "combinations_processed.json"

    try:
        with open(input_file, 'r') as file:
            data = json.load(file)

        process_combinations(data)

        with open(output_file, 'w') as file:
            json.dump(data, file, indent=4)

        print(f"Processing complete. Output saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {input_file} is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()