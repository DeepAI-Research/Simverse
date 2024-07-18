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

def write_to_file(rewritten_combinations, mode='w'):
    with open("./get_captions_processed.json", mode) as file:
        if mode == 'a':
            file.write(',\n')
        json.dump(rewritten_combinations, file, indent=4)
    print(f"==== Batch of {len(rewritten_combinations)} combinations written to file ====")

def rewrite_captions_in_batches(model, combinations, context_string):
    batch_size = 5
    all_rewritten_combinations = []
    for i in range(0, len(combinations), batch_size):
        caption_batch = combinations[i : i + batch_size]
        rewritten_captions = rewrite_caption(model, caption_batch, context_string)
        
        # Write this batch to the file
        write_mode = 'w' if i == 0 else 'a'
        write_to_file(rewritten_captions, mode=write_mode)
        
        all_rewritten_combinations.extend(rewritten_captions)
    return all_rewritten_combinations

if __name__ == "__main__":
    CONTEXT_STRING_1 = """
    Here are some examples of a task I want you to do which involves rewriting captions.

    Hey, I need you to rewrite these scene descriptions super casually.

    Example 1:
    Before:
        "index": 0,
        "caption": "Mario Bros model compatible with 3ds Max, Maya, Blender, and other modeling and animation software. = Mario Bros model compatible with 3ds Max, Maya, Blender, and other modeling and animation software.  The camera pans alongside Mario Bros model compatible with 3ds Max, Maya, Blender, and other modeling and animation software., capturing every move. The Mario Bros model compatible with 3ds Max, Maya, Blender, and other modeling and animation software. shifts to the right at quickly 0.29 each second. Direct the camera far right front, set tilt to mildly downward. Full perspective Set the fov of the camera to 57 degrees. (32.00 mm focal length) The scene has a moderate bloom effect. No screen-space ray tracing is used in the scene. The background scene is Brown Photostudio. The floor material is Medieval Blocks. The scene is rendered with a moderate animation speed of 83%."
        "objects_caption": "Object caption:   The Mario Bros model compatible with 3ds Max, Maya, Blender, and other modeling and animation software. shifts to the right at quickly 0.29 each second.",
        "background_caption": "Scene background: The landscape is Brown Photostudio 07.",
        "orientation_caption": "Camera orientation: Direct the camera far right front, set tilt to mildly downward.",
        "framing_caption": "Camera framing: Full perspective Set the fov of the camera to 57 degrees. (32.00 mm focal length)",
        "animation_caption": "Camera animation: The camera pans alongside Mario Bros model compatible with 3ds Max, Maya, Blender, and other modeling and animation software., capturing every move. The scene is rendered with a moderate animation speed of 83%.",
        "stage_caption": "Scene stage: The background scene is Brown Photostudio. The floor material is Medieval Blocks.",
        "postprocessing_caption": "Post-processing effects: The scene has a moderate bloom effect. No screen-space ray tracing is used in the scene.",
    After:
        "index": 0,
        "caption": "Camera moves around Mario Bros model capturing every move as it moves right quickly. The camera is placed far right front pointing abit downward. Show full perspective fov. Scene has a normal brightness with no screen-space ray tracing. The background scene is Brown Photostudio with Medieval Blocks floor."
        "objects_caption": "Object caption: Mario Bros model shifts to the right quickly each second.",
        "background_caption": "Scene background: The landscape is Brown Photostudio 07.",
        "orientation_caption": "Camera orientation: The camera is far forward and right and pointing slightly downward.",
        "framing_caption": "Camera framing: Camera should show full fov",
        "animation_caption": "Camera animation: The camera shows the Mario Bros model as it moves. calm animation speed.",
        "stage_caption": "Scene stage: The background scene is Brown Photostudio with Medieval-like floor",
        "postprocessing_caption": "Post-processing effects: Scene overall has normal brightness effect. No screen-space ray tracing is used in the scene.",

    Example 2: 
    Before:
        "index": 1,
        "caption": "A massive a white ornate corbel and column. is a white ornate corbel and column.  Tracking a white ornate corbel and column., the camera provides a dynamic view of its actions. The a white ornate corbel and column. drifts forward at brisk 0.46 units. Yaw: flat left, Pitch: 47 degrees downward. Balanced perspective The field of view is 38 degrees. (50.00 mm focal length) Bloom effect is set to high intensity. The scene is rendered with a strong ambient occlusion effect. The scene is Theater. The ground is Coast Sand. Fast animation of 141% is used in the scene."
        "objects_caption": "Object caption:   The a white ornate corbel and column. drifts forward at brisk 0.46 units.",
        "background_caption": "Scene background: The landscape is Theater 01.",
        "orientation_caption": "Camera orientation: Yaw: flat left, Pitch: 47 degrees downward.",
        "framing_caption": "Camera framing: Balanced perspective The field of view is 38 degrees. (50.00 mm focal length)",
        "animation_caption": "Camera animation: Tracking a white ornate corbel and column., the camera provides a dynamic view of its actions. Fast animation of 141% is used in the scene.",
        "stage_caption": "Scene stage: The scene is Theater. The ground is Coast Sand.",
        "postprocessing_caption": "Post-processing effects: Bloom effect is set to high intensity. The scene is rendered with a strong ambient occlusion effect.",
    After:
        "index": 1,
        "caption": "Make the camera track the massive white ornate corbel and column as it moves forward quickly and make camera flat left with downward pointing. The scene is Theater with Coast Sand ground"
        "objects_caption": "Object caption: The a white ornate corbel and column moves forward quick",
        "background_caption": "Scene background: The landscape is Theater 01.",
        "orientation_caption": "Camera orientation: flat left with kinda downward pitch",
        "framing_caption": "Camera framing: even field of view",
        "animation_caption": "Camera animation: Tracking a white ornate corbel and column. Camera provides dynamic view of its actions in a fast paced animation.",
        "stage_caption": "Scene stage: The scene is Theater and the ground is Coast Sand.",
        "postprocessing_caption": "Post-processing effects: high intense lighting plus strong ambient occlusion effect.",

    Hey, I need you to rewrite these scene descriptions super casually, and simplifiy and remove complex words or values.
    MUST capture all important details like objects in scene, position of objects in scene and relative to each other, movement, background stuff and more!
    Below are groups of captions that NEED to be rewritten by the guidelines. Be direct as possible.
    Rewrite the following captions and return them in the same format.
    """


    CONTEXT_STRING_2 = """
    Hey, I need you to rewrite these scene descriptions super casually, like you're telling a friend about a cool video idea. Here's what to do:

    1. Keep it super simple and chatty. No tech talk at all.
    2. Keep the main objects and where they are, but say it in a really casual way.
    3. Describe the camera and scene in a way anyone can picture, like "the camera's checking out the whole scene" instead of specific angles.
    4. Mention the overall vibe of the scene - what it looks like, feels like.
    5. If stuff is moving, just say it's moving without any exact speeds.
    6. Keep the important parts of the background and effects, but say it in a really laid-back way.
    7. Don't use ANY numbers. Use words like "big", "small", "close", "far" instead.
    8. It's cool to leave out details that aren't super important.

    Most importantly: Keep the JSON structure exactly the same, just rewrite the content of each field.

    Example:
    Original:
    {
        "index": 0,
        "objects_caption": "Object caption: The blue and green plane and umbrella shifts to the forward at regular 0.07 each second.",
        "background_caption": "Scene background: The landscape is Park Parking.",
        "orientation_caption": "Camera orientation: Pitch: horizontally level, Yaw: far left front.",
        "framing_caption": "Camera framing: Zoomed in The camera has a 17 degree FOV. (117.00 mm focal length)",
        "animation_caption": "Camera animation: Animations move at an expedited speed in the scene.",
        "stage_caption": "Scene stage: The background environment is Park Parking. The flooring texture is Red Brick Plaster Patch.",
        "postprocessing_caption": "Post-processing effects: Extreme bloom is used in the scene. The scene is rendered with a moderate ambient occlusion effect. High motion blur is used in the scene.",
        "caption": "The blue and green plane and umbrella reaches 3feet in height. The blue and green plane and umbrella shifts to the forward at regular 0.07 each second. Pitch: horizontally level, Yaw: far left front. Zoomed in The camera has a 17 degree FOV. (117.00 mm focal length) Extreme bloom is used in the scene. The scene is rendered with a moderate ambient occlusion effect. High motion blur is used in the scene. The background environment is Park Parking. The flooring texture is Red Brick Plaster Patch. Animations move at an expedited speed in the scene."
    }

    Rewritten:
    {
        "index": 0,
        "objects_caption": "Object caption: There's this cool plane and umbrella combo, blue and green, moving forward slowly.",
        "background_caption": "Scene background: We're in a park parking lot.",
        "orientation_caption": "Camera orientation: The camera's looking straight ahead, but from the far left.",
        "framing_caption": "Camera framing: It's zoomed in pretty close.",
        "animation_caption": "Camera animation: Everything's moving pretty fast.",
        "stage_caption": "Scene stage: We're in a park parking lot with this red brick floor that's got some patches.",
        "postprocessing_caption": "Post-processing effects: The scene's super bright and glowy, with some blurring when things move.",
        "caption": "awesome blue and green plane with an umbrella, and it's slowly moving forward. The camera's zoomed in close, watching it from the left side. Everything's moving pretty fast, and the whole scene is super bright and glowy. We're in a park parking lot, and the ground is this cool red brick with some patches. When stuff moves, it gets all blurry. It's like a super stylized, fast-paced shot in a quirky movie!"
    }

    Remember, keep it super casual and you can sound super lazy. MUST capture all important details like objects in scene, movement, and maybe background stuff.
    Below are groups of captions that NEED to be rewritten by the guidelines. Btw stop using intros like "Picture this" or stupid stuff. Just cut to the chase.

    Rewrite the following captions and return them in the same format.
    """

    CONTEXT_STRING_3  = """
    Hey, I need you to rewrite these scene descriptions super casually and super direct.

    Example:
    Original:
    {
        "index": 0,
        "caption": "The blue and green plane and umbrella reaches 3feet in height. The blue and green plane and umbrella shifts to the forward at regular 0.07 each second. Pitch: horizontally level, Yaw: far left front. Zoomed in The camera has a 17 degree FOV. (117.00 mm focal length) Extreme bloom is used in the scene. The scene is rendered with a moderate ambient occlusion effect. High motion blur is used in the scene. The background environment is Park Parking. The flooring texture is Red Brick Plaster Patch. Animations move at an expedited speed in the scene."
        "objects_caption": "Object caption: The blue and green plane and umbrella shifts to the forward at regular 0.07 each second.",
        "background_caption": "Scene background: The landscape is Park Parking.",
        "orientation_caption": "Camera orientation: Pitch: horizontally level, Yaw: far left front.",
        "framing_caption": "Camera framing: Zoomed in The camera has a 17 degree FOV. (117.00 mm focal length)",
        "animation_caption": "Camera animation: Animations move at an expedited speed in the scene.",
        "stage_caption": "Scene stage: The background environment is Park Parking. The flooring texture is Red Brick Plaster Patch.",
        "postprocessing_caption": "Post-processing effects: Extreme bloom is used in the scene. The scene is rendered with a moderate ambient occlusion effect. High motion blur is used in the scene.",
    }

    Rewritten:
    {
        "index": 0,
        "caption": "blue and green plane with an umbrella, and it's slowly moving forward. camera zoomed in close, from the left side. Everything moves fast, scene is super bright and glowy. In park parking lot, and the ground is red brick with some patches. When stuff moves, blurry. fast-paced."
        "objects_caption": "Object caption: plane and umbrella combo, blue and green, moving forward slow.",
        "background_caption": "Scene background: park parking lot.",
        "orientation_caption": "Camera orientation: camera looks straight ahead, far left.",
        "framing_caption": "Camera framing: zoomed in close.",
        "animation_caption": "Camera animation: animation moves pretty fast.",
        "stage_caption": "Scene stage: In a park parking lot with red brick floor that's got some patches.",
        "postprocessing_caption": "Post-processing effects: The scene's super bright and glowy, with some blurring when things move.",
    }

    MUST capture all important details like objects in scene, position of objects in scene and relative to each other, movement, background stuff and more!
    Below are groups of captions that NEED to be rewritten by the guidelines. Be direct as possible.
    Rewrite the following captions and return them in the same format.
    """

    model = setup_gemini()
    combinations = read_combinations()
    rewritten_combinations = rewrite_captions_in_batches(model, combinations, CONTEXT_STRING_1)
    write_to_file(rewritten_combinations)