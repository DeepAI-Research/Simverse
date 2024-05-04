import requests
import json
import os

if not os.path.exists("./datasets"):
    os.makedirs("./datasets")

json_file = "./datasets/texture_urls.json"

if os.path.exists(json_file):
    with open(json_file, "r") as file:
        texture_data = json.load(file)
else:
    texture_data = {}

url = "https://api.polyhaven.com/assets?type=textures"
response = requests.get(url)
data = response.json()

for id, asset_data in data.items():
    if id in texture_data:
        print(f"Skipping ID: {id} (already exists in the JSON file)")
        continue
    
    file_url = f"https://api.polyhaven.com/files/{id}"
    file_response = requests.get(file_url)
    file_data = file_response.json()
    
    texture_maps = {}
    
    map_types = file_data.keys()
    
    for map_type in map_types:
        preferred_resolutions = ["4k", "2k"]  # Prioritize higher resolutions first
        file_formats = ["jpg", "png"]  # Common file formats

        for resolution in preferred_resolutions:
            if resolution in file_data[map_type]:
                for file_format in file_formats:
                    if file_format in file_data[map_type][resolution]:
                        texture_maps[map_type] = file_data[map_type][resolution][file_format]["url"]
                        break  # Stop checking once the first applicable format is found
                if map_type in texture_maps:
                    break  # Break the outer loop if a URL has been found

    name = asset_data["name"]
    categories = asset_data["categories"]
    tags = asset_data["tags"]
    
    texture_data[id] = {
        "maps": texture_maps,
        "name": name,
        "categories": categories,
        "tags": tags
    }
    
    with open(json_file, "w") as file:
        json.dump(texture_data, file, indent=4)
    
    print(f"Added ID: {id}, Name: {name}")

print("JSON file updated successfully.")