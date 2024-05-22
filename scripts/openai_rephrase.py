import json
from openai import OpenAI


CONTEXT_STRING = """
Go through array of captions and make it sound more human. Think in terms of prompting a 
humans would not commonly write specific values, nor use words "director" words like "bloom" or "pitch". 
Easier synonyms/words to use. Or like some variations should not ha to know to say for the average 
person simply prompting. Just make it sounds like a human prompted it. You can even remove some words/sentences. 
Rewritten caption should be at least shorter by an entire sentence and remove coordinates or entire sentences/words if necessary.

examples:
Before: "2ft Vehicle Mine GTA2 3d remake: A green and red spaceship with a circular design and a red button. 7 LOW POLY PROPS: a pink square with a small brown box and a stick on it, resembling a basketball court. Modified Colt 1911 Pistol is a gun LOW POLY PROPS is to the left of and behind Modified Colt 1911 Pistol. Modified Colt 1911 Pistol is to the right of and in front of LOW POLY PROPS. Vehicle Mine GTA2 3d remake is  and in front of LOW POLY PROPS. The view is set sharply downward, looking 189\u00b0 to the right. Set the focal length of the camera to 75 mm. Semi-close perspective  The panorama is Monbachtal Riverbank. The floor is Shell Floor. The scene transitions swiftly with enhanced animation speed."
After: "Vehicle Mine GTA2 3d remake is a green and red spaceship with a circular design and a red button. 7 LOW POLY PROPS: a pink square with a small brown box and a stick on it, resembling a basketball court. Modified Colt 1911 Pistol is a gun LOW POLY PROPS is to the left of and behind Modified Colt 1911 Pistol. Modified Colt 1911 Pistol is to the right of and in front of LOW POLY PROPS. Vehicle Mine GTA2 3d remake is  and in front of LOW POLY PROPS. The view is set sharply downward, looking 189 degrees to the right. Semi-close perspective. The floor is Shell Floor. Scene transitions swiftly with enhanced animation speed."

Before: "Dulal Das Test File (height: 5feet) is a tan leather recliner chair and ottoman. Stylized Apple = a pink apple or peach on a plate. Stylized Apple is to the left of Dulal Das Test File. Dulal Das Test File is to the right of Stylized Apple. The lens is oriented direct right, with a 30 forward tilt. Set the fov of the camera to 32 degrees. (61.00 mm focal length) Standard medium.  The scenery is Limehouse. The ground material is Gravel Floor. A standard animation speed is applied to the scene."
After: "Dulal Das Test File is a tan leather recliner chair and ottoman. Stylized Apple is pink apple or peach on a plate. Stylized Apple is of Dulal Das Test File. Dulal Das Test File is right of Stylized Apple. The lens is oriented direct right, with a 30 forward tilt. Set the fov of the camera to 32 degrees. The scenery is Limehouse with ground material of Gravel Floor. A standard animation speed is applied to the scene."

Before: "Best Japanese Curry is 1 and A bowl of stew with rice and meat. Apple is 7feet and an apple. Apple is  and behind Best Japanese Curry. Best Japanese Curry is  and in front of Apple. Direct the camera sharp right back, set tilt to steeply angled down. The focal length is 29 mm. Taking in the whole scene. The scene has a noticeable bloom effect. Motion blur is set to medium intensity in the scene. The backdrop is Pump House. The floor texture is Wood Plank Wall. The scene moves with a relaxed animation speed."
After: "Best Japanese Curry is a bowl of stew with rice and meat. Apple is an apple placed behind Best Japanese Curry. Best Japanese Curry is in front of Apple. The camera is sharply angled right and steeply downward, capture the whole scene. Subtle bloom effect, and the motion blur is set to medium intensity. Background is Pump House with a wood plank floor. Relaxed animation speed."

Only return the rewritten caption for each sentence as a list/array of strings seperated by commas. Do not return anything else not even an intro just the array of the rewritten captions.
"""
TOKEN_LIMIT = 16000 - len(CONTEXT_STRING) - 1000

client = OpenAI(
    api_key="",
)

def rewrite_caption(caption_arr, context_string): # caption is a string array
    # we need to turn caption to just a large string separated by commas cause rn it's an array
    captions_string = ', '.join(caption for caption in caption_arr)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "user", "content": f"{context_string}\n\n{captions_string}"}
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    rewritten_caption = response['choices'][0]['message']['content']

    print(f"Rewritten captions: {rewritten_caption}")


def read_combinations_and_get_array_of_just_captions():
    # we want just the caption text and store in array
    with open('combinations.json') as file:
        data = json.load(file)
        combinations = data.get('combinations')
        captions = []
        for obj in combinations:
            caption = obj.get('caption')
            captions.append(caption)
        return captions


combinations = read_combinations_and_get_array_of_just_captions()
num_combinations = len(combinations)

rewritten_captions = []
captions_that_need_to_be_rewritten = []
current_caption_length = 0

for i in range(num_combinations):
    current_caption = combinations[i]
    current_caption_length += len(current_caption)
    captions_that_need_to_be_rewritten.append(current_caption)

    if current_caption_length > TOKEN_LIMIT:
        while current_caption_length > TOKEN_LIMIT:
            current_caption_length -= len(captions_that_need_to_be_rewritten.pop())

    rewritten_caption = rewrite_caption(captions_that_need_to_be_rewritten, CONTEXT_STRING)
    current_caption_length = 0
    rewritten_captions = []
