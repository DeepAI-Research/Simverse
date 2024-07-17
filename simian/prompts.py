import os
import json
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
MODEL = "gemini-1.5-pro"

OBJECTS_PROMPT = """
    Extract the objects, background, and ground from the scene prompt and return as an array (make the last two the background and ground.

    Examples:
    
    "caption": "The camera is behind and to the right, pointing down. The scene contains Star Wars lightsabers with red and blue blades, a small town, a white box that looks like a refrigerator, Samsung Galaxy earbuds in their case, and a white piece of paper. The earbuds are behind the town and the piece of paper, the town is behind the paper, the paper is to the left of the box. Make all objects move slowly in their own direction: the lightsabers to the right, the town forward, the box right, the earbuds forward and the paper right. Keep the camera on the town. The background is Kloppenheim Pure Sky and the floor is Painted Worn Brick.",
    ["Star Wars lightsabers", "a small town", "a box", "earbuds", "piece of paper", "Kloppenheim 01 (Pure Sky)", "Painted Worn Brick"]
    Kloppenheim is the background while the painted is the ground/stage. 

    "caption": "A huge shark tooth, some wood, and a rock with ice are right behind a blue and white helmet with a beetle design. Camera follows the helmet as it moves. Shark tooth, wood, and rock move left slowly. The helmet moves right slowly. Camera is tilted down a bit and facing right. Tight FOV. Scene is bright and blurry. Background is Greenwich Park with a concrete rock path. Animation is fast.",
    ["A shark tooth", "some wood", "a rock with ice", "blue and white helmet", "Greenwich Park", "concrete rock path"]

    "caption": "A hedgehog is in the scene with a campfire that has marshmallows and a cake behind it. A sword is behind the hedgehog and to the right of a clock, brass sculpture, hooks, and a lock. A wall with a painting, a pot, and a statue is in front of the sword.  Camera is pointing down and left. Full FOV. Scene has some brightness, low shadow detail, and very blurry.  Background is Hochsal Forest with a cobblestone floor. Animation is a bit fast.",
    ["hedgehog", "campfire that has marshmallows", "cake", "sword", "clock", "brass sculpture", "hooks", "lock", "painting", "pot", "statue", "Hochsal Forest", "cobblestone floor"]

    include descriptions of the objects like if it says "black and white arrow" don't just say arrow include the description of that object.
    Here is the caption:
"""

OBJECTS_JSON_PROMPT = """
Ok so I want to place objects in a 3D scene, imagine a 3x3 grid 

0 1 2
3 4 5
6 7 8

the 6,7,8 part being the "front" where we assume the camera sees first. 
We want to split the caption into its respective descriptive objects (ONLY OBJECTS NOT background or ground/stage). We then want to generate a JSON which includes the objects, their placement, movement, camera_follow and all those attributes. For example, objects that are ontop of each other have the same index placement as a result.

Here are the speed "guidlines":

Something moderate/average/normal speed is around = 0.25-0.5
Something fast, quick, rapid, swift is around = 0.5

Here are scale guidlines:
Something tiny/mini/extra small is around = 0.25
Something small/undersized/smaller is around 0.5
Something medium/normal/average is around 0.75
Something medium-large/considerable is around 1.5
Something large/big/tall is around 2.25
Something huge/towering/giant is around 3.0

Examples:


Example 1: 

Prompt/caption: There's a small house and a modern white house in the scene. The small house is to the left of the modern house. The small house moves to the right at a moderate speed and the modern house moves backward. The camera should smoothly follow the movement of the modern house. Make the camera 325 degrees to the right, slightly tilted. The backdrop is Driving School and the flooring is Rock Ground. Apply a medium ambient occlusion and high ray tracing. Add a slight blur effect.

"objects": [
        {
            "name": "a small house with a roof, chimney, and insulation",
            "uid": "42cd3cd73892469492aa8e4bddbeed84",
            "description": "a small house with a roof, chimney, and insulation",
            "placement": 4,
            "from": "cap3d",
            "scale": {
                "factor": 0.25,
                "name": "tiny",
                "name_synonym": "petite"
            },
            "movement": {
                "direction": "right",
                "speed": 0.12043596124471068
            },
        },
        {
            "name": "a modern, white house surrounded by palm trees and plants",
            "uid": "d9ec8eb389e54dbdbfc06a44dab0f1ff",
            "description": "a modern, white house surrounded by palm trees and plants",
            "placement": 1,
            "from": "cap3d",
            "scale": {
                "factor": 1.5,
                "name": "medium-large",
                "name_synonym": "medium-large"
            },
            "movement": {
                "direction": "backward",
                "speed": 0.13079011338247018
            },
            "camera_follow": {
                "follow": true
            },
        }
    ]

Example 2: 

Prompt/caption: A building with a clock tower, a ferris wheel, and a boat, a white ring, a red and pink square, a pink alien toy, and a black teddy bear wearing a hat are in the scene. The ring is to the right of the building. The alien is to the left of the square and to the right of the teddy bear.  The building is to the left of and behind the square and behind the alien. The building moves left, the ring moves backward, the square moves left, the alien moves forward, and the teddy bear moves right.  The camera follows the teddy bear. Camera is facing backward and angled forward.  The scene has a normal blur effect.

"objects": [
        {
            "name": "a building featuring a clock tower, staircase, ferris wheel, and a floating boat nearby",
            "uid": "efccbdf2299e4b3d8ab767e879e60863",
            "description": "a building featuring a clock tower, staircase, ferris wheel, and a floating boat nearby",
            "placement": 4,
            "from": "cap3d",
            "scale": {
                "factor": 3.0,
                "name": "huge",
                "name_synonym": "very big"
            },
            "movement": {
                "direction": "left",
                "speed": 0.08990124981699919
            },
            "relationships": "a building featuring a clock tower, staircase, ferris wheel, and a floating boat nearby is to the left of white ring with a curved design."
        },
        {
            "name": "white ring with a curved design",
            "uid": "39825e7b48454e74bae405ea7f8ab964",
            "description": "white ring with a curved design",
            "placement": 1,
            "from": "cap3d",
            "scale": {
                "factor": 2.25,
                "name": "large",
                "name_synonym": "massive"
            },
            "movement": {
                "direction": "backward",
                "speed": 0.10487729616518639
            },
            "relationships": "a building featuring a clock tower, staircase, ferris wheel, and a floating boat nearby is to the left of and behind a square object featuring red and pink lines, resembling a table, rug, or ceiling panel."
        },
        {
            "name": "a square object featuring red and pink lines, resembling a table, rug, or ceiling panel",
            "uid": "69dfa841d1444622883d9fc1fd726625",
            "description": "a square object featuring red and pink lines, resembling a table, rug, or ceiling panel",
            "placement": 2,
            "from": "cap3d",
            "scale": {
                "factor": 3.0,
                "name": "huge",
                "name_synonym": "extra large"
            },
            "movement": {
                "direction": "left",
                "speed": 0.13250349055797148
            },
            "relationships": "a building featuring a clock tower, staircase, ferris wheel, and a floating boat nearby is  and behind A pink alien-shaped toy with eyes, arms, legs, and a mouth, resembling a rabbit or bunny."
        },
        {
            "name": "A pink alien-shaped toy with eyes, arms, legs, and a mouth, resembling a rabbit or bunny",
            "uid": "23da888f8d034c9594930eba8279c6e9",
            "description": "A pink alien-shaped toy with eyes, arms, legs, and a mouth, resembling a rabbit or bunny",
            "placement": 5,
            "from": "cap3d",
            "scale": {
                "factor": 2.25,
                "name": "large",
                "name_synonym": "large"
            },
            "movement": {
                "direction": "forward",
                "speed": 0.10110217017409817
            },
            "relationships": "a building featuring a clock tower, staircase, ferris wheel, and a floating boat nearby is to the right of and behind a black teddy bear and a black bird, both wearing hats."
        },
        {
            "name": "a black teddy bear and a black bird, both wearing hats",
            "uid": "18969fffe8674a91a41b093c4f6bf612",
            "description": "a black teddy bear and a black bird, both wearing hats",
            "placement": 8,
            "from": "cap3d",
            "scale": {
                "factor": 1.0,
                "name": "medium",
                "name_synonym": "usual"
            },
            "movement": {
                "direction": "right",
                "speed": 0.10007398751033873
            },
            "camera_follow": {
                "follow": true
            },
            "relationships": "white ring with a curved design is to the right of a building featuring a clock tower, staircase, ferris wheel, and a floating boat nearby."
        }
    ],

Example 3:

Prompt/caption: A house with a detailed roof and a map on the ceiling moves slowly to the left.  Camera angle is forward and ahead to show the house moving. The scene is set on an evening road with white sandstone brick flooring, and uses normal lighting with motion blur.

"objects": [
    {
        "name": "a house featuring a detailed roof structure and a suspended ceiling with a map on it",
        "uid": "ee7e6031912b46bc8ca7205a959c5c16",
        "description": "a house featuring a detailed roof structure and a suspended ceiling with a map on it",
        "placement": 4,
        "from": "cap3d",
        "scale": {
            "factor": 1.5,
            "name": "medium-large",
            "name_synonym": "considerable"
        },
        "transformed_position": [
            0,
            0
        ],
        "movement": {
            "direction": "left",
            "speed": 0.06752940064263789
        },
        "relationships": []
    }
],

TIP: Only add movement to the object if it is moving. If it is not moving, do not include the movement attribute.

Now generate the correct object placements and structures based on the prompt:  
"""


CAMERA_PROMPT = """
    For camera information:


{
    "orientation": {
        "yaw_max": 360,
        "yaw_min": 0,
        "pitch_max": 75,
        "pitch_min": 0,
        "labels": {
            "yaw": {
                "0": [
                    "facing forward",
                    "directly ahead",
                    "straight ahead",
                    "head on",
                    "<degrees> degrees forward",
                    "dead ahead",
                    "right in front",
                    "pointed forward",
                    "aligned forward",
                    "squarely ahead",
                    "<degrees>° forward"
                ],
                "15": [
                    "slightly left of front",
                    "front left quarter",
                    "slight left front",
                    "on the left side",
                    "<degrees> degrees to the left of front",
                    "<degrees> degrees left of front",
                    "<degrees> degrees to the left",
                    "<degrees>° to the left of front",
                    "<degrees>° left of front",
                    "<degrees>° to the left",
                    "just off front to the left",
                    "almost forward but left",
                    "slightly turned left"
                ],
                "30": [
                    "front left",
                    "left forward",
                    "leftward front",
                    "<degrees>° to the left",
                    "<degrees>° left",
                    "<degrees>° front left",
                    "<degrees> degrees to the left",
                    "<degrees> degrees left",
                    "<degrees> degrees front left",
                    "a bit to the left front",
                    "leaning left forward",
                    "slightly forward left",
                    "angled left forward"
                ],
                "45": [
                    "front left side",
                    "left forward side",
                    "oblique left",
                    "<degrees> degrees to the left",
                    "<degrees>° to the left",
                    "slightly to the front-left",
                    "a bit to the left of forward",
                    "not quite perpendicular to the left",
                    "just off the left forward",
                    "leaning towards the left front"
                ],
                "60": [
                    "left front quarter",
                    "left forward quarter",
                    "<degrees> degrees to the left",
                    "<degrees>° to the left",
                    "<degrees> degrees front left",
                    "<degrees>° front left",
                    "a sharp left forward",
                    "leaning strongly to the left",
                    "angled forward on the left",
                    "deep into the left quadrant",
                    "majorly to the left front"
                ],
                "75": [
                    "far left front",
                    "left side forward",
                    "<degrees> degrees to the left",
                    "<degrees>° to the left",
                    "<degrees> degrees front left",
                    "<degrees>° front left",
                    "nearing perpendicular left",
                    "heavily biased to the left front",
                    "sharply forward left",
                    "greatly to the left front",
                    "deep left but forward"
                ],
                "90": [
                    "left side",
                    "directly left",
                    "perpendicular left",
                    "<degrees> degrees to the left",
                    "<degrees>° to the left",
                    "<degrees> degrees left",
                    "<degrees>° left",
                    "direct left",
                    "straight to the left",
                    "clearly to the left",
                    "flat left",
                    "horizontal left"
                ],
                "105": [
                    "back left quarter",
                    "left rear quarter",
                    "<degrees> degrees to the left",
                    "<degrees>° to the left",
                    "<degrees> degrees rear left",
                    "<degrees>° rear left",
                    "slightly back on the left",
                    "a bit behind to the left",
                    "just off left but backwards",
                    "leaning back on the left",
                    "rearward to the left"
                ],
                "120": [
                    "rear left",
                    "left backward",
                    "<degrees> degrees to the left",
                    "<degrees>° to the left",
                    "<degrees> degrees rear left",
                    "<degrees>° rear left",
                    "back towards the left",
                    "left and slightly behind",
                    "left rearward",
                    "angled back on the left",
                    "deep into the rear-left quadrant"
                ],
                "135": [
                    "back left side",
                    "left rear side",
                    "oblique rear left",
                    "<degrees> degrees to the left",
                    "<degrees>° to the left",
                    "<degrees> degrees rear left",
                    "<degrees>° rear left",
                    "strongly to the rear-left",
                    "deep left rear",
                    "sharply back left",
                    "heavily to the back left",
                    "far back to the left"
                ],
                "150": [
                    "left rear quarter",
                    "left back quarter",
                    "<degrees> degrees to the left",
                    "<degrees>° to the left",
                    "<degrees> degrees rear left",
                    "<degrees>° rear left",
                    "sharp left back",
                    "deep into left rear quadrant",
                    "majorly to the left back",
                    "back and deep left",
                    "left and far behind"
                ],
                "165": [
                    "far back left",
                    "left side back",
                    "<degrees> degrees to the left",
                    "<degrees>° to the left",
                    "nearing directly behind on the left",
                    "<degrees> degrees rear left",
                    "<degrees>° rear left",
                    "almost back left",
                    "strong left back",
                    "heavy left rear",
                    "deeply back on the left"
                ],
                "180": [
                    "back",
                    "directly back",
                    "rear",
                    "<degrees> degrees",
                    "<degrees>°",
                    "<degrees> degrees rear",
                    "<degrees>° rear",
                    "directly behind",
                    "straight back",
                    "clear back",
                    "flat back",
                    "horizontal rear"
                ],
                "195": [
                    "far back right",
                    "right side back",
                    "<degrees> degrees to the right",
                    "<degrees>° to the right",
                    "<degrees> degrees rear right",
                    "<degrees>° rear right",
                    "nearing directly behind on the right",
                    "almost back right",
                    "strong right back",
                    "heavy right rear",
                    "deeply back on the right"
                ],
                "210": [
                    "right rear quarter",
                    "right back quarter",
                    "<degrees> degrees to the right",
                    "<degrees>° to the right",
                    "<degrees> degrees rear right",
                    "<degrees>° rear right",
                    "sharp right back",
                    "deep into right rear quadrant",
                    "majorly to the right back",
                    "back and deep right",
                    "right and far behind"
                ],
                "225": [
                    "back right side",
                    "right rear side",
                    "oblique rear right",
                    "<degrees> degrees to the right",
                    "<degrees>° to the right",
                    "<degrees> degrees rear right",
                    "<degrees>° rear right",
                    "strongly to the rear-right",
                    "deep right rear",
                    "sharply back right",
                    "heavily to the back right",
                    "far back to the right"
                ],
                "240": [
                    "rear right",
                    "right backward",
                    "<degrees> degrees to the right",
                    "<degrees>° to the right",
                    "<degrees> degrees rear right",
                    "<degrees>° rear right",
                    "back towards the right",
                    "right and slightly behind",
                    "right rearward",
                    "angled back on the right",
                    "deep into the rear-right quadrant"
                ],
                "255": [
                    "back right quarter",
                    "right rear quarter",
                    "<degrees> degrees to the right",
                    "<degrees>° to the right",
                    "<degrees> degrees rear right",
                    "<degrees>° rear right",
                    "slightly back on the right",
                    "a bit behind to the right",
                    "just off right but backwards",
                    "leaning back on the right",
                    "rearward to the right"
                ],
                "270": [
                    "right side",
                    "directly right",
                    "perpendicular right",
                    "<degrees> degrees to the right",
                    "<degrees>° to the right",
                    "<degrees> degrees right",
                    "<degrees>° right",
                    "direct right",
                    "straight to the right",
                    "clearly to the right",
                    "flat right",
                    "horizontal right"
                ],
                "285": [
                    "far right front",
                    "right side forward",
                    "<degrees> degrees to the right",
                    "<degrees>° to the right",
                    "<degrees> degrees front right",
                    "<degrees>° front right",
                    "nearing perpendicular right",
                    "heavily biased to the right front",
                    "sharply forward right",
                    "greatly to the right front",
                    "deep right but forward"
                ],
                "300": [
                    "right front quarter",
                    "right forward quarter",
                    "<degrees> degrees to the right",
                    "<degrees>° to the right",
                    "<degrees> degrees front right",
                    "<degrees>° front right",
                    "a sharp right forward",
                    "leaning strongly to the right",
                    "angled forward on the right",
                    "deep into the right quadrant",
                    "majorly to the right front"
                ],
                "315": [
                    "front right side",
                    "right forward side",
                    "oblique right",
                    "<degrees> degrees to the right",
                    "<degrees>° to the right",
                    "<degrees> degrees front right",
                    "<degrees>° front right",
                    "slightly to the front-right",
                    "a bit to the right of forward",
                    "not quite perpendicular to the right",
                    "just off the right forward",
                    "leaning towards the right front"
                ],
                "330": [
                    "front right",
                    "right forward",
                    "<degrees> degrees to the right",
                    "<degrees>° to the right",
                    "<degrees> degrees front right",
                    "<degrees>° front right",
                    "slightly to the right of forward",
                    "slight bias to the right",
                    "marginally front right"
                ],
                "345": [
                    "slightly right of front",
                    "front right quarter",
                    "slight right front",
                    "on the right side",
                    "<degrees> degrees to the right of front",
                    "<degrees> degrees right of front",
                    "<degrees> degrees to the right",
                    "just shy of directly ahead on the right",
                    "almost facing front-right",
                    "nearly front but to the right",
                    "front-right leaning",
                    "ahead but veered right"
                ]
            },
            "pitch": {
                "0": [
                    "level with the ground",
                    "horizontally level",
                    "flat",
                    "even",
                    "<degrees> degrees"
                ],
                "15": [
                    "tilted down slightly",
                    "slightly downward",
                    "mildly downward",
                    "<degrees> degrees downward",
                    "<degrees> forward"
                ],
                "30": [
                    "tilted down",
                    "downward tilt",
                    "angled down",
                    "<degrees> degrees downward",
                    "<degrees> forward",
                    "angled downward"
                ],
                "45": [
                    "tilted down sharply",
                    "sharply downward",
                    "steeply downward",
                    "<degrees> degrees downward",
                    "<degrees> forward"
                ],
                "60": [
                    "tilted down steeply",
                    "steeply angled down",
                    "sharply angled downward",
                    "<degrees> degrees downward",
                    "<degrees> forward",
                    "angled down sharply",
                    "<degrees> down steeply>",
                    "<degrees> steeply down",
                    "<degrees> sharply downward"
                ]
            }
        },
        "descriptions": [
            "The camera is <yaw>, <pitch>.",
            "The camera is <pitch>, <yaw>.",
            "<pitch>, <yaw>.",
            "Yaw: <yaw>, Pitch: <pitch>.",
            "Pitch: <pitch>, Yaw: <yaw>.",
            "Tilt: <pitch>, Rotation: <yaw>.",
            "The lens is oriented <yaw>, with a <pitch> tilt.",
            "Camera facing <yaw> and angled <pitch>.",
            "The view is set <pitch>, looking <yaw>.",
            "Orientation: <yaw>, Angle: <pitch>.",
            "The shot is angled <pitch> while pointing <yaw>.",
            "Direction <yaw>, elevation <pitch>.",
            "Adjust the camera <yaw> and <pitch>.",
            "Set the camera to <pitch> and <yaw>.",
            "Position the camera at <pitch> and <yaw>.",
            "Yaw: <yaw>, Pitch: <pitch>.",
            "Pitch: <pitch>, Yaw: <yaw>.",
            "Tilt: <pitch>, Rotation: <yaw>.",
            "Orient the camera <yaw> with a <pitch> tilt.",
            "Direct the camera <yaw>, set tilt to <pitch>.",
            "Angle the lens <pitch> and rotate it <yaw>.",
            "Configure the camera to face <yaw> with a <pitch> angle.",
            "Align the camera to <yaw>, and adjust the pitch to <pitch>.",
            "Rotate the camera to <yaw> and tilt it <pitch>."
        ]
    },
    "framings": [
        {
            "name": "extreme_closeup",
            "fov_min": 10,
            "fov_max": 15,
            "coverage_factor_min": 0.7,
            "coverage_factor_max": 1.1,
            "descriptions": [
                "Extreme close-up shot",
                "Extremely tight framing",
                "Intensely intimate view",
                "Minute details captured",
                "Right up close",
                "Heavily zoomed in",
                "Details fill the frame",
                "Extreme detail focus",
                "Extremely near view",
                "As close as possible",
                "Extremely close framing",
                "Intense close-up perspective",
                "Extreme close-up of objects",
                "Objects dominate the frame",
                "Deeply intimate close-up",
                "Extremely tight shot",
                "Incredibly close view",
                "Extreme zoom on details",
                "Macro-level perspective",
                "Microscopic framing",
                "Up-close and personal",
                "Extreme close focus",
                "Highly detailed close-up",
                "Extremely zoomed in",
                "Intensely close shot",
                "Extreme proximity",
                "Ultra-tight framing",
                "Magnified view",
                "Ultra-close perspective",
                "Extremely detailed shot"
            ]
        },
        {
            "name": "closeup",
            "fov_min": 15,
            "fov_max": 24,
            "coverage_factor_min": 1.0,
            "coverage_factor_max": 1.2,
            "descriptions": [
                "Close-up shot of the objects.",
                "Close-up framing.",
                "Close view of the objects.",
                "Objects occupy the frame closely.",
                "Intimate close-up.",
                "Tight framing on the objects.",
                "Close-up perspective.",
                "Objects captured up close.",
                "Detailed close-up shot.",
                "Tight close-up.",
                "Close-up view.",
                "Intimate close-up.",
                "Detailed close-up.",
                "Close framing.",
                "Zoomed in close on the details.",
                "Intimately close view of the objects.",
                "Fills the frame for an up-close perspective.",
                "Tight shot that gets in close to the objects.",
                "Close-up shot",
                "Tight framing",
                "Intimate view",
                "Detailed perspective",
                "Up close",
                "Zoomed in",
                "Fill the frame",
                "Details highlighted",
                "Close focus",
                "Near view",
                "In tight"
            ]
        },
        {
            "name": "medium_closeup",
            "fov_min": 24,
            "fov_max": 30,
            "coverage_factor_min": 0.8,
            "coverage_factor_max": 1.2,
            "descriptions": [
                "Medium close-up shot",
                "Slightly tight framing",
                "Fairly intimate view",
                "Moderate detail focus",
                "Closer than medium",
                "Slightly zoomed in",
                "Objects fill more frame",
                "Emphasized details",
                "Medium-close perspective",
                "Moderately near view",
                "Tighter than standard",
                "Mildly close framing",
                "Somewhat close shot",
                "Moderate object focus",
                "Slightly intimate view",
                "Medium-tight shot",
                "Moderately close view",
                "Mild zoom on details",
                "Semi-close perspective",
                "In between medium and close",
                "Somewhat zoomed in",
                "Moderately detailed shot"
            ]
        },
        {
            "name": "medium",
            "fov_min": 30,
            "fov_max": 40,
            "coverage_factor_min": 1.0,
            "coverage_factor_max": 1.5,
            "descriptions": [
                "Medium shot",
                "Medium framing",
                "Medium shot framing the objects.",
                "Medium shot.",
                "Balanced medium.",
                "Standard medium.",
                "Standard medium framing on the objects.",
                "Not too tight, not too loose - just right in the middle.",
                "A moderate, neutral distance from the subjects.",
                "Medium distance, balanced composition.",
                "Standard view",
                "Typical framing",
                "Normal distance",
                "Mid-range shot",
                "Balanced perspective",
                "Average framing",
                "Neutral distance",
                "Middle ground",
                "Moderate zoom",
                "Halfway in"
            ]
        },
        {
            "name": "medium_wide",
            "fov_min": 40,
            "fov_max": 55,
            "coverage_factor_min": 1.5,
            "coverage_factor_max": 2.0,
            "descriptions": [
                "Medium-wide shot",
                "Medium wide shot",
                "Medium wide angle",
                "Medium wide framing",
                "Medium wide shot of the objects.",
                "Medium wide perspective.",
                "Medium-wide framing on the objects.",
                "Medium-wide shot of the scene.",
                "Medium-wide.",
                "Medium wide",
                "Medium-wide angle",
                "Not too close, not too far.",
                "A bit wider than a typical medium shot.",
                "Halfway between a medium and a wide.",
                "Pulls back a little from medium framing.",
                "Slightly expanded view compared to medium.",
                "Slightly wide",
                "Moderately broad",
                "Mild widening",
                "Somewhat expansive",
                "Gently zoomed out"
            ]
        },
        {
            "name": "wide",
            "fov_min": 55,
            "fov_max": 70,
            "coverage_factor_min": 2.0,
            "coverage_factor_max": 3.0,
            "descriptions": [
                "Wide shot.",
                "Wide angle",
                "Wide framing.",
                "Wide shot of the objects.",
                "Expansive view of the objects.",
                "Expansive view.",
                "Taking in the whole scene.",
                "Expansive, broad view of the full setting and objects.",
                "Wide perspective showing everything.",
                "Zoomed out to capture the big picture.",
                "All-encompassing wide angle on the full space.",
                "Zoomed out",
                "Broad view",
                "Expansive framing",
                "Full perspective",
                "Sweeping vista",
                "All-encompassing",
                "Big picture",
                "Comprehensive view",
                "Wide-angle",
                "Broad scope",
                "Fully zoomed out"
            ]
        },
        {
            "name": "extreme_wide",
            "fov_min": 70,
            "fov_max": 90,
            "coverage_factor_min": 3.0,
            "coverage_factor_max": 4.0,
            "descriptions": [
                "Extreme wide shot",
                "Extreme wide angle",
                "Extreme wide framing",
                "Extremely broad framing",
                "Extremely zoomed out",
                "Captures entire scene",
                "Panoramic view",
                "Massively wide shot",
                "Extremely expansive framing",
                "Ultra-wide perspective",
                "Extremely wide landscape",
                "Extremely broad view",
                "Ultra-zoomed out",
                "Extremely wide angle",
                "Captures entire setting",
                "Extremely wide coverage",
                "Ultra-expansive shot",
                "Extremely wide perspective"
            ]
        }
    ],
    "animation_speed": { 
        "min": 0.5,
        "max": 2.0,
        "types": {
            "slow": {
                "min": 0.5,
                "max": 0.75,
                "descriptions": [
                    "Slow animation speed <animation_speed_value> applied.",
                    "The scene has a slow animation speed of <animation_speed_value>.",
                    "Animation speed of <animation_speed_value> is set to slow.",
                    "The scene is rendered with a slow animation speed of <animation_speed_value>.",
                    "Slow animation is used in the scene.",
                    "The scene has a leisurely animation speed of <animation_speed_value>.",
                    "Animation is set to slow speed of <animation_speed_value> in the scene.",
                    "The scene is enhanced with a slow animation speed of <animation_speed_value>.",
                    "Slow animation is present in the scene.",
                    "The scene is rendered with a slow animation speed of <animation_speed_value>.",
                    "The animation runs at a slow pace.",
                    "The scene features a gentle animation speed.",
                    "Animations are intentionally slowed down.",
                    "A calm and slow animation speed is applied.",
                    "The scene moves with a relaxed animation speed.",
                    "Animations unfold slowly in the scene.",
                    "The pace of animation is deliberately slow.",
                    "The scene showcases a leisurely animation speed.",
                    "Slow-motion animation effects are used.",
                    "The scene transitions smoothly with a slow animation speed."
                ]
            },
            "medium": {
                "min": 0.75,
                "max": 1.25,
                "descriptions": [
                    [
                        "Medium animation speed of <animation_speed_value> applied.",
                        "The scene has a moderate animation speed of <animation_speed_value>.",
                        "Animation speed is set to medium of <animation_speed_value>.",
                        "The scene is rendered with a moderate animation speed of <animation_speed_value>.",
                        "Medium animation of <animation_speed_value> is used in the scene.",
                        "The scene has a normal animation speed of <animation_speed_value>.",
                        "Animation is set to medium speed of <animation_speed_value> in the scene.",
                        "The scene is enhanced with a moderate animation speed of <animation_speed_value>.",
                        "Medium animation of <animation_speed_value> is present in the scene.",
                        "The scene is rendered with a moderate animation speed of <animation_speed_value>.",
                        "The animation speed is set to a balanced pace.",
                        "The scene features a moderate animation tempo.",
                        "Animations operate at a medium speed.",
                        "A standard animation speed is applied to the scene.",
                        "The scene progresses with a medium-paced animation.",
                        "Animations move at a steady speed in the scene.",
                        "The animation runs at a moderate rate.",
                        "The scene has a typical animation speed.",
                        "Animations flow at a medium speed in the scene.",
                        "The scene transitions at a moderate animation speed."
                    ]
                ]
            },
            "fast": {
                "min": 1.25,
                "max": 1.5,
                "descriptions": [
                    [
                        "Fast animation speed of <animation_speed_value> applied.",
                        "The scene has a fast animation speed of <animation_speed_value>.",
                        "Animation speed is set to fast of <animation_speed_value>.",
                        "The scene is rendered with a fast animation speed of <animation_speed_value>.",
                        "Fast animation of <animation_speed_value> is used in the scene.",
                        "The scene has a quick animation speed of <animation_speed_value>.",
                        "Animation is set to fast speed of <animation_speed_value> in the scene.",
                        "The scene is enhanced with a fast animation speed of <animation_speed_value>.",
                        "Fast animation of <animation_speed_value> is present in the scene.",
                        "The scene is rendered with a fast animation speed of <animation_speed_value>.",
                        "The animation runs at a rapid pace.",
                        "The scene features a swift animation speed.",
                        "Animations are set to a fast tempo.",
                        "A quick animation speed is applied.",
                        "The scene moves with high-speed animation.",
                        "Animations unfold rapidly in the scene.",
                        "The pace of animation is brisk.",
                        "The scene showcases a fast animation rate.",
                        "High-speed animation effects are used.",
                        "The scene transitions quickly with fast animation."
                    ]
                ]
            },
            "faster": {
                "min": 1.5,
                "max": 2.0,
                "descriptions": [
                    [
                        "Faster animation speed of <animation_speed_value> applied.",
                        "The scene has a faster animation speed of <animation_speed_value>.",
                        "Animation speed is set to faster of <animation_speed_value>.",
                        "The scene is rendered with a faster animation speed of <animation_speed_value>.",
                        "Faster animation of <animation_speed_value> is used in the scene.",
                        "The scene has an accelerated animation speed of <animation_speed_value>.",
                        "Animation is set to faster speed of <animation_speed_value> in the scene.",
                        "The scene is enhanced with a faster animation speed of <animation_speed_value>.",
                        "Faster animation of <animation_speed_value> is present in the scene.",
                        "The scene is rendered with a faster animation speed of <animation_speed_value>.",
                        "The animation speed is increased significantly.",
                        "The scene features an enhanced animation tempo.",
                        "Animations are set to a much faster pace.",
                        "A highly accelerated animation speed is applied.",
                        "The scene progresses with a rapid animation rate.",
                        "Animations move at an expedited speed in the scene.",
                        "The animation runs at a notably faster rate.",
                        "The scene showcases a significantly increased animation speed.",
                        "Animations unfold at an accelerated pace.",
                        "The scene transitions swiftly with enhanced animation speed."
                    ]
                ]
            }
        }
    },
    "animations": [        
        {
            "name": "static",
            "descriptions": [
                "The camera remains stationary.",
                "No camera movement.",
                "The camera holds still.",
                "Static camera shot.",
                "The camera does not move.",
                "Steady, unmoving camera.",
                "Fixed camera position.",
                "Motionless camera.",
                "The camera is locked in place.",
                "Stable, static camera view.",
                "The scene is captured from a fixed perspective.",
                "Unmoving camera angle.",
                "The camera is set in a fixed position.",
                "No motion in the camera view.",
                "The objects are captured with a static camera."
            ],
            "keyframes": []
        },
        {
            "name": "pan_left",
            "descriptions": [
                "The camera moves horizontally to the left.",
                "The view shifts to the left.",
                "Sweeping leftward movement of the camera.",
                "Camera glides left.",
                "The scene moves smoothly to the left as the camera pans.",
                "Horizontal pan to the left.",
                "The camera shifts left.",
                "Leftward panning of the camera.",
                "The camera moves left.",
                "Pan the camera left.",
                "Shift the camera smoothly to the left to alter the view.",
                "Pan the camera to the left to capture a wider perspective.",
                "Glide the camera left to change the scene laterally.",
                "Sweep the camera to the left.",
                "Move the camera horizontally to the left.",
                "Adjust the camera to pan left.",
                "Slide the camera leftward.",
                "The camera swings to the left.",
                "Lateral movement of the camera to the left.",
                "The view transitions to the left as the camera moves.",
                "Horizontal shift of the camera to the left.",
                "The camera tracks left."
            ],
            "keyframes": [
                {
                    "CameraAnimationPivot": {
                        "position": [
                            0,
                            -1.5,
                            0
                        ]
                    }
                },
                {
                    "CameraAnimationPivot": {
                        "position": [
                            0,
                            0.5,
                            0
                        ]
                    }
                }
            ]
        },
        {
            "name": "pan_right",
            "descriptions": [
                "The camera moves horizontally to the right.",
                "Pan the camera right.",
                "The view shifts to the right.",
                "Sweeping rightward movement of the camera.",
                "Camera glides right.",
                "The scene moves smoothly to the right as the camera pans.",
                "Horizontal pan to the right.",
                "The camera shifts right.",
                "Rightward panning of the camera.",
                "The camera moves right.",
                "Shift the camera smoothly to the right to alter the view.",
                "Pan the camera to the right to capture a wider perspective.",
                "Glide the camera right to change the scene laterally.",
                "Sweep the camera to the right.",
                "Move the camera horizontally to the right to extend the visible area.",
                "Rotate the camera right.",
                "Adjust the camera to pan right.",
                "Swivel the camera to the right.",
                "Turn the camera to the right.",
                "Slide the camera rightward to enhance the panoramic perspective.",
                "The camera swings to the right.",
                "Lateral movement of the camera to the right.",
                "The view transitions to the right as the camera moves.",
                "Horizontal shift of the camera to the right.",
                "The camera tracks right."
            ],
            "keyframes": [
                {
                    "CameraAnimationPivot": {
                        "position": [
                            0,
                            1.5,
                            0
                        ]
                    }
                },
                {
                    "CameraAnimationPivot": {
                        "position": [
                            0,
                            -0.5,
                            0
                        ]
                    }
                }
            ]
        },
        {
            "name": "orbit_left",
            "descriptions": [
                "The camera orbits counter-clockwise around the scene.",
                "Move the camera in a circular path to the left around the stage.",
                "The camera circles the objects to the left.",
                "Counter-clockwise orbit around the objects.",
                "Camera makes a complete rotation to the left around the objects.",
                "Orbiting left around the objects.",
                "The camera encircles the scene to the left.",
                "Circular motion of the camera around the objects to the left.",
                "Camera travels in a leftward circle around the subjects.",
                "Full orbit to the left around the objects.",
                "Orbit the camera counter-clockwise around the subject.",
                "Circle the camera to the left around the subject.",
                "Rotate the camera in a counter-clockwise path around the objects.",
                "Move the camera in a circular leftward path around the objects.",
                "Guide the camera to orbit left around the objects.",
                "Swing the camera around the objects to the left.",
                "Rotate the camera left in a circular motion around the objects.",
                "Spiral the camera to the left around the objects.",
                "Encircle the scene with the camera moving left.",
                "Turn the camera in a counter-clockwise orbit.",
                "The camera revolves around the objects counter-clockwise.",
                "Circular trajectory of the camera moving to the left around the scene.",
                "The camera arcs around the objects to the left.",
                "Rotate the camera around the objects in a counter-clockwise direction.",
                "The camera traces a circular path to the left around the subjects."
            ],
            "keyframes": [
                {
                    "CameraAnimationRoot": {
                        "rotation": [
                            0,
                            0,
                            90
                        ]
                    }
                },
                {
                    "CameraAnimationRoot": {
                        "rotation": [
                            0,
                            0,
                            0
                        ]
                    }
                }
            ]
        },
        {
            "name": "orbit_right",
            "descriptions": [
                "The camera orbits clockwise around the objects.",
                "Move the camera in a circular path to the right around the subject.",
                "The camera circles the scene to the right.",
                "Clockwise orbit around the subject.",
                "Camera makes a complete rotation to the right.",
                "Orbiting right around the objects.",
                "The camera encircles the objects to the right.",
                "Spiral motion of the camera around the objects.",
                "Camera travels in a rightward circle around the objects.",
                "Full orbit to the right around the objects.",
                "Orbit the camera clockwise around the scene.",
                "Circle the camera to the right around the stage.",
                "Rotate the camera in a clockwise path around the objects.",
                "Move the camera in a circular rightward path around the objects.",
                "Guide the camera to orbit right around the objects.",
                "Swing the camera around the objects to the right.",
                "Rotate the camera right in a circular motion around the objects.",
                "Spiral the camera to the right around the objects.",
                "Encircle the objects with the camera moving right.",
                "Spin the camera in a clockwise orbit around the objects.",
                "The camera revolves around the objects clockwise.",
                "Circular trajectory of the camera moving to the right around the scene.",
                "The camera arcs around the objects to the right.",
                "Rotate the camera around the objects in a clockwise direction.",
                "The camera traces a circular path to the right around the subjects."
            ],
            "keyframes": [
                {
                    "CameraAnimationRoot": {
                        "rotation": [
                            0,
                            0,
                            0
                        ]
                    }
                },
                {
                    "CameraAnimationRoot": {
                        "rotation": [
                            0,
                            0,
                            90
                        ]
                    }
                }
            ]
        },
        {
            "name": "orbit_up",
            "descriptions": [
                "The camera orbits upward from 0 to 90 degrees over the scene.",
                "Elevate the camera in an orbital path above the objects.",
                "Raise the camera perspective while orbiting over the scene.",
                "Orbit the camera up to a 90-degree angle.",
                "The view lifts as the camera orbits upward.",
                "Upward orbital movement of the camera.",
                "The camera arcs up and over the scene.",
                "Rotate the camera upward in an orbital trajectory.",
                "Orbit up to capture a bird's eye view of the scene.",
                "The camera ascends in an orbital path over the objects.",
                "Sweep the camera up and over the scene.",
                "Adjust the camera to orbit upward.",
                "Trace an upward orbital path with the camera.",
                "Elevate the camera perspective with an upward orbit.",
                "Orbit the camera up to look down on the scene from above."
            ],
            "keyframes": [
                {
                    "CameraFramingPivot": {
                        "rotation": [
                            0,
                            0,
                            0
                        ]
                    }
                },
                {
                    "CameraFramingPivot": {
                        "rotation": [
                            0,
                            -30,
                            0
                        ]
                    }
                }
            ]
        },
        {
            "name": "orbit_down",
            "descriptions": [
                "The camera orbits downward from 90 to 0 degrees over the scene.",
                "Lower the camera in an orbital path back to the starting position.",
                "Descend the camera perspective while orbiting over the scene.",
                "Orbit the camera down from a 90-degree angle.",
                "The view lowers as the camera orbits downward.",
                "Downward orbital movement of the camera.",
                "The camera arcs down and returns to the initial view.",
                "Rotate the camera downward in an orbital trajectory.",
                "Orbit down to restore the original camera perspective.",
                "The camera descends in an orbital path back to the objects.",
                "Sweep the camera down from the elevated position.",
                "Adjust the camera to orbit downward.",
                "Trace a downward orbital path with the camera.",
                "Lower the camera perspective with a downward orbit.",
                "Orbit the camera down to look at the scene from the starting angle."
            ],
            "keyframes": [
                {
                    "CameraFramingPivot": {
                        "rotation": [
                            0,
                            -30,
                            0
                        ]
                    }
                },
                {
                    "CameraFramingPivot": {
                        "rotation": [
                            0,
                            0,
                            0
                        ]
                    }
                }
            ]
        },
        {
            "name": "dolly_in",
            "descriptions": [
                "The camera moves closer to the subject.",
                "Dolly the camera toward the scene.",
                "The camera advances toward the objects.",
                "The camera pushes toward the subject.",
                "Dolly in to focus more closely.",
                "The camera travels in to capture details.",
                "Dolly in to highlight the objects.",
                "The camera moves in to concentrate on the objects.",
                "The camera progresses closer to emphasize details.",
                "The camera narrows the scene by moving in.",
                "The camera approaches the objects.",
                "Dolly in to bring the objects nearer.",
                "The camera advances to fill the frame with objects."
            ],
            "keyframes": [
                {
                    "CameraAnimationPivot": {
                        "position": [
                            4,
                            0,
                            0
                        ]
                    }
                },
                {
                    "CameraAnimationPivot": {
                        "position": [
                            0,
                            0,
                            0
                        ]
                    }
                }
            ]
        },
        {
            "name": "dolly_out",
            "descriptions": [
                "The camera pulls back from the scene.",
                "Dolly out to widen the view.",
                "The camera retreats from the objects.",
                "The camera withdraws from the subject.",
                "Pull the camera back.",
                "Dolly out to de-emphasize the objects.",
                "The camera moves out to show a wider scene.",
                "The camera pulls back to reveal more context.",
                "The camera pulls away, expanding the view.",
                "Dolly out to reduce focus on the objects.",
                "The camera retreats to show a broader perspective.",
                "Dolly out to place the objects into a larger context."
            ],
            "keyframes": [
                {
                    "CameraAnimationPivot": {
                        "position": [
                            0,
                            0,
                            0
                        ]
                    }
                },
                {
                    "CameraAnimationPivot": {
                        "position": [
                            4,
                            0,
                            0
                        ]
                    }
                }
            ]
        },
        {
            "name": "zoom_in",
            "descriptions": [
                "The camera zooms in.",
                "Move closer to the scene.",
                "Move toward the objects.",
                "Move toward the subject.",
                "Zoom in.",
                "Zoom in to the scene.",
                "Zoom in on the objects",
                "Camera narrows the view to concentrate on the objects.",
                "Zooming in to highlight details of the objects.",
                "The camera zooms in.",
                "The camera closes in on the objects.",
                "Zoom in to make the objects appear closer.",
                "Adjust the zoom to concentrate on the objects.",
                "Move the camera closer.",
                "Zoom in to focus on the objects.",
                "Close in on the objects with the zoom.",
                "The view narrows as the camera zooms in.",
                "The camera focuses to emphasize the objects.",
                "Zooming in brings the objects closer.",
                "The camera magnifies the view of the objects.",
                "Adjust the zoom to fill the frame with the objects."
            ],
            "keyframes": [
                {
                    "Camera": {
                        "angle_offset": 10
                    }
                },
                {
                    "Camera": {
                        "angle_offset": 0
                    }
                }
            ]
        },
        {
            "name": "zoom_out",
            "descriptions": [
                "The camera zooms out.",
                "Zoom out.",
                "Zooming out.",
                "The objects become smaller as the camera zooms out.",
                "Increasing the view width.",
                "Zooming out de-emphasizes the objects.",
                "The camera zooms in.",
                "Move away from the scene.",
                "Move away the objects.",
                "Move away the subject.",
                "Pull back.",
                "Pull away from the objects.",
                "Pull back with the camera zoom.",
                "Zoom in.",
                "Zoom in to the scene.",
                "Zoom in on the objects",
                "Zooming in to highlight details of the objects.",
                "The camera zooms in.",
                "The camera closes in on the objects.",
                "Zoom in to make the objects appear closer.",
                "Adjust the zoom to concentrate on the objects.",
                "Move the camera closer.",
                "Zoom in to focus on the objects.",
                "Close in on the objects with the zoom.",
                "Pull back with the camera zoom.",
                "The view widens as the camera zooms out.",
                "The camera pulls back to de-emphasize the objects.",
                "Zooming out pushes the objects further away.",
                "The camera reduces the view of the objects.",
                "Adjust the zoom to expand the frame beyond the objects."
            ],
            "keyframes": [
                {
                    "Camera": {
                        "angle_offset": 0
                    }
                },
                {
                    "Camera": {
                        "angle_offset": 10
                    }
                }
            ]
        },
        {
            "name": "tilt_up",
            "descriptions": [
                "The camera tilts upward.",
                "Tilt the view up.",
                "Camera points up.",
                "Angle the camera upward.",
                "The scene tilts up as the camera moves.",
                "Vertical tilt upward.",
                "The camera tilts up.",
                "Upward tilting of the camera.",
                "The camera rotates up.",
                "Tilt the camera up.",
                "Angle the camera up to shift the view vertically.",
                "Tilt the camera upward to capture more of the upper scene.",
                "Rotate the camera up to change the vertical perspective.",
                "Incline the camera upward.",
                "Move the camera to tilt up.",
                "Adjust the camera for an upward tilt.",
                "Pivot the camera up.",
                "The camera inclines vertically.",
                "Vertical rotation of the camera upward.",
                "The camera pans up.",
                "Upward pivot of the camera.",
                "The view shifts up as the camera tilts."
            ],
            "keyframes": [
                {
                    "Camera": {
                        "rotation": [
                            -25,
                            0,
                            0
                        ]
                    }
                },
                {
                    "Camera": {
                        "rotation": [
                            5,
                            0,
                            0
                        ]
                    }
                }
            ]
        },
        {
            "name": "tilt_down",
            "descriptions": [
                "The camera tilts downward.",
                "Tilt the view down.",
                "Camera points down.",
                "Angle the camera downward.",
                "The scene tilts down as the camera moves.",
                "Vertical tilt downward.",
                "The camera tilts down.",
                "Downward tilting of the camera.",
                "The camera rotates down.",
                "Tilt the camera down.",
                "Angle the camera down to shift the view vertically.",
                "Tilt the camera downward to capture more of the lower scene.",
                "Rotate the camera down to change the vertical perspective.",
                "Decline the camera downward.",
                "Move the camera to tilt down.",
                "Adjust the camera for a downward tilt.",
                "Pivot the camera down.",
                "The camera declines vertically.",
                "Vertical rotation of the camera downward.",
                "The camera pans down.",
                "Downward pivot of the camera.",
                "The view shifts down as the camera tilts."
            ],
            "keyframes": [
                {
                    "Camera": {
                        "rotation": [
                            25,
                            0,
                            0
                        ]
                    }
                },
                {
                    "Camera": {
                        "rotation": [
                            -5,
                            0,
                            0
                        ]
                    }
                }
            ]
        },
        {
            "name": "tilt_left",
            "descriptions": [
                "The camera tilts to the left.",
                "Tilt the view left.",
                "Camera banks left.",
                "Angle the camera to the left.",
                "The scene tilts left as the camera moves.",
                "Horizontal tilt to the left.",
                "The camera tilts left.",
                "Leftward tilting of the camera.",
                "The camera rotates left.",
                "Tilt the camera left.",
                "Angle the camera left to shift the view horizontally.",
                "Tilt the camera to the left.",
                "Rotate the camera left to change the horizontal perspective.",
                "Bank the camera to the left.",
                "Move the camera to tilt left.",
                "Adjust the camera for a leftward tilt.",
                "Pivot the camera left.",
                "The camera swivels to the left.",
                "Horizontal rotation of the camera to the left.",
                "The camera swivels left.",
                "Leftward banking of the camera.",
                "The view shifts to the left as the camera tilts."
            ],
            "keyframes": [
                {
                    "Camera": {
                        "rotation": [
                            0,
                            -25,
                            0
                        ]
                    }
                },
                {
                    "Camera": {
                        "rotation": [
                            0,
                            5,
                            0
                        ]
                    }
                }
            ]
        },
        {
            "name": "tilt_right",
            "descriptions": [
                "The camera tilts to the right.",
                "Tilt the view right.",
                "Camera banks right.",
                "Angle the camera to the right.",
                "The scene tilts right as the camera moves.",
                "Horizontal tilt to the right.",
                "The camera tilts right.",
                "Rightward tilting of the camera.",
                "The camera rotates right.",
                "Tilt the camera right.",
                "Angle the camera right to shift the view horizontally.",
                "Tilt the camera to the right.",
                "Rotate the camera right to change the horizontal perspective.",
                "Bank the camera to the right.",
                "Move the camera to tilt right.",
                "Adjust the camera for a rightward tilt.",
                "Pivot the camera right.",
                "The camera swivels to the right.",
                "Horizontal rotation of the camera to the right.",
                "The camera swivels right.",
                "Rightward banking of the camera.",
                "The view shifts to the right as the camera tilts."
            ],
            "keyframes": [
                {
                    "Camera": {
                        "rotation": [
                            0,
                            25,
                            0
                        ]
                    }
                },
                {
                    "Camera": {
                        "rotation": [
                            0,
                            -5,
                            0
                        ]
                    }
                }
            ]
        },
        {
            "name": "crane_up",
            "descriptions": [
                "The camera cranes upward.",
                "Crane the camera up.",
                "The view lifts as the camera cranes up.",
                "Camera rises in a crane shot.",
                "The scene moves up with the camera crane.",
                "Upward crane of the camera.",
                "The camera moves up on a crane.",
                "Craning shot lifting the camera.",
                "The camera elevates in a crane movement.",
                "Crane up with the camera.",
                "Lift the camera view using a crane shot.",
                "Crane the camera upward to gain height.",
                "Raise the camera perspective with a crane.",
                "Elevate the camera angle using a crane.",
                "Move the camera up in a craning motion.",
                "Adjust the camera to crane up.",
                "Hoist the camera view with a crane shot.",
                "The camera boom lifts.",
                "Elevating crane movement of the camera.",
                "The camera rises in a crane shot.",
                "Vertical tracking of the camera upward on a crane.",
                "The view ascends with the camera crane."
            ],
            "keyframes": [
                {
                    "CameraAnimationPivot": {
                        "position": [
                            0,
                            0,
                            0
                        ]
                    }
                },
                {
                    "CameraAnimationPivot": {
                        "position": [
                            0,
                            0,
                            2
                        ]
                    }
                }
            ]
        },
        {
            "name": "crane_down",
            "descriptions": [
                "The camera cranes downward.",
                "Crane the camera down.",
                "The view lowers as the camera cranes down.",
                "Camera descends in a crane shot.",
                "The scene moves down with the camera crane.",
                "Downward crane of the camera.",
                "The camera moves down on a crane.",
                "Craning shot lowering the camera.",
                "The camera lowers in a crane movement.",
                "Crane down with the camera.",
                "Lower the camera view using a crane shot.",
                "Crane the camera downward to reduce height.",
                "Descend the camera perspective with a crane.",
                "Lower the camera angle using a crane.",
                "Move the camera down in a craning motion.",
                "Adjust the camera to crane down.",
                "Bring down the camera view with a crane shot.",
                "The camera boom lowers.",
                "Descending crane movement of the camera.",
                "The camera falls in a crane shot.",
                "Vertical tracking of the camera downward on a crane.",
                "The view descends with the camera crane."
            ],
            "keyframes": [
                {
                    "CameraAnimationPivot": {
                        "position": [
                            0,
                            0,
                            2
                        ]
                    }
                },
                {
                    "CameraAnimationPivot": {
                        "position": [
                            0,
                            0,
                            0
                        ]
                    }
                }
            ]
        }
    ],
    "postprocessing": {
        "bloom": {
            "threshold_min": 0.7,
            "threshold_max": 1.0,
            "intensity_min": 0.0,
            "intensity_max": 1.0,
            "radius_min": 1.0,
            "radius_max": 10.0,
            "types": {
                "none": {
                    "intensity_min": 0.0,
                    "intensity_max": 0.02,
                    "descriptions": [
                        "No bloom effect applied.",
                        "The scene has no bloom effect.",
                        "Bloom effect is turned off.",
                        "The scene is rendered without bloom.",
                        "No bloom is used in the scene.",
                        "The scene does not have a bloom effect.",
                        "Bloom is disabled in the scene.",
                        "The scene is not enhanced with bloom.",
                        "No bloom is present in the scene.",
                        "The scene is not rendered with bloom."
                    ]
                },
                "low": {
                    "intensity_min": 0.02,
                    "intensity_max": 0.2,
                    "descriptions": [
                        "Low bloom effect applied.",
                        "The scene has a subtle bloom effect.",
                        "Bloom effect is set to low intensity.",
                        "The scene is rendered with a mild bloom effect.",
                        "Low bloom is used in the scene.",
                        "The scene has a slight bloom effect.",
                        "Bloom is set to low intensity in the scene.",
                        "The scene is enhanced with a gentle bloom effect.",
                        "Low bloom is present in the scene.",
                        "The scene is rendered with a mild bloom effect."
                    ]
                },
                "medium": {
                    "intensity_min": 0.2,
                    "intensity_max": 0.5,
                    "descriptions": [
                        "Medium bloom effect applied.",
                        "The scene has a moderate bloom effect.",
                        "Bloom effect is set to medium intensity.",
                        "The scene is rendered with a moderate bloom effect.",
                        "Medium bloom is used in the scene.",
                        "The scene has a noticeable bloom effect.",
                        "Bloom is set to medium intensity in the scene.",
                        "The scene is enhanced with a moderate bloom effect.",
                        "Medium bloom is present in the scene.",
                        "The scene is rendered with a moderate bloom effect."
                    ]
                },
                "high": {
                    "intensity_min": 0.5,
                    "intensity_max": 0.8,
                    "descriptions": [
                        "High bloom effect applied.",
                        "The scene has a strong bloom effect.",
                        "Bloom effect is set to high intensity.",
                        "The scene is rendered with a strong bloom effect.",
                        "High bloom is used in the scene.",
                        "The scene has a powerful bloom effect.",
                        "Bloom is set to high intensity in the scene.",
                        "The scene is enhanced with a strong bloom effect.",
                        "High bloom is present in the scene.",
                        "The scene is rendered with a strong bloom effect."
                    ]
                },
                "extreme": {
                    "intensity_min": 0.8,
                    "intensity_max": 1.1,
                    "descriptions": [
                        "Extreme bloom effect applied.",
                        "The scene has an intense bloom effect.",
                        "Bloom effect is set to extreme intensity.",
                        "The scene is rendered with an extreme bloom effect.",
                        "Extreme bloom is used in the scene.",
                        "The scene has an overwhelming bloom effect.",
                        "Bloom is set to extreme intensity in the scene.",
                        "The scene is enhanced with an extreme bloom effect.",
                        "Extreme bloom is present in the scene.",
                        "The scene is rendered with an extreme bloom effect."
                    ]
                }
            }
        },
        "ssao": {
            "distance_min": 0.02,
            "distance_max": 1.2,
            "factor_min": 0.0,
            "factor_max": 1.0,
            "types": {
                "none": {
                    "factor_min": 0.0,
                    "factor_max": 0.02,
                    "descriptions": [
                        "No ambient occlusion effect applied.",
                        "The scene has no ambient occlusion effect.",
                        "Ambient occlusion is turned off.",
                        "The scene is rendered without ambient occlusion.",
                        "No ambient occlusion is used in the scene.",
                        "The scene does not have an ambient occlusion effect.",
                        "Ambient occlusion is disabled in the scene.",
                        "The scene is not enhanced with ambient occlusion.",
                        "No ambient occlusion is present in the scene.",
                        "The scene is not rendered with ambient occlusion."
                    ]
                },
                "low": {
                    "factor_min": 0.02,
                    "factor_max": 0.2,
                    "descriptions": [
                        "Low ambient occlusion effect applied.",
                        "The scene has a subtle ambient occlusion effect.",
                        "Ambient occlusion is set to low intensity.",
                        "The scene is rendered with a mild ambient occlusion effect.",
                        "Low ambient occlusion is used in the scene.",
                        "The scene has a slight ambient occlusion effect.",
                        "Ambient occlusion is set to low intensity in the scene.",
                        "The scene is enhanced with a gentle ambient occlusion effect.",
                        "Low ambient occlusion is present in the scene.",
                        "The scene is rendered with a mild ambient occlusion effect."
                    ]
                },
                "medium": {
                    "factor_min": 0.2,
                    "factor_max": 0.6,
                    "descriptions": [
                        "Medium ambient occlusion effect applied.",
                        "The scene has a moderate ambient occlusion effect.",
                        "Ambient occlusion is set to medium intensity.",
                        "The scene is rendered with a moderate ambient occlusion effect.",
                        "Medium ambient occlusion is used in the scene.",
                        "The scene has a noticeable ambient occlusion effect.",
                        "Ambient occlusion is set to medium intensity in the scene.",
                        "The scene is enhanced with a moderate ambient occlusion effect.",
                        "Medium ambient occlusion is present in the scene.",
                        "The scene is rendered with a moderate ambient occlusion effect."
                    ]
                },
                "high": {
                    "factor_min": 0.6,
                    "factor_max": 1.0,
                    "descriptions": [
                        "High ambient occlusion effect applied.",
                        "The scene has a strong ambient occlusion effect.",
                        "Ambient occlusion is set to high intensity.",
                        "The scene is rendered with a strong ambient occlusion effect.",
                        "High ambient occlusion is used in the scene.",
                        "The scene has a powerful ambient occlusion effect.",
                        "Ambient occlusion is set to high intensity in the scene.",
                        "The scene is enhanced with a strong ambient occlusion effect.",
                        "High ambient occlusion is present in the scene.",
                        "The scene is rendered with a strong ambient occlusion effect."
                    ]
                },
                "extreme": {
                    "factor_min": 1.0,
                    "factor_max": 1.2,
                    "descriptions": [
                        "Extreme ambient occlusion effect applied.",
                        "The scene has an intense ambient occlusion effect.",
                        "Ambient occlusion is set to extreme intensity.",
                        "The scene is rendered with an extreme ambient occlusion effect.",
                        "Extreme ambient occlusion is used in the scene.",
                        "The scene has an overwhelming ambient occlusion effect.",
                        "Ambient occlusion is set to extreme intensity in the scene.",
                        "The scene is enhanced with an extreme ambient occlusion effect.",
                        "Extreme ambient occlusion is present in the scene.",
                        "The scene is rendered with an extreme ambient occlusion effect."
                    ]
                }
            }
        },
        "ssrr": {
            "min_max_roughness": 0.0,
            "max_max_roughness": 1.0,
            "min_thickness": 0.05,
            "max_thickness": 5.0,
            "types": {
                "none": {
                    "max_roughness_min": 0.0,
                    "max_roughness_max": 0.02,
                    "descriptions": [
                        "No screen-space ray tracing effect applied.",
                        "The scene has no screen-space ray tracing effect.",
                        "Screen-space ray tracing is turned off.",
                        "The scene is rendered without screen-space ray tracing.",
                        "No screen-space ray tracing is used in the scene.",
                        "The scene does not have a screen-space ray tracing effect.",
                        "Screen-space ray tracing is disabled in the scene.",
                        "The scene is not enhanced with screen-space ray tracing.",
                        "No screen-space ray tracing is present in the scene.",
                        "The scene is not rendered with screen-space ray tracing."
                    ]
                },
                "low": {
                    "max_roughness_min": 0.02,
                    "max_roughness_max": 0.1,
                    "descriptions": [
                        "Low screen-space ray tracing effect applied.",
                        "The scene has a subtle screen-space ray tracing effect.",
                        "Screen-space ray tracing is set to low intensity.",
                        "The scene is rendered with a mild screen-space ray tracing effect.",
                        "Low screen-space ray tracing is used in the scene.",
                        "The scene has a slight screen-space ray tracing effect.",
                        "Screen-space ray tracing is set to low intensity in the scene.",
                        "The scene is enhanced with a gentle screen-space ray tracing effect.",
                        "Low screen-space ray tracing is present in the scene.",
                        "The scene is rendered with a mild screen-space ray tracing effect."
                    ]
                },
                "medium": {
                    "max_roughness_min": 0.1,
                    "max_roughness_max": 0.3,
                    "descriptions": [
                        "Medium screen-space ray tracing effect applied.",
                        "The scene has a moderate screen-space ray tracing effect.",
                        "Screen-space ray tracing is set to medium intensity.",
                        "The scene is rendered with a moderate screen-space ray tracing effect.",
                        "Medium screen-space ray tracing is used in the scene.",
                        "The scene has a noticeable screen-space ray tracing effect.",
                        "Screen-space ray tracing is set to medium intensity in the scene.",
                        "The scene is enhanced with a moderate screen-space ray tracing effect.",
                        "Medium screen-space ray tracing is present in the scene.",
                        "The scene is rendered with a moderate screen-space ray tracing effect."
                    ]
                },
                "high": {
                    "max_roughness_min": 0.3,
                    "max_roughness_max": 0.6,
                    "descriptions": [
                        "High screen-space ray tracing effect applied.",
                        "The scene has a strong screen-space ray tracing effect.",
                        "Screen-space ray tracing is set to high intensity.",
                        "The scene is rendered with a strong screen-space ray tracing effect.",
                        "High screen-space ray tracing is used in the scene.",
                        "The scene has a powerful screen-space ray tracing effect.",
                        "Screen-space ray tracing is set to high intensity in the scene.",
                        "The scene is enhanced with a strong screen-space ray tracing effect.",
                        "High screen-space ray tracing is present in the scene.",
                        "The scene is rendered with a strong screen-space ray tracing effect."
                    ],
                    "extreme": {
                        "max_roughness_min": 0.6,
                        "max_roughness_max": 1.0,
                        "descriptions": [
                            "Extreme screen-space ray tracing effect applied.",
                            "The scene has an intense screen-space ray tracing effect.",
                            "Screen-space ray tracing is set to extreme intensity.",
                            "The scene is rendered with an extreme screen-space ray tracing effect.",
                            "Extreme screen-space ray tracing is used in the scene.",
                            "The scene has an overwhelming screen-space ray tracing effect.",
                            "Screen-space ray tracing is set to extreme intensity in the scene.",
                            "The scene is enhanced with an extreme screen-space ray tracing effect.",
                            "Extreme screen-space ray tracing is present in the scene.",
                            "The scene is rendered with an extreme screen-space ray tracing effect."
                        ]
                    }
                }
            }
        },
        "motionblur": {
            "shutter_speed_min": 0.0,
            "shutter_speed_max": 1.0,
            "types": {
                "none": {
                    "shutter_speed_min": 0.0,
                    "shutter_speed_max": 0.02,
                    "descriptions": [
                        "No motion blur effect applied.",
                        "The scene has no motion blur effect.",
                        "Motion blur is turned off.",
                        "The scene is rendered without motion blur.",
                        "No motion blur is used in the scene.",
                        "The scene does not have a motion blur effect.",
                        "Motion blur is disabled in the scene.",
                        "The scene is not enhanced with motion blur.",
                        "No motion blur is present in the scene.",
                        "The scene is not rendered with motion blur."
                    ]
                },
                "low": {
                    "shutter_speed_min": 0.02,
                    "shutter_speed_max": 0.2,
                    "descriptions": [
                        "Low motion blur effect applied.",
                        "The scene has a subtle motion blur effect.",
                        "Motion blur is set to low intensity.",
                        "The scene is rendered with a mild motion blur effect.",
                        "Low motion blur is used in the scene.",
                        "The scene has a slight motion blur effect.",
                        "Motion blur is set to low intensity in the scene.",
                        "The scene is enhanced with a gentle motion blur effect.",
                        "Low motion blur is present in the scene.",
                        "The scene is rendered with a mild motion blur effect."
                    ]
                },
                "medium": {
                    "shutter_speed_min": 0.2,
                    "shutter_speed_max": 0.5,
                    "descriptions": [
                        "Medium motion blur effect applied.",
                        "The scene has a moderate motion blur effect.",
                        "Motion blur is set to medium intensity.",
                        "The scene is rendered with a moderate motion blur effect.",
                        "Medium motion blur is used in the scene.",
                        "The scene has a noticeable motion blur effect.",
                        "Motion blur is set to medium intensity in the scene.",
                        "The scene is enhanced with a moderate motion blur effect.",
                        "Medium motion blur is present in the scene.",
                        "The scene is rendered with a moderate motion blur effect."
                    ]
                },
                "high": {
                    "shutter_speed_min": 0.5,
                    "shutter_speed_max": 0.8,
                    "descriptions": [
                        "High motion blur effect applied.",
                        "The scene has a strong motion blur effect.",
                        "Motion blur is set to high intensity.",
                        "The scene is rendered with a strong motion blur effect.",
                        "High motion blur is used in the scene.",
                        "The scene has a powerful motion blur effect.",
                        "Motion blur is set to high intensity in the scene.",
                        "The scene is enhanced with a strong motion blur effect.",
                        "High motion blur is present in the scene.",
                        "The scene is rendered with a strong motion blur effect."
                    ]
                },
                "extreme": {
                    "shutter_speed_min": 0.8,
                    "shutter_speed_max": 1.0,
                    "descriptions": [
                        "Extreme motion blur effect applied.",
                        "The scene has an intense motion blur effect.",
                        "Motion blur is set to extreme intensity.",
                        "The scene is rendered with an extreme motion blur effect.",
                        "Extreme motion blur is used in the scene.",
                        "The scene has an overwhelming motion blur effect.",
                        "Motion blur is set to extreme intensity in the scene.",
                        "The scene is enhanced with an extreme motion blur effect.",
                        "Extreme motion blur is present in the scene.",
                        "The scene is rendered with an extreme motion blur effect."
                    ]
                }
            }
        }
    }
}

Examples:

Example 1:
Prompt/caption: 

caption: A small wooden book with a lock, a teapot, text that says 'Geo Winter', and an axe are all in the scene. The text is behind the teapot, the axe is to the right of the teapot, and the book is behind both the axe and the teapot. The book moves backward slowly, the teapot moves forward slowly, the text slides left, and the axe moves forward. The camera follows the axe. The camera is angled right and level with the ground.  The scene has a slight blur effect. The scene is animated at a fast pace.

{
    "orientation_caption": "Camera orientation: Yaw: oblique right, Pitch: level with the ground.",
    "orientation": {
        "yaw": 317,
        "pitch": 1
    },
    "framing_caption": "Camera framing: Captures entire scene Set the fov of the camera to 74 degrees. (23.00 mm focal length)",
    "framing": {
        "fov": 74,
        "coverage_factor": 3.3787342191874163,
        "name": "extreme_wide"
    },
    "animation_caption": "Camera animation: Throughout the sequence, the camera follows a red, yellow, and black axe seamlessly. The scene transitions quickly with fast animation.",
    "animation": {
        "name": "crane_down",
        "keyframes": [
            {
                "CameraAnimationPivot": {
                    "position": [
                        0,
                        0,
                        2
                    ]
                }
            },
            {
                "CameraAnimationPivot": {
                    "position": [
                        0,
                        0,
                        0
                    ]
                }
            }
        ],
        "speed_factor": 1.3754731748375375
    },
    "postprocessing_caption": "Post-processing effects: The scene is rendered with a mild ambient occlusion effect. The scene has a slight motion blur effect.",
    "postprocessing": {
        "bloom": {
            "threshold": 0.9049127669422115,
            "intensity": 0.8086834007424443,
            "radius": 4.345852681550845,
            "type": "extreme"
        },
        "ssao": {
            "distance": 0.2675165509421571,
            "factor": 0.03757264803813665,
            "type": "low"
        },
        "ssrr": {
            "max_roughness": 0.674072407335585,
            "thickness": 0.7906668082985685,
            "type": "none"
        },
        "motionblur": {
            "shutter_speed": 0.1915879393539549,
            "type": "low"
        }
    },
}


Example 2:

Prompt/caption: A house with a roof is on the left and a skateboard ramp with a building is on the right. The house moves left and the skateboard ramp moves backward. The camera is positioned behind and to the right, tilted steeply downward, showing a zoomed-in view. The scene has subtle shadows and a slight ray tracing effect. The background is a Belfast Sunset with a grassy and rocky ground.

{
    "orientation_caption": "Camera orientation: Orientation: right back quarter, Angle: tilted down steeply.",
    "orientation": {
        "yaw": 214,
        "pitch": 69
    },
    "framing_caption": "Camera framing: Magnified view The camera has a 181 mm focal length.",
    "framing": {
        "fov": 11,
        "coverage_factor": 0.8407846352674209,
        "name": "extreme_closeup"
    },
    "animation_caption": "Camera animation:  Fast animation speed of 1.4x applied.",
    "animation": {
        "name": "zoom_in",
        "keyframes": [
            {
                "Camera": {
                    "angle_offset": 10
                }
            },
            {
                "Camera": {
                    "angle_offset": 0
                }
            }
        ],
        "speed_factor": 1.404395487155547
    },
    "postprocessing_caption": "Post-processing effects: The scene is enhanced with a gentle ambient occlusion effect. Low screen-space ray tracing effect applied.",
    "postprocessing": {
        "bloom": {
            "threshold": 0.8496130440000619,
            "intensity": 0.2220181839537102,
            "radius": 1.3457534686773542,
            "type": "medium"
        },
        "ssao": {
            "distance": 0.4896150467674612,
            "factor": 0.04480824053315857,
            "type": "low"
        },
        "ssrr": {
            "max_roughness": 0.09441042633095198,
            "thickness": 0.7098830677702582,
            "type": "low"
        },
        "motionblur": {
            "shutter_speed": 0.9803040919463857,
            "type": "extreme"
        }
    },
}

Example 3:
Prompt/caption: Show a stick with a blue and white handle, a blue crystal, and a blue and white bird, a light blue hat with white polka dots, a turquoise window with a blue shutter, a chicken in a yellow dress, and a house with trees, a pool, and cars. The chicken is to the right and behind the window. The window is in front of the hat. The stick is to the left of the hat. The hat is behind the window. The house is to the left of and behind the window. Camera follows the chicken as it moves. Camera is positioned low and far right. Use a very wide camera angle. The scene is set at night with cobblestone flooring, no bloom, and some motion blur.

{
    "orientation_caption": "Camera orientation: The camera is steeply downward, far back to the right.",
    "orientation": {
        "yaw": 225,
        "pitch": 40
    },
    "framing_caption": "Camera framing: Extremely wide coverage The camera has a 76 degree field of view. (22.00 mm focal length)",
    "framing": {
        "fov": 76,
        "coverage_factor": 3.8613973293159507,
        "name": "extreme_wide"
    },
    "animation_caption": "Camera animation: Capturing A low poly a chicken in a yellow dress in motion, the camera stays locked on target. The scene has a typical animation speed.",
    "animation": {
        "name": "orbit_left",
        "keyframes": [
            {
                "CameraAnimationRoot": {
                    "rotation": [
                        0,
                        0,
                        90
                    ]
                }
            },
            {
                "CameraAnimationRoot": {
                    "rotation": [
                        0,
                        0,
                        0
                    ]
                }
            }
        ],
        "speed_factor": 1.228949164388366
    },
    "postprocessing_caption": "Post-processing effects: No bloom is present in the scene. Medium motion blur is used in the scene.",
    "postprocessing": {
        "bloom": {
            "threshold": 0.95650677196721,
            "intensity": 0.017154654617546394,
            "radius": 6.005265759454469,
            "type": "none"
        },
        "ssao": {
            "distance": 0.7460410976901686,
            "factor": 0.7479792653337443,
            "type": "high"
        },
        "ssrr": {
            "max_roughness": 0.3143241035761323,
            "thickness": 4.2697366020954,
            "type": "high"
        },
        "motionblur": {
            "shutter_speed": 0.40866738731531493,
            "type": "medium"
        }
    },
}

You must include all attributes. Be sure to include keyframes and CameraAnimationRoot stuff. Go back and make sure you're not missing anhthing.

Generate the correct values for the orientation, framing, and postprocessing based on the caption:
"""


def parse_gemini_json(raw_output: str) -> Optional[dict]:
    """
    Parse the JSON output from the Gemini API.

    Args:
        raw_output (str): The raw output from the Gemini API.

    Returns:
        Optional[dict]: The parsed JSON output as a dictionary, or None if an error occurs.
    """

    try:
        if "```json" in raw_output:
            json_start = raw_output.index("```json") + 7
            json_end = raw_output.rindex("```")
            json_content = raw_output[json_start:json_end].strip()
        else:
            json_content = raw_output.strip()

        # Remove any leading or trailing commas
        json_content = json_content.strip(',')

        # If the content starts with a key (e.g., "objects":), wrap it in curly braces
        if json_content.strip().startswith('"') and ':' in json_content:
            json_content = "{" + json_content + "}"

        # Parse the JSON
        parsed_json = json.loads(json_content)
        
        print("Successfully parsed JSON:")
        print(json.dumps(parsed_json, indent=2))
        
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {str(e)}")
        return None


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


def generate_gemini(model, template, prompt):
    content = template + prompt

    try:
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(content)
        captions_content = response.text.strip()
        
        return captions_content
    except Exception as e:
        print(f"Error: {str(e)}")