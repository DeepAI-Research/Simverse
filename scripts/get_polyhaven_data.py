import requests
import json
import os

# JSON file path
json_file = "hdri_urls.json"

# Check if the JSON file exists, otherwise create an empty dictionary
if os.path.exists(json_file):
    with open(json_file, "r") as file:
        hdri_data = json.load(file)
else:
    hdri_data = {}

# Step 1: GET request to retrieve the list of HDRIs
url = "https://api.polyhaven.com/assets?type=hdris"
response = requests.get(url)
data = response.json()

# Step 2: Iterate over the keys (IDs) of the JSON object
for id, asset_data in data.items():
    # Check if the ID is already in the JSON file
    if id in hdri_data:
        print(f"Skipping ID: {id} (already exists in the JSON file)")
        continue

    # Step 3: Visit the URL for each ID
    file_url = f"https://api.polyhaven.com/files/{id}"
    file_response = requests.get(file_url)
    file_data = file_response.json()

    # Step 4: Extract the URL associated with the HDR file inside the 8k hdri key'd value
    hdr_url = file_data["hdri"]["8k"]["hdr"]["url"]

    # Step 5: Extract the name, categories, and tags from the asset data
    name = asset_data["name"]
    categories = asset_data["categories"]
    tags = asset_data["tags"]

    # Step 6: Add the ID, URL, name, categories, and tags to the dictionary
    hdri_data[id] = {
        "url": hdr_url,
        "name": name,
        "categories": categories,
        "tags": tags
    }

    # Save the updated dictionary to the JSON file
    with open(json_file, "w") as file:
        json.dump(hdri_data, file, indent=4)

    print(f"Added ID: {id}, URL: {hdr_url}, Name: {name}")

print("JSON file updated successfully.")