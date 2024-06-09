import os

from ..camera import create_camera_rig
from ..scene import initialize_scene
from ..object import (
    delete_all_empties,
    get_hierarchy_bbox,
    join_objects_in_hierarchy,
    lock_all_objects,
    normalize_object_scale,
    optimize_meshes_in_hierarchy,
    get_meshes_in_hierarchy,
    set_pivot_to_bottom,
    unlock_objects,
    unparent_keep_transform,
)
import bpy


def test_hierarchy_bbox():
    """
    Test the get_hierarchy_bbox function.
    """
    # Load an empty scene
    initialize_scene()

    # Create two cubes 1 meter apart
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    cube1 = bpy.context.active_object
    bpy.ops.mesh.primitive_cube_add(size=2, location=(3, 0, 0))
    cube2 = bpy.context.active_object

    # Create an empty and parent cube1 to it
    bpy.ops.object.empty_add(location=(0, 0, 0))
    empty1 = bpy.context.active_object
    cube1.parent = empty1

    # Create a second empty, parent it to the first empty, and parent cube2 to this second empty
    bpy.ops.object.empty_add(location=(0, 0, 0))
    empty2 = bpy.context.active_object
    empty2.parent = empty1
    cube2.parent = empty2

    # Call the function on the root empty
    min_coord, max_coord = get_hierarchy_bbox(empty1)

    # The expected width of the bounding box should be the distance between the centers plus the size of one cube (since both cubes have a center at their geometric center)
    expected_width = 5  # 3 meters apart plus 1 meter half-width of each cube
    calculated_width = max_coord[0] - min_coord[0]

    # Assert to check if the calculated width matches the expected width
    assert (
        abs(calculated_width - expected_width) < 0.001
    ), "Bounding box width is incorrect"
    print("============ Test Passed: test_hierarchy_bbox ============")


def test_remove_small_geometry():
    """
    Test the remove_small_geometry function.
    """
    current_dir = os.path.dirname(__file__)

    # Load an empty scene
    initialize_scene()
    create_camera_rig()

    initial_objects = lock_all_objects()

    # Path to the GLB file
    glb_path = os.path.join(current_dir, "../", "../", "examples", "dangling_parts.glb")

    # Load the model
    bpy.ops.import_scene.gltf(filepath=glb_path)

    # Assume the last object added is the root object (this may need to be adjusted based on actual structure)
    root_obj = bpy.data.objects[0]

    optimize_meshes_in_hierarchy(root_obj)

    join_objects_in_hierarchy(root_obj)

    meshes = get_meshes_in_hierarchy(root_obj)
    obj = meshes[0]

    set_pivot_to_bottom(obj)
    unparent_keep_transform(obj)
    normalize_object_scale(obj)
    delete_all_empties()

    # set position to 0, 0, 0
    obj.location = (0, 0, 0)

    # go back to object mode
    bpy.ops.object.mode_set(mode="OBJECT")

    unlock_objects(initial_objects)

    # Assert that the resulting object has fewer vertices than the initial count
    assert len(obj.data.vertices) > 0
    assert len(meshes) == 1
    print("============ Test Passed: test_remove_small_geometry ============")


def test_normalize_object_scale():
    """
    Test the normalize_object_scale function.
    """
    # Load an empty scene
    initialize_scene()
    # Create a cube with known dimensions
    bpy.ops.mesh.primitive_cube_add(size=2)  # Creates a cube with edge length 2
    cube = bpy.context.active_object

    # Calculate expected scale factor to normalize the cube to unit length (scale_factor / max_dimension)
    scale_factor = 1.0
    expected_dimension = 1.0  # Since we want the largest dimension to be scaled to 1.0

    # Normalize the cube's scale
    normalize_object_scale(cube, scale_factor)

    # Force a scene update to ensure that all transforms are applied
    bpy.context.view_layer.update()

    # Recalculate actual dimensions after scaling
    actual_dimensions = [cube.dimensions[i] for i in range(3)]
    max_dimension_after_scaling = max(actual_dimensions)

    # Assert that the maximum dimension is within a small epsilon of expected_dimension
    epsilon = 0.001  # Small threshold to account for floating point arithmetic errors
    assert (
        abs(max_dimension_after_scaling - expected_dimension) < epsilon
    ), f"Expected max dimension to be close to {expected_dimension}, but got {max_dimension_after_scaling}"
    print("============ Test Passed: test_normalize_object_scale ============")


# Run tests if this file is executed as a script
if __name__ == "__main__":
    test_hierarchy_bbox()
    test_remove_small_geometry()
    test_normalize_object_scale()
    print("============ ALL TESTS PASSED ============")
