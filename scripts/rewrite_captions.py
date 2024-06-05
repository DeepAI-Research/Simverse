import os
import json
import requests

MODEL = "gpt-4o"


def rewrite_caption(caption_arr, context_string):
    split_captions = [caption.split(", ") for caption in caption_arr]
    caption_string = json.dumps(split_captions)

    content = f"{context_string}\n\n{caption_string}"

    print("Caption context:")
    print(content)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.5,
        "top_p": 0.8,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )

    if response.status_code == 200:
        response_data = response.json()
        captions_content = response_data["choices"][0]["message"]["content"].strip()
        print("API Response:\n", captions_content)  # Debug print

        try:
            # Try parsing the response as a JSON list
            rewritten_captions_content = json.loads(captions_content)
            if not isinstance(rewritten_captions_content, list):
                raise ValueError("Parsed JSON is not a list")
        except (json.JSONDecodeError, ValueError) as e:
            print("JSON Decode Error or Value Error:", e)
            # Fallback to splitting the response by newlines, assuming each line is a caption
            rewritten_captions_content = captions_content.split("\n")

        print("==== Captions rewritten by OpenAI ====")
        return rewritten_captions_content
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []


def read_combinations_and_get_array_of_just_captions():
    # we want just the caption text and store in array
    with open("combinations.json") as file:
        data = json.load(file)
        combinations = data.get("combinations")
        captions = []
        for obj in combinations:
            caption = obj.get("caption")
            captions.append(caption)
        print("==== File read, captions extracted ====")
        return captions


def write_to_file(i, rewritten_captions):
    with open("combinations.json", "r+") as file:
        data = json.load(file)

        combinations = data.get("combinations")

        for j in range(len(rewritten_captions)):
            print("==> Rewriting caption: ", i + j)
            combinations[i + j]["caption"] = rewritten_captions[j]

        data["combinations"] = combinations

        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

    print("==== File captions rewritten, check file ====")


def rewrite_captions_in_batches(combinations, context_string):
    batch_size = 10
    num_combinations = len(combinations)

    for i in range(0, num_combinations, batch_size):
        captions_batch = combinations[i : i + batch_size]
        rewritten_captions = rewrite_caption(captions_batch, context_string)
        write_to_file(i, rewritten_captions)


if __name__ == "__main__":
    CONTEXT_STRING = """
    examples:
    Before: "2ft Vehicle Mine GTA2 3d remake: A green and red spaceship with a circular design and a red button. 7 LOW POLY PROPS: a pink square with a small brown box and a stick on it, resembling a basketball court. Modified Colt 1911 Pistol is a gun LOW POLY PROPS is to the left of and behind Modified Colt 1911 Pistol. Modified Colt 1911 Pistol is to the right of and in front of LOW POLY PROPS. Vehicle Mine GTA2 3d remake is  and in front of LOW POLY PROPS. The view is set sharply downward, looking 189\u00b0 to the right. Set the focal length of the camera to 75 mm. Semi-close perspective  The panorama is Monbachtal Riverbank. The floor is Shell Floor. The scene transitions swiftly with enhanced animation speed."
    After: "Vehicle Mine GTA2 3d remake is a green and red spaceship with a circular design and a red button. LOW POLY PROPS is pink square with a small brown box and a stick on it, resembling a basketball court. Modified Colt 1911 Pistol is a gun LOW POLY PROPS is to the left of and behind Modified Colt 1911 Pistol. Modified Colt 1911 Pistol is to the right of and in front of LOW POLY PROPS. Vehicle Mine GTA2 3d remake is  and in front of LOW POLY PROPS. The view is set sharply downward and looking 189 degrees to the right. Somewhat close perspective and the floor is a Shell Floor. Scene transitions swiftly with enhanced animation speed."

    Before: "Dulal Das Test File (height: 5feet) is a tan leather recliner chair and ottoman. Stylized Apple = a pink apple or peach on a plate. Stylized Apple is to the left of Dulal Das Test File. Dulal Das Test File is to the right of Stylized Apple. The lens is oriented direct right, with a 30 forward tilt. Set the fov of the camera to 32 degrees. (61.00 mm focal length) Standard medium.  The scenery is Limehouse. The ground material is Gravel Floor. A standard animation speed is applied to the scene."
    After: "Dulal Das Test File is a tan leather recliner chair and ottoman. Stylized Apple is pink apple or peach on a plate. Dulal Das Test File is right of Stylized Apple. The lens is oriented direct right, with a slight forward tilt. Set the field of view of the camera to 32 degrees. The scenery is Limehouse with ground material of Gravel Floor. A normal animation speed for the scene."

    Before: "Best Japanese Curry is 1 and A bowl of stew with rice and meat. Apple is 7feet and an apple. Apple is  and behind Best Japanese Curry. Best Japanese Curry is  and in front of Apple. Direct the camera sharp right back, set tilt to steeply angled down. The focal length is 29 mm. Taking in the whole scene. The scene has a noticeable bloom effect. Motion blur is set to medium intensity in the scene. The backdrop is Pump House. The floor texture is Wood Plank Wall. The scene moves with a relaxed animation speed."
    After: "Best Japanese Curry is a bowl of stew with rice and meat. Apple is an apple placed behind Best Japanese Curry. Best Japanese Curry is in front of Apple. The camera is very angled right and very down, make sure to capture whole scene. Subtle glow effect, and medium blur when movement. Background is Pump House with a wood plank floor. Slow animation speed maybe"

    Above are caption example before and after. Go through array of captions and make it sound more human. Change complex director-like words like "bloom" or "pitch", change them to synonyms that are easier to understand and that any person would most likely use.
    Feel free to change/remove exact values like degrees. Instead of 32 degrees left you can say slightly to the left. Combine sentences maybe.
    Use synonyms/words to use. You can even remove some words/sentences but capture some of the holistic important details.

    Below are captions that NEED to be shortened/simplified, and more human-like. Return an array of rewritten captions. DO NOT wrap the strings in quotes in the array and return in format: ["caption1", "caption2", "caption3"]
    """

    combinations = read_combinations_and_get_array_of_just_captions()
    rewrite_captions_in_batches(combinations, CONTEXT_STRING)
