import math
import bpy


def create_camera_rig() -> bpy.types.Object:
    """
    Creates a camera rig consisting of multiple objects in Blender.

    Returns:
        dict: A dictionary containing the created objects:
            - camera_animation_root: The root object of the camera animation hierarchy.
            - camera_orientation_pivot_yaw: The yaw pivot object for camera orientation.
            - camera_orientation_pivot_pitch: The pitch pivot object for camera orientation.
            - camera_framing_pivot: The pivot object for camera framing.
            - camera_animation_pivot: The pivot object for camera animation.
            - camera_object: The camera object.
            - camera: The camera data.
    """
    camera_animation_root = bpy.data.objects.new("CameraAnimationRoot", None)
    bpy.context.scene.collection.objects.link(camera_animation_root)

    camera_orientation_pivot_yaw = bpy.data.objects.new(
        "CameraOrientationPivotYaw", None
    )
    camera_orientation_pivot_yaw.parent = camera_animation_root
    bpy.context.scene.collection.objects.link(camera_orientation_pivot_yaw)

    camera_orientation_pivot_pitch = bpy.data.objects.new(
        "CameraOrientationPivotPitch", None
    )
    camera_orientation_pivot_pitch.parent = camera_orientation_pivot_yaw
    bpy.context.scene.collection.objects.link(camera_orientation_pivot_pitch)

    camera_framing_pivot = bpy.data.objects.new("CameraFramingPivot", None)
    camera_framing_pivot.parent = camera_orientation_pivot_pitch
    bpy.context.scene.collection.objects.link(camera_framing_pivot)

    camera_animation_pivot = bpy.data.objects.new("CameraAnimationPivot", None)
    camera_animation_pivot.parent = camera_framing_pivot
    bpy.context.scene.collection.objects.link(camera_animation_pivot)

    camera = bpy.data.cameras.new("Camera")
    camera_object = bpy.data.objects.new("Camera", camera)
    
    # rotate the Camera 90º,
    camera_object.delta_rotation_euler = [1.5708, 0, 1.5708]
    
    camera_object.parent = camera_animation_pivot
    bpy.context.scene.collection.objects.link(camera_object)

    bpy.context.scene.camera = camera_object

    return {
        "camera_animation_root": camera_animation_root,
        "camera_orientation_pivot_yaw": camera_orientation_pivot_yaw,
        "camera_orientation_pivot_pitch": camera_orientation_pivot_pitch,
        "camera_framing_pivot": camera_framing_pivot,
        "camera_animation_pivot": camera_animation_pivot,
        "camera_object": camera_object,
        "camera": camera,
    }


def set_camera_settings(combination: dict) -> None:
    """
    Applies camera settings from a combination to the Blender scene.

    This function updates various camera settings including orientation, pivot adjustments, and
    framing based on the provided combination dictionary.

    Args:
        combination (dict): A dictionary containing camera settings including 'fov', 'animation',
                            and orientation details.
    Returns:
        None
    """
    camera = bpy.context.scene.objects["Camera"]
    
    # get the camera on the camera object
    camera = camera.data

    camera.lens = combination["framing"]["fov"]

    orientation_data = combination["orientation"]

    orientation = {"pitch": orientation_data["pitch"], "yaw": orientation_data["yaw"]}

    # Rotate CameraOrientationPivotYaw by the Y
    camera_orientation_pivot_yaw = bpy.data.objects.get("CameraOrientationPivotYaw")

    # Convert from degrees to radians. orientation['pitch'] is in degrees, but Blender uses radians
    camera_orientation_pivot_yaw.rotation_euler[2] = orientation["yaw"] * math.pi / 180

    # Rotate CameraOrientationPivotPitch by the X
    camera_orientation_pivot_pitch = bpy.data.objects.get("CameraOrientationPivotPitch")

    # Apply the pitch rotation adjustment. Negative sign used to invert the rotation for upward pitch in Blender's coordinate system.
    camera_orientation_pivot_pitch.rotation_euler[1] = (
        orientation["pitch"] * -math.pi / 180
    )
    framing = combination["framing"]

    # Set the root of the whole rig to the orientation position
    camera_animation_root = bpy.data.objects.get("CameraAnimationRoot")

    # TODO: Get the center of the bounding box of the focus object and set the camera to that position
    camera_animation_root.location = [0, 0, 0.5]

    # Set the CameraFramingPivot X to the framing
    camera_framing_pivot = bpy.data.objects.get("CameraFramingPivot")
    camera_framing_pivot.location = framing["position"]
    set_camera_animation(combination)


def set_camera_animation(combination: dict, frame_distance: int = 120) -> None:
    """
    Applies the specified animation to the camera based on the keyframes from the camera_data.json file.

    Args:
        animation_name (str): The name of the animation to apply to the camera.
        camera_data (dict): The dictionary containing the camera data from the JSON file.

    Raises:
        ValueError: If the animation is not found in the camera data.

    Returns:
        None
    """
    # Find the animation in the camera data
    animation = combination["animation"]

    # Get the keyframes from the animation
    keyframes = animation["keyframes"]

    # Iterate over the keyframes and apply the transformations to the corresponding objects
    for i, keyframe in enumerate(keyframes):
        for obj_name, transforms in keyframe.items():
            obj = bpy.data.objects.get(obj_name)
            if obj is None:
                raise ValueError(f"Object {obj_name} not found in the scene")

            # Set the keyframe for each transformation
            frame = i * frame_distance
            for transform_name, value in transforms.items():
                if transform_name == "position":
                    obj.location = value
                    obj.keyframe_insert(data_path="location", frame=frame)
                elif transform_name == "rotation":
                    obj.rotation_euler = [math.radians(angle) for angle in value]
                    obj.keyframe_insert(data_path="rotation_euler", frame=frame)
                elif transform_name == "scale":
                    obj.scale = value
                    obj.keyframe_insert(data_path="scale", frame=frame)

    # Set the current frame to the start of the animation
    bpy.context.scene.frame_set(0)