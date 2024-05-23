
import os
import json
import tiktoken
from openai import OpenAI

from dotenv import load_dotenv

def rewrite_caption(caption_arr, context_string, max_tokens_for_completion): # caption is a string array
    load_dotenv()
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
        
    split_captions = [caption.split(', ') for caption in caption_arr]

    # Convert the list of lists into a string that maintains the structure
    captions_string = "[\n" + ",\n".join(
        "[" + ", ".join(f"'{line}'" for line in caption) + "]" for caption in split_captions
    ) + "\n]"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "user", "content": f"{context_string}\n\n{captions_string}"}
        ],
        temperature=1,
        max_tokens=max_tokens_for_completion,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Strip the surrounding brackets and commas from the string
    captions_content = response.choices[0].message.content.replace('[', '').replace(']', '').replace("',", '')

    # Split the string into a list of captions
    rewritten_captions_content = captions_content.split('\n')

    # Remove any empty strings from the list
    rewritten_captions_content = [caption for caption in rewritten_captions_content if caption]

    # Remove the double '' from the start and end of each caption
    rewritten_captions_content = [caption.strip("'") for caption in rewritten_captions_content]
    
    print("==== Captions rewritten by OpenAI ====")
    return rewritten_captions_content



def read_combinations_and_get_array_of_just_captions():
    # we want just the caption text and store in array
    with open('combinations.json') as file:
        data = json.load(file)
        combinations = data.get('combinations')
        captions = []
        for obj in combinations:
            caption = obj.get('caption')
            captions.append(caption)
        print("==== File read, captions extracted ====")
        return captions


def write_to_file(i, rewritten_captions):
    with open('combinations.json', 'r+') as file:
        data = json.load(file)
        
        combinations = data.get('combinations')

        j = 0
        while j < len(rewritten_captions):
            print("==> Rewriting caption: ", i + j)
            combinations[i + j]['caption'] = rewritten_captions[j]
            j += 1
        
        data['combinations'] = combinations

        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

    print("==== File captions rewritten, check file ====")


def estimate_tokens(text, encoding):
    return len(encoding.encode(text))


def rewrite_captions_in_batches(combinations, context_string):
    num_combinations = len(combinations)
    
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-16k")

    context_length = estimate_tokens(context_string, encoding)
    TOKEN_LIMIT = 16385
    INPUT_TOKEN_LIMIT = (TOKEN_LIMIT - context_length)//2

    starting_point = 0
    i = 0
    while i < num_combinations:
        captions_that_need_to_be_rewritten = []
        current_caption_length = 0

        # Gather captions until the token limit is reached
        while i < num_combinations:
            current_caption = combinations[i]
            caption_length = estimate_tokens(current_caption, encoding)

            if (current_caption_length + caption_length + context_length + 1000) >= INPUT_TOKEN_LIMIT:
                break

            captions_that_need_to_be_rewritten.append(current_caption)
            current_caption_length += caption_length
            print(f"Current Caption Length: {current_caption_length}, TOKEN_LIMIT: {INPUT_TOKEN_LIMIT - context_length}")
            i += 1

        # Calculate the max tokens available for completion
        max_tokens_for_completion = TOKEN_LIMIT//2
        rewritten_captions = rewrite_caption(captions_that_need_to_be_rewritten, context_string, max_tokens_for_completion)
        write_to_file(starting_point, rewritten_captions)
        starting_point = i


if __name__ == '__main__':
    CONTEXT_STRING = """
    Go through array of captions and make it sound more human. Chagne "directory" words like "bloom" or "pitch".
    Feel free to change/remove exact values like degrees. Instead of 32 degrees left you can say slightly to the left.
    Use synonyms/words to use. You can even remove some words/sentences. Rewritten caption should be at least 
    shorter by an entire sentence.

    examples:
    Before: "2ft Vehicle Mine GTA2 3d remake: A green and red spaceship with a circular design and a red button. 7 LOW POLY PROPS: a pink square with a small brown box and a stick on it, resembling a basketball court. Modified Colt 1911 Pistol is a gun LOW POLY PROPS is to the left of and behind Modified Colt 1911 Pistol. Modified Colt 1911 Pistol is to the right of and in front of LOW POLY PROPS. Vehicle Mine GTA2 3d remake is  and in front of LOW POLY PROPS. The view is set sharply downward, looking 189\u00b0 to the right. Set the focal length of the camera to 75 mm. Semi-close perspective  The panorama is Monbachtal Riverbank. The floor is Shell Floor. The scene transitions swiftly with enhanced animation speed."
    After: "Vehicle Mine GTA2 3d remake is a green and red spaceship with a circular design and a red button. 7 LOW POLY PROPS: a pink square with a small brown box and a stick on it, resembling a basketball court. Modified Colt 1911 Pistol is a gun LOW POLY PROPS is to the left of and behind Modified Colt 1911 Pistol. Modified Colt 1911 Pistol is to the right of and in front of LOW POLY PROPS. Vehicle Mine GTA2 3d remake is  and in front of LOW POLY PROPS. The view is set sharply downward, looking 189 degrees to the right. Semi-close perspective. The floor is Shell Floor. Scene transitions swiftly with enhanced animation speed."

    Before: "Dulal Das Test File (height: 5feet) is a tan leather recliner chair and ottoman. Stylized Apple = a pink apple or peach on a plate. Stylized Apple is to the left of Dulal Das Test File. Dulal Das Test File is to the right of Stylized Apple. The lens is oriented direct right, with a 30 forward tilt. Set the fov of the camera to 32 degrees. (61.00 mm focal length) Standard medium.  The scenery is Limehouse. The ground material is Gravel Floor. A standard animation speed is applied to the scene."
    After: "Dulal Das Test File is a tan leather recliner chair and ottoman. Stylized Apple is pink apple or peach on a plate. Stylized Apple is of Dulal Das Test File. Dulal Das Test File is right of Stylized Apple. The lens is oriented direct right, with a 30 forward tilt. Set the fov of the camera to 32 degrees. The scenery is Limehouse with ground material of Gravel Floor. A standard animation speed is applied to the scene."
    Another Alternate: "Dulal Das Test File is a tan leather recliner chair and ottoman. Stylized Apple is pink apple or peach on a plate. Stylized Apple is of Dulal Das Test File. Dulal Das Test File is right of Stylized Apple. The lens is oriented direct right, with a 30 forward tilt. Set the fov of the camera to be small amount. The scenery is Limehouse with ground material of Gravel Floor. A standard animation speed is applied to the scene."

    Before: "Best Japanese Curry is 1 and A bowl of stew with rice and meat. Apple is 7feet and an apple. Apple is  and behind Best Japanese Curry. Best Japanese Curry is  and in front of Apple. Direct the camera sharp right back, set tilt to steeply angled down. The focal length is 29 mm. Taking in the whole scene. The scene has a noticeable bloom effect. Motion blur is set to medium intensity in the scene. The backdrop is Pump House. The floor texture is Wood Plank Wall. The scene moves with a relaxed animation speed."
    After: "Best Japanese Curry is a bowl of stew with rice and meat. Apple is an apple placed behind Best Japanese Curry. Best Japanese Curry is in front of Apple. The camera is sharply angled right and steeply downward, capture the whole scene. Subtle bloom effect, and the motion blur is set to medium intensity. Background is Pump House with a wood plank floor. Relaxed animation speed."

    Only return the rewritten caption for each sentence as a list/array of strings seperated by commas. Do not return anything else not even an intro just the array of the rewritten captions.
    """

    combinations = read_combinations_and_get_array_of_just_captions()
    rewritten_captions = rewrite_captions_in_batches(combinations, CONTEXT_STRING)

