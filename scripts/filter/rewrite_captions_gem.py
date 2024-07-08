import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
MODEL = "gemini-1.5-pro"

def setup_gemini():
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name=MODEL,
        generation_config=generation_config,
    )
    return model

def rewrite_caption(model, caption_batch, context_string):
    content = f"{context_string}\n\n{json.dumps(caption_batch)}"

    print("Caption context:")
    print(content)

    try:
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(content)
        captions_content = response.text.strip()
        print("API Response:\n", captions_content)  # Debug print

        # Remove Markdown code block syntax if present
        if captions_content.startswith("```json"):
            captions_content = captions_content.replace("```json", "", 1)
        if captions_content.endswith("```"):
            captions_content = captions_content.rsplit("```", 1)[0]
        captions_content = captions_content.strip()

        try:
            # Try parsing the response as a JSON list
            rewritten_captions_content = json.loads(captions_content)
            if not isinstance(rewritten_captions_content, list):
                raise ValueError("Parsed JSON is not a list")
        except (json.JSONDecodeError, ValueError) as e:
            print("JSON Decode Error or Value Error:", e)
            print("Fallback: Returning original captions")
            return caption_batch

        print("==== Captions rewritten by Google Gemini ====")
        return rewritten_captions_content
    except Exception as e:
        print(f"Error: {str(e)}")
        return caption_batch

def read_combinations():
    with open("./get_captions_1.json") as file:
        data = json.load(file)
        print("==== File read, combinations extracted ====")
        return data

def write_to_file(rewritten_combinations):
    with open("./get_captions_processed.json", "w") as file:
        json.dump(rewritten_combinations, file, indent=4)
    print("==== File combinations rewritten, check file ====")

def rewrite_captions_in_batches(model, combinations, context_string):
    batch_size = 5
    rewritten_combinations = []
    for i in range(0, len(combinations), batch_size):
        caption_batch = combinations[i : i + batch_size]
        rewritten_captions = rewrite_caption(model, caption_batch, context_string)
        rewritten_combinations.extend(rewritten_captions)
    return rewritten_combinations

if __name__ == "__main__":
    CONTEXT_STRING = """
    examples:
    Before: "2ft Vehicle Mine GTA2 3d remake: A green and red spaceship with a circular design and a red button. 7 LOW POLY PROPS: a pink square with a small brown box and a stick on it, resembling a basketball court. Modified Colt 1911 Pistol is a gun LOW POLY PROPS is to the left of and behind Modified Colt 1911 Pistol. Modified Colt 1911 Pistol is to the right of and in front of LOW POLY PROPS. Vehicle Mine GTA2 3d remake is  and in front of LOW POLY PROPS. The view is set sharply downward, looking 189\u00b0 to the right. Set the focal length of the camera to 75 mm. Semi-close perspective  The panorama is Monbachtal Riverbank. The floor is Shell Floor. The scene transitions swiftly with enhanced animation speed."
    After: "Vehicle Mine GTA2 3d remake is a green and red spaceship with a circular design and a red button. LOW POLY PROPS is pink square with a small brown box and a stick on it, resembling a basketball court. Modified Colt 1911 Pistol is a gun LOW POLY PROPS is to the left of and behind Modified Colt 1911 Pistol. Modified Colt 1911 Pistol is to the right of and in front of LOW POLY PROPS. Vehicle Mine GTA2 3d remake is  and in front of LOW POLY PROPS. The view is set sharply downward and looking 189 degrees to the right. Somewhat close perspective and the floor is a Shell Floor. Scene transitions swiftly with enhanced animation speed."

    Before: "Dulal Das Test File (height: 5feet) is a tan leather recliner chair and ottoman. Stylized Apple = a pink apple or peach on a plate. Stylized Apple is to the left of Dulal Das Test File. Dulal Das Test File is to the right of Stylized Apple. The lens is oriented direct right, with a 30 forward tilt. Set the fov of the camera to 32 degrees. (61.00 mm focal length) Standard medium.  The scenery is Limehouse. The ground material is Gravel Floor. A standard animation speed is applied to the scene."
    After: "Dulal Das Test File is a tan leather recliner chair and ottoman. Stylized Apple is pink apple or peach on a plate. Dulal Das Test File is right of Stylized Apple. The lens is oriented direct right, with a slight forward tilt. Set the field of view of the camera to 32 degrees. The scenery is Limehouse with ground material of Gravel Floor. A normal animation speed for the scene."

    Before: "Best Japanese Curry is 1 and A bowl of stew with rice and meat. Apple is 7feet and an apple. Apple is  and behind Best Japanese Curry. Best Japanese Curry is  and in front of Apple. Direct the camera sharp right back, set tilt to steeply angled down. The focal length is 29 mm. Taking in the whole scene. The scene has a noticeable bloom effect. Motion blur is set to medium intensity in the scene. The backdrop is Pump House. The floor texture is Wood Plank Wall. The scene moves with a relaxed animation speed."
    After: "Best Japanese Curry is a bowl of stew with rice and meat. Apple is an apple placed behind Best Japanese Curry. Best Japanese Curry is in front of Apple. The camera is very angled right and very down, make sure to capture whole scene. Subtle glow effect, and medium blur when movement. Background is Pump House with a wood plank floor. Slow animation speed maybe"

    Before: "[Black Mercedes-Benz G-Class SUV - Black Mercedes-Benz G-Class SUV - 0.75meters] a damaged room with a kitchen and bathroom, including a refrigerator, sinks, and a toilet, in an upside-down house and destroyed building. (size: 1.5meters) a damaged room with a kitchen and bathroom, including a refrigerator, sinks, and a toilet, in an upside-down house and destroyed building. is  and in front of Black Mercedes-Benz G-Class SUV. Black Mercedes-Benz G-Class SUV is  and behind a damaged room with a kitchen and bathroom, including a refrigerator, sinks, and a toilet, in an upside-down house and destroyed building.. Rotate the camera to heavy left rear and tilt it 51 forward. The camera has a 17 mm focal length. Extremely wide coverage  The landscape is Woods. The floor material is Blue Painted Planks. The scene has a faster animation speed of 156%."
    After: "there are 2 objects: Black Mercedes-Benz G-Class SUV, a damaged room with a kitchen and bathroom, including a refrigerator, sinks, and a toilet, in an upside-down house and destroyed building. the damaged room with a kitchen and bathroom is infront of Black Mercedes-Benz G-Class SUV. Black Mercedes-Benz G-Class SUV is  and behind the damaged room. Rotate the camera a lot left and tilt it forward, wide angle. wood landscape. The floor is blue painted planks. fast animation speed."

    Above are caption example before and after. Go through array of captions and make it sound more human. Change complex director-like words like "bloom" or "pitch", change them to synonyms that are easier to understand and that any person would most likely use.
    Feel free to change/remove exact values like degrees. Instead of 32 degrees left you can say slightly to the left. Combine sentences maybe.
    Use synonyms/words to use. You can even remove some words/sentences but capture some of the holistic important details.

    Below are captions that NEED to be shortened/simplified, and more human-like. Return an array of rewritten captions. 
    Process the input array and return a new array with rewritten captions in the same format.
    """

    model = setup_gemini()
    combinations = read_combinations()
    rewritten_combinations = rewrite_captions_in_batches(model, combinations, CONTEXT_STRING)
    write_to_file(rewritten_combinations)