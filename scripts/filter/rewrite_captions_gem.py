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

    Example 1:
    Before:
        "index": 0,
        "objects_caption": "Object caption:   The Mario Bros model compatible with 3ds Max, Maya, Blender, and other modeling and animation software. shifts to the right at quickly 0.29 each second.",
        "background_caption": "Scene background: The landscape is Brown Photostudio 07.",
        "orientation_caption": "Camera orientation: Direct the camera far right front, set tilt to mildly downward.",
        "framing_caption": "Camera framing: Full perspective Set the fov of the camera to 57 degrees. (32.00 mm focal length)",
        "animation_caption": "Camera animation: The camera pans alongside Mario Bros model compatible with 3ds Max, Maya, Blender, and other modeling and animation software., capturing every move. The scene is rendered with a moderate animation speed of 83%.",
        "stage_caption": "Scene stage: The background scene is Brown Photostudio. The floor material is Medieval Blocks.",
        "postprocessing_caption": "Post-processing effects: The scene has a moderate bloom effect. No screen-space ray tracing is used in the scene.",
        "caption": "Mario Bros model compatible with 3ds Max, Maya, Blender, and other modeling and animation software. = Mario Bros model compatible with 3ds Max, Maya, Blender, and other modeling and animation software.  The camera pans alongside Mario Bros model compatible with 3ds Max, Maya, Blender, and other modeling and animation software., capturing every move. The Mario Bros model compatible with 3ds Max, Maya, Blender, and other modeling and animation software. shifts to the right at quickly 0.29 each second. Direct the camera far right front, set tilt to mildly downward. Full perspective Set the fov of the camera to 57 degrees. (32.00 mm focal length) The scene has a moderate bloom effect. No screen-space ray tracing is used in the scene. The background scene is Brown Photostudio. The floor material is Medieval Blocks. The scene is rendered with a moderate animation speed of 83%."
    After:
        "index": 0,
        "objects_caption": "Object caption: Mario Bros model shifts to the right quickly each second.",
        "background_caption": "Scene background: The landscape is Brown Photostudio 07.",
        "orientation_caption": "Camera orientation: Direct the camera far right front, set tilt to mildly downward.",
        "framing_caption": "Camera framing: Full perspective fov of the camera",
        "animation_caption": "Camera animation: The camera pans alongside Mario Bros model, capturing every move. The scene is rendered with a moderate animation speed.",
        "stage_caption": "Scene stage: The background scene is Brown Photostudio. The floor material is Medieval Blocks.",
        "postprocessing_caption": "Post-processing effects: The scene has a moderate bloom effect. No screen-space ray tracing is used in the scene.",
        "caption": "Camera pans alongside Mario Bros model capturing every move. The Mario Bros model compatible shifts right at quickly 0.29 per second. The camera far right front, set tilt to mildly downward. Full perspective fov of camera. Scene has a moderate bloom effect. No screen-space ray tracing is used in the scene. The background scene is Brown Photostudio. The floor material is Medieval Blocks. The scene is rendered with a moderate animation speed of 83%."

    Example 2: 
    Before:
        "index": 1,
        "objects_caption": "Object caption:   The a white ornate corbel and column. drifts forward at brisk 0.46 units.",
        "background_caption": "Scene background: The landscape is Theater 01.",
        "orientation_caption": "Camera orientation: Yaw: flat left, Pitch: 47 degrees downward.",
        "framing_caption": "Camera framing: Balanced perspective The field of view is 38 degrees. (50.00 mm focal length)",
        "animation_caption": "Camera animation: Tracking a white ornate corbel and column., the camera provides a dynamic view of its actions. Fast animation of 141% is used in the scene.",
        "stage_caption": "Scene stage: The scene is Theater. The ground is Coast Sand.",
        "postprocessing_caption": "Post-processing effects: Bloom effect is set to high intensity. The scene is rendered with a strong ambient occlusion effect.",
        "caption": "A massive a white ornate corbel and column. is a white ornate corbel and column.  Tracking a white ornate corbel and column., the camera provides a dynamic view of its actions. The a white ornate corbel and column. drifts forward at brisk 0.46 units. Yaw: flat left, Pitch: 47 degrees downward. Balanced perspective The field of view is 38 degrees. (50.00 mm focal length) Bloom effect is set to high intensity. The scene is rendered with a strong ambient occlusion effect. The scene is Theater. The ground is Coast Sand. Fast animation of 141% is used in the scene."
    After:
        "index": 1,
        "objects_caption": "Object caption: The a white ornate corbel and column moves forward quick",
        "background_caption": "Scene background: The landscape is Theater 01.",
        "orientation_caption": "Camera orientation: flat left with downward pitch roughly",
        "framing_caption": "Camera framing: even field of view",
        "animation_caption": "Camera animation: Tracking a white ornate corbel and column. Camera provides dynamic view of its actions in a fast paced animation.",
        "stage_caption": "Scene stage: The scene is Theater and the ground is Coast Sand.",
        "postprocessing_caption": "Post-processing effects: high intensity lighting plus strong ambient occlusion effect.",
        "caption": "Track the massive white ornate corbel and column as camera provides dynamic view of movement. Make white ornate drift forward quickly and make camera flat left with downward pointing , Pitch: 47 degrees downward. The scene is Theater with Coast Sand ground"
        
    Example 3:
    Before:
        "index": 499,
        "objects_caption": "Object caption: a lion wearing a t-shirt, accompanied by a white piece of paper with writing on it. is to the left of a small house with a purple roof and a ceiling light fixture.. a small house with a purple roof and a ceiling light fixture. is to the right of a lion wearing a t-shirt, accompanied by a white piece of paper with writing on it.. a lion wearing a t-shirt, accompanied by a white piece of paper with writing on it. is to the left of and behind a square table with a square base and light fixture..  The a square table with a square base and light fixture. heads to the left at 0.15. The a small house with a purple roof and a ceiling light fixture. heads right at 0.27 units. Moving forward at speedily 0.30, the a lion wearing a t-shirt, accompanied by a white piece of paper with writing on it. progresses.",
        "background_caption": "Scene background: The landscape is Harvest.",
        "orientation_caption": "Camera orientation: Yaw: sharply forward left, Pitch: horizontally level.",
        "framing_caption": "Camera framing: Fully zoomed out The focal length is 30 mm.",
        "animation_caption": "Camera animation: Tracking a square table with a square base and light fixture., the camera provides a dynamic view of its actions. Animations are intentionally slowed down.",
        "stage_caption": "Scene stage: The background view is Harvest. The flooring texture is Stone Floor.",
        "postprocessing_caption": "Post-processing effects: High screen-space ray tracing is used in the scene. High motion blur is used in the scene.",
        "caption": "a square table with a square base and light fixture. is a square table with a square base and light fixture. A hefty a lion wearing a t-shirt, accompanied by a white piece of paper with writing on it. is a lion wearing a t-shirt, accompanied by a white piece of paper with writing on it. The a small house with a purple roof and a ceiling light fixture. is described as a small house with a purple roof and a ceiling light fixture. a lion wearing a t-shirt, accompanied by a white piece of paper with writing on it. is to the left of a small house with a purple roof and a ceiling light fixture.. a small house with a purple roof and a ceiling light fixture. is to the right of a lion wearing a t-shirt, accompanied by a white piece of paper with writing on it.. a lion wearing a t-shirt, accompanied by a white piece of paper with writing on it. is to the left of and behind a square table with a square base and light fixture.. Tracking a square table with a square base and light fixture., the camera provides a dynamic view of its actions. The a square table with a square base and light fixture. heads to the left at 0.15. The a small house with a purple roof and a ceiling light fixture. heads right at 0.27 units. Moving forward at speedily 0.30, the a lion wearing a t-shirt, accompanied by a white piece of paper with writing on it. progresses. Yaw: sharply forward left, Pitch: horizontally level. Fully zoomed out The focal length is 30 mm. High screen-space ray tracing is used in the scene. High motion blur is used in the scene. The background view is Harvest. The flooring texture is Stone Floor. Animations are intentionally slowed down."
    After:
        "index": 499,
        "objects_caption": "Object caption: 3 objects: A lion wearing a t-shirt with white piece of paper with writing on it is to the left of a small house with a purple roof and a ceiling light fixture. The small house with a purple roof and a ceiling light fixture is to the right of a lion wearing a t-shirt with white piece of paper with writing on it. Lion is to the left of and behind a square table. The square table goes to the left in the screen. The a small house with a purple roof shifts right. The lion wearing a t-shit with paper moves forward at speedily",
        "background_caption": "Scene background: The landscape is Harvest.",
        "orientation_caption": "Camera orientation: forward left, leveled nicely.",
        "framing_caption": "Camera framing: Fully zoomed out",
        "animation_caption": "Camera animation: Track the square table with a square base and light fixture. Slow animation",
        "stage_caption": "Scene stage: The background view is Harvest. The flooring texture is Stone Floor.",
        "postprocessing_caption": "Post-processing effects: Strong motion blur and ray tracing",
        "caption": "There's a total of 3 objects: a square table with a square base and light fixture, lion wearing a t-shirt with white piece of paper with writing on it, and small house with a purple roof and a ceiling light fixture. Lion wearing a t-shirt is left of small house with a purple roof. Small house is to the right of a lion. Lion is left of and behind a square table with a square base. Camera should track the square table as it heads to the left. 
                    Small house moves right at 0.27 units. Moving forward at speedily is the lion. Camera is forward left and fully zoomed out. Btw scene has high screen-space ray tracing and motion blur. Background view is Harvest with Stone Floor texture. Animations are intentionally slowed down."
    
    Example 4:
        Before:
        "index": 495,
        "objects_caption": "Object caption: a house with a roof. is to the left of and in front of a man wearing a blue and black outfit.. a white Chevrolet Suburban SUV is to the right of and behind a man wearing a blue and black outfit.. a man wearing a blue and black outfit. is to the left of and in front of a white Chevrolet Suburban SUV. a brick and stone wall. is to the right of and behind a house with a roof..  The a man wearing a blue and black outfit. travels right at a rate of 0.32 per second. The a brick and stone wall. proceeds left at a speed of speedily 0.91. The a white Chevrolet Suburban SUV moves at swiftly 0.93 units/s towards the left. The a house with a roof. advances forward at quickly 0.70 units.",
        "background_caption": "Scene background: The landscape is White Cliff Top.",
        "orientation_caption": "Camera orientation: Align the camera to 330\u00b0 to the right, and adjust the pitch to 67 sharply downward.",
        "framing_caption": "Camera framing: Medium-wide angle Set the fov of the camera to 44 degrees. (43.00 mm focal length)",
        "animation_caption": "Camera animation: The camera pans alongside a house with a roof., capturing every move. Animations are intentionally slowed down.",
        "stage_caption": "Scene stage: The background setting is White Cliff Top. The ground is Running Track.",
        "postprocessing_caption": "Post-processing effects: Medium ambient occlusion is present in the scene. The scene is rendered with a mild screen-space ray tracing effect.",
        "caption": "a house with a roof. (size: 7) [a man wearing a blue and black outfit. - a man wearing a blue and black outfit. - 2] a brick and stone wall. (size: 0.5m) There is a a white Chevrolet Suburban SUV a house with a roof. is to the left of and in front of a man wearing a blue and black outfit.. a white Chevrolet Suburban SUV is to the right of and behind a man wearing a blue and black outfit.. a man wearing a blue and black outfit. is to the left of and in front of a white Chevrolet Suburban SUV. a brick and stone wall. is to the right of and behind a house with a roof.. The camera pans alongside a house with a roof., capturing every move. The a man wearing a blue and black outfit. travels right at a rate of 0.32 per second. The a brick and stone wall. proceeds left at a speed of speedily 0.91. The a white Chevrolet Suburban SUV moves at swiftly 0.93 units/s towards the left. The a house with a roof. advances forward at quickly 0.70 units. Align the camera to 330\u00b0 to the right, and adjust the pitch to 67 sharply downward. Medium-wide angle Set the fov of the camera to 44 degrees. (43.00 mm focal length) Medium ambient occlusion is present in the scene. The scene is rendered with a mild screen-space ray tracing effect. The background setting is White Cliff Top. The ground is Running Track. Animations are intentionally slowed down."
    After:
        "index": 495,
        "objects_caption": "Object caption: a house with a roof is to the left of and in front of a man wearing a blue and black outfit. There's also a white Chevrolet Suburban SUV to the right of and behind the man wearing black outfit. The man is left of and in front of a white Chevrolet Suburban SUV. The brick and stone wall is to the right of and behind the house. The man travels right at a rate of 0.32 per second. The stone wall proceeds left really fast. The white Chevrolet moves swiftly leftward. The house moves forward quickly too",
        "background_caption": "Scene background: The landscape is White Cliff Top.",
        "orientation_caption": "Camera orientation: Align camera right and adjust the pitch sharply downward. OR Camera captures most things and show downward",
        "framing_caption": "Camera framing: Medium-wide angle fov of the camera",
        "animation_caption": "Camera animation: The camera pans alongside the house with a roof",
        "stage_caption": "Scene stage: White Cliff Top backgroung and Running Track.",
        "postprocessing_caption": "Post-processing effects: Medium ambient occlusion is present in the scene. The scene is rendered with a mild screen-space ray tracing effect.",
        "caption": "a house with a roof, a man wearing a blue and black outfit, a brick and stone wall (size: 0.5m), and white Chevrolet Suburban SUV. a house with a roof is to the left of and in front of a man wearing a blue and black outfit. There's also a white Chevrolet Suburban SUV to the right of and behind the man wearing black outfit. The man is left of and in front of a white Chevrolet Suburban SUV. The brick and stone wall is to the right of and behind the house. The man travels right at a rate of 0.32 per second. The stone wall proceeds left really fast. The white Chevrolet moves swiftly leftward. The house moves forward quickly too. Align camera right and adjust the pitch sharply downward with camera capturing most things. White background and track floor."
    
    Below are captions that NEED to be shortened/simplified, and more human-like. Return an array of rewritten captions. 
    Process the input array and return a new array with rewritten captions in the same format.
    """

    model = setup_gemini()
    combinations = read_combinations()
    rewritten_combinations = rewrite_captions_in_batches(model, combinations, CONTEXT_STRING)
    write_to_file(rewritten_combinations)