print("starting object_test.py")
import subprocess
import sys
import os
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))

# Append the simian directory to sys.path
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

from simian.object import delete_all_empties, get_hierarchy_bbox, join_objects_in_hierarchy, lock_all_objects, normalize_object_scale, optimize_meshes_in_hierarchy, remove_loose_meshes, get_meshes_in_hierarchy, set_pivot_to_bottom, unlock_objects, unparent_keep_transform
import numpy as np
import bpy

# Test function for the hierarchy bounding box
def test_hierarchy_bbox():
    # Load an empty scene
    bpy.ops.wm.open_mainfile(filepath="../scenes/empty.blend")
    
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
    assert abs(calculated_width - expected_width) < 0.001, "Bounding box width is incorrect"

# Run the test
test_hierarchy_bbox()

def test_remove_small_geometry():
    current_dir = os.path.dirname(__file__)

    # Load an empty scene
    bpy.ops.wm.open_mainfile(filepath=os.path.join(current_dir, "../", "scenes/video_generation_v1.blend"))

    initial_objects = lock_all_objects()

    # Path to the GLB file
    glb_path = os.path.join(current_dir, "../", "examples", "dangling_parts.glb")
    
    # Load the model
    bpy.ops.import_scene.gltf(filepath=glb_path)
    
    # Assume the last object added is the root object (this may need to be adjusted based on actual structure)
    root_obj = bpy.data.objects[0]
        
    optimize_meshes_in_hierarchy(root_obj)
    
    join_objects_in_hierarchy(root_obj)
    
    remove_loose_meshes(root_obj)
        
    meshes = get_meshes_in_hierarchy(root_obj)
    obj = meshes[0]
    
    set_pivot_to_bottom(obj)
    unparent_keep_transform(obj)
    normalize_object_scale(obj)
    delete_all_empties()
    
    # set position to 0, 0, 0
    obj.location = (0, 0, 0)

    # go back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    unlock_objects(initial_objects)
    
    # Assert that the resulting object has fewer vertices than the initial count
    assert len(obj.data.vertices) > 0
    assert len(meshes) == 1

# def test_normalize_object_scale():
#     # load scene from ./scenes/empty.blend
#     bpy.ops.wm.open_mainfile(filepath="scenes/empty.blend")
#     context = bpy.context
    
#     models = ["examples/animated_model.glb", "examples/animated.glb", "examples/dangling_parts.glb", "examples/separate_faces.glb"]
#     for model_path in models:
#         # Reset the scene
#         bpy.ops.wm.read_factory_settings(use_empty=True)
        
#         # Load the model
#         object.load_object(model_path, context)
#         obj = bpy.data.objects[0]
        
#         # Call normalize_object_scale with a scale_factor of 1.0
#         object.normalize_object_scale(context, obj, scale_factor=1.0)
        
#         # Get the world coordinates of each vertex in the mesh
#         mesh = obj.data
#         world_coords = [obj.matrix_world @ v.co for v in mesh.vertices]
        
#         # Calculate the bounding box of the world coordinates
#         Convert world coordinates to numpy array
          # world_coords = np.array([obj.matrix_world @ v.co for v in mesh.vertices])

          # # Calculate the bounding box of the world coordinates
          # bbox_min = np.min(world_coords, axis=0)
          # bbox_max = np.max(world_coords, axis=0)
#         # Assert that all world coordinates are within the unit bounding box
#         assert all(bbox_min[i] >= -0.5 and bbox_max[i] <= 0.5 for i in range(3))
        
if __name__ == "__main__":
    # pytest.main(["-s", __file__])
    test_remove_small_geometry()