
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

    """
    sometimes we get this:
    [['2feet シナイモツゴ 雑種 ♂ Topmouth Gudgeon', "P. pumila x parva: a fish next to a Rubik's cube. A 0.5meters Dragon Zok - Herculoids is a yellow dragon with wings and horns. The Mokey is 0.5meters short and a black and white Mickey Mouse teddy bear. Horse = a horse Horse is to the left of and behind Mokey. Horse is to the left of and in front of Dragon Zok - Herculoids. シナイモツゴ 雑種 ♂ Topmouth Gudgeon", 'P. pumila x parva is to the left of and behind Mokey. シナイモツゴ 雑種 ♂ Topmouth Gudgeon', 'P. pumila x parva is  and in front of Dragon Zok - Herculoids. The lens is oriented greatly to the right front', 'with a slightly downward tilt. The camera has a 87 degree FOV. (18.00 mm focal length) Extremely zoomed out  The view is Studio Small. The flooring material is Rock Pitted Mossy. A highly accelerated animation speed is applied.']
    
    We want to turn it into this: 
    We want all of these strings within each sub-array to be joined into a single string 
    ["2feet シナイモツゴ 雑種 ♂ Topmouth Gudgeon: P. pumila x parva is a fish next to a Rubik's cube. Dragon Zok - Herculoids is a yellow dragon with wings and horns. Mokey is a black and white Mickey Mouse teddy bear. Horse is to the left of and behind Mokey. Horse is to the left of and in front of Dragon Zok - Herculoids. P. pumila x parva is to the left of and behind Mokey. P. pumila x parva is in front of Dragon Zok - Herculoids. The camera is oriented greatly to the right front with a slightly downward tilt. The camera has a 87 degree field of view. The view is Studio Small with Rock Pitted Mossy flooring. The scene has a highly accelerated animation speed."]   
    """

    # we have an array like this [["caption1"], ["caption2"], ["caption3"]]
    # but sometimes within each ["caption1"] there are multiple strings, we want to join them
    split_captions = [', '.join(caption) for caption in split_captions]
    

    print("THESE ARE THE SPLIT CAPTIONS: ", split_captions)

    """
    split_captions = [
        ["A green and red spaceship with a circular design and a red button is a 2ft Vehicle Mine GTA2 3d remake."],
        ["LOW POLY PROPS is a pink square with a small brown box and a stick on it", "resembling a basketball court."],
        ["Modified Colt 1911 Pistol is a gun."]
    ]
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "user", "content": f"{context_string}\n\n{split_captions}"}
        ],
        temperature=1,
        max_tokens=max_tokens_for_completion,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Strip the surrounding brackets and commas from the string
    captions_content = response.choices[0].message.content

    print(captions_content)
    """
    sometimes the captions_content will look like this:
    ["The Box is a small wooden and metal chest with a lock, a hinged lid, a key, and a map on it. Incensário de Gato is a cat sitting on a hanging green leaf. Low Poly Bedroom Set includes a couch, a pink and blue chair, a bed with a laptop, a furniture set, a row of blocks, multicolored paper pieces, and a flying plane. Low Poly Bedroom Set is positioned to the right of Incensário de Gato and Incensário de Gato is positioned to the left of Low Poly Bedroom Set. The Box is positioned to the left of Low Poly Bedroom Set and behind it. The camera is tilted slightly downward and rotated to the left. The scene is set in Orbita with a wood plank wall floor. The animation speed is medium."],
    ["The scene includes a rusty tank and a train engine. The camera is positioned facing downward and slightly to the left but towards the back. The scene features a subtle bloom effect, a subtle screen-space ray tracing effect, and a medium motion blur. The background view is Skidpan, and the ground material is Wood Stone Pathway. The animation speed is medium."],
    ["The HELL ARENA is composed of a dragon head, a lava-filled volcano, and a spiked lava bowl with a large flaming rock. The camera is tilted downward and looking slightly to the right. The scene is set in Belfast Open Field with a rock stage material. The animation speed is fast."],
    ["The scene features a rock with various objects like a piece of bread, a ruler, and a credit card. Ship's Telegraph Single Handled is a clock tower with a brass meter and a gas meter on a pedestal. Female Doctor [LowPoly] Asset is a person flying a blue kite. Female Doctor [LowPoly] Asset is positioned to the right of Fracture Surface - Location D, and Fracture Surface - Location D is positioned to the left of Female Doctor [LowPoly] Asset. The camera is angled left forward with a downward tilt. The scene is set in Air Museum Playground with a Worn Corrugated Iron stage texture. The animation speed is rapid."],
    ["The Zombie Virus (Fictional) is represented by a Coronavirus - Preview No. 1. The camera is angled downward and flat to the left, capturing a broad viewpoint. The scene features a high bloom effect, a medium ambient occlusion effect, and no screen-space ray tracing effect. The background environment is Adams Place Bridge with a Grooved Concrete Driveway ground. The animation speed is medium."]

    We want to turn it into this ["caption1", "caption2", "caption3"]
    """

    # if "],\n[" in captions_content:
    #     # turn it into an array of [[], [], []]
    #     cleaned_captions_content = captions_content.replace('\n', '')
    #     rewritten_captions_content = json.loads(cleaned_captions_content)

    #     # then turn it into ["caption1", "caption2", "caption3"]
    #     rewritten_captions_content = [caption[0] for caption in rewritten_captions_content]
    # else:
    #     cleaned_captions_content = captions_content.replace('\n', '')
    #     rewritten_captions_content = json.loads(cleaned_captions_content)

    # Cleaning the response content
    captions_content = captions_content.strip()

    # Check if the response is a single valid JSON array
    try:
        # Ensure the response is a single valid JSON array
        if captions_content.startswith('[') and captions_content.endswith(']'):
            # Remove trailing commas and square brackets from nested arrays
            captions_content = captions_content.replace('],\n[', '],[')
            cleaned_captions_content = captions_content
        else:
            # Add brackets to make it a JSON array
            cleaned_captions_content = f"[{captions_content}]"
        
        """
        Problematic content: ["Painters Dance is a man in a black and white suit and also depicted as a robot. The view is sharply downward, looking rear left. Camera has a focal length of 82 mm. Up-close perspective with strong glow effect. No screen-space ray tracing. Low motion blur. Background is Belvedere with Aerial Rocks flooring. Faster animation speed.",
        "The Liquid Container is a beverage holder with various items. Wooden Rocking Chair is a modern chair with a wooden couch/sofa/bench nearby. Liquid Container is behind Wooden Rocking Chair. Antique Sofa is left of Wooden Rocking Chair. Camera angle is deep right and slightly forward. Wide shot with moderate glow effect. Medium occlusion effect. No ray tracing. Kloofendal d Misty Pure Sky view with Rock Wall flooring. Medium animation speed.",
        ]
        """

        # remove "," if it is right before a ]
        cleaned_captions_content = cleaned_captions_content.replace('",\n]', '"\n]')
        
        rewritten_captions_content = json.loads(cleaned_captions_content)
        
        # Check if we have nested lists and flatten if necessary
        if isinstance(rewritten_captions_content[0], list):
            rewritten_captions_content = [item for sublist in rewritten_captions_content for item in sublist]

    except json.JSONDecodeError as e:
        print("JSONDecodeError:", e)
        print("Problematic content:", captions_content)
        rewritten_captions_content = []

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
    # TOKEN_LIMIT = 32000
    TOKEN_LIMIT_OUTPUT = 4096
    INPUT_TOKEN_LIMIT = 4096 - context_length

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
        rewritten_captions = rewrite_caption(captions_that_need_to_be_rewritten, context_string, TOKEN_LIMIT_OUTPUT)
        write_to_file(starting_point, rewritten_captions)
        starting_point = i


if __name__ == '__main__':
    CONTEXT_STRING = """
    examples:
    Before: "2ft Vehicle Mine GTA2 3d remake: A green and red spaceship with a circular design and a red button. 7 LOW POLY PROPS: a pink square with a small brown box and a stick on it, resembling a basketball court. Modified Colt 1911 Pistol is a gun LOW POLY PROPS is to the left of and behind Modified Colt 1911 Pistol. Modified Colt 1911 Pistol is to the right of and in front of LOW POLY PROPS. Vehicle Mine GTA2 3d remake is  and in front of LOW POLY PROPS. The view is set sharply downward, looking 189\u00b0 to the right. Set the focal length of the camera to 75 mm. Semi-close perspective  The panorama is Monbachtal Riverbank. The floor is Shell Floor. The scene transitions swiftly with enhanced animation speed."
    After: "Vehicle Mine GTA2 3d remake is a green and red spaceship with a circular design and a red button. LOW POLY PROPS is pink square with a small brown box and a stick on it, resembling a basketball court. Modified Colt 1911 Pistol is a gun LOW POLY PROPS is to the left of and behind Modified Colt 1911 Pistol. Modified Colt 1911 Pistol is to the right of and in front of LOW POLY PROPS. Vehicle Mine GTA2 3d remake is  and in front of LOW POLY PROPS. The view is set sharply downward and looking 189 degrees to the right. Somewhat close perspective and the floor is a Shell Floor. Scene transitions swiftly with enhanced animation speed."

    Before: "Dulal Das Test File (height: 5feet) is a tan leather recliner chair and ottoman. Stylized Apple = a pink apple or peach on a plate. Stylized Apple is to the left of Dulal Das Test File. Dulal Das Test File is to the right of Stylized Apple. The lens is oriented direct right, with a 30 forward tilt. Set the fov of the camera to 32 degrees. (61.00 mm focal length) Standard medium.  The scenery is Limehouse. The ground material is Gravel Floor. A standard animation speed is applied to the scene."
    After: "Dulal Das Test File is a tan leather recliner chair and ottoman. Stylized Apple is pink apple or peach on a plate. Dulal Das Test File is right of Stylized Apple. The lens is oriented direct right, with a slight forward tilt. Set the field of view of the camera to 32 degrees. The scenery is Limehouse with ground material of Gravel Floor. A normal animation speed for the scene."

    Before: "Best Japanese Curry is 1 and A bowl of stew with rice and meat. Apple is 7feet and an apple. Apple is  and behind Best Japanese Curry. Best Japanese Curry is  and in front of Apple. Direct the camera sharp right back, set tilt to steeply angled down. The focal length is 29 mm. Taking in the whole scene. The scene has a noticeable bloom effect. Motion blur is set to medium intensity in the scene. The backdrop is Pump House. The floor texture is Wood Plank Wall. The scene moves with a relaxed animation speed."
    After: "Best Japanese Curry is a bowl of stew with rice and meat. Apple is an apple placed behind Best Japanese Curry. Best Japanese Curry is in front of Apple. The camera is very angled right and very down, make sure to capture whole scene. Subtle glow effect, and medium blur when movement. Background is Pump House with a wood plank floor. Slow animation speed maybe"

    Above are caption example before and after. Change complex director-like words like "bloom" or "pitch" to more common synonyms.
    Feel free to change/remove exact values like degrees. Instead of 32 degrees left you can say slightly to the left. 

    Do the following: 
    - REDUCE the complexity of the captions. 
    - REDUCE the number of too specific values in the captions (29mm or 50 degrees, that type of stuff we don't need to include every time). 
    - Use more common synonyms of words (replace bloom, inclusion, those complex words with everyday words).
    - each caption must be shorter than it's original.
    - Ensure that there are no unnecesaary quotes or square brackets in the captions.

    Below are captions that NEED to be SHORTENED/SIMPLIFIED and human prompted-like. Return an array of rewritten captions.
    You will be give an array of captions something like this: [["caption1"], ["caption2"], ["caption3"]]
    PLEASE REWRITE THE CAPTIONS BASED ON EXAMPLES AND INSTRUCTIONS ABOVE AND FORMAT YOUR RESPONSE EXACTLY THIS: ["caption1",\n "caption2",\n "caption3"].

    So like this (please wrap the captions in "" NOT ''):
    ["A blue and yellow cylinder resembling a grasshopper, a beetle, and a cicada. A wooden stick and a business card. A small white dragon with pink wings. The wooden stick and business card are in front of the cylinder. The cylinder is behind the wooden stick and business card.",
    "A vending machine with purple lights and a wooden cabinet featuring a glass top and a sign. The camera is angled sharply downward and rotated 173°. The camera has a 22 mm focal length. It captures an extremely wide landscape. The scene is rendered with a moderate bloom effect.",
    "A woman with long red hair wearing a red hooded hat. The camera is angled slightly downward and rotated 173°. The camera has a 22 mm focal length. It captures an extremely wide landscape. The setting is Medieval Cafe. The flooring texture is Double Brick Floor. The scene features an enhanced animation tempo."]
    """

    combinations = read_combinations_and_get_array_of_just_captions()
    rewritten_captions = rewrite_captions_in_batches(combinations, CONTEXT_STRING)

