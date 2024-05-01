import os
import time
import objaverse
import objaverse.xl as oxl
import json

import requests

annotations = oxl.get_annotations(download_dir='./', )

annotations = objaverse.load_annotations()

# save annotations to json. annotations is a dict
with open('annotations.json', 'w') as file:
    json.dump(annotations, file, indent=4)

annotations = json.load(open('annotations.json'))

categories = set()
for model in annotations.values():
    for category in model["categories"]:
        categories.add(category['name'])

for category in categories:
    category_data = [model for model in annotations.values() if category in [cat['name'] for cat in model['categories']]]
    with open(f"data/{category}.json", 'w') as file:
        json.dump(category_data, file, indent=4)

files = os.listdir('./datasets')

model_count = 0

for file in files:
    data = json.load(open(f'./datasets/{file}'))
    
    # Filter data entries ensuring all required fields are present and meet criteria
    filtered_data = []
    for model in data:
        # Check for presence of all necessary keys and that their values meet criteria
        if ('faceCount' in model and 50 < model['faceCount'] < 1000000 and 
            'vertexCount' in model and 50 < model['vertexCount'] < 1000000 and 
            'tags' in model and 
            not any(tag['name'].lower().find("scan") != -1 or tag['name'].lower().find("photogrammetry") != -1 for tag in model['tags']) and
            'archives' in model and 
            not any(archive_data.get("textureCount") == 0 for archive_data in model['archives'].values())):
            filtered_data.append(model)
    
    annotations_slim = [{"uid": model["uid"], "name": model["name"], "categories": [cat['name'] for cat in model["categories"]], "description": model["description"], "tags": [tag['name'] for tag in model["tags"]]} for model in filtered_data]
    model_count += len(annotations_slim)
    # Overwrite the file with filtered data
    with open(f"./datasets/{file}", 'w') as file:
        json.dump(annotations_slim, file, indent=4)
        
print(f"Extracted data for {model_count} models")

files = os.listdir('./datasets')
for file in files:
    data = json.load(open(f'./datasets/{file}'))

    # for each entry get https://api.sketchfab.com/v3/models/<uid>
    # get the "description" field and save it to the existing entry
    for model in data:
        uid = model["uid"]
        request = requests.get(f"https://api.sketchfab.com/v3/models/{uid}")
        model_data = request.json()
        if "description" in model_data:
            model["description"] = model_data["description"]
            print(f"got description for {uid}: {model_data['description']}")
        else:
            print(f"no description for {uid}")
            model["description"] = ""
        time.sleep(.1)

    with open(f"./datasets/{file}", 'w') as file:
        json.dump(data, file, indent=4)
