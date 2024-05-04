import bpy
import bmesh

def create_stage(context, stage_size=(10, 10), stage_height=0.1):
    """
    Creates a simple stage object in the scene.
    """
    # Create a new plane object
    bpy.ops.mesh.primitive_plane_add(size=1)
    stage = context.active_object
    
    # Scale the stage to the desired size
    stage.scale = (stage_size[0], stage_size[1], 1)
    
    # Set the stage location to be at the bottom of the scene
    stage.location = (0, 0, -stage_height / 2)
    
    # Rename the stage object
    stage.name = "Stage"
    
    # Rescale the UVs based on the inverse of the scale multiplied by 2
    scale_x = 1 / (stage_size[0] * 2)
    scale_y = 1 / (stage_size[1] * 2)
    
    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Get the bmesh representation of the stage
    bm = bmesh.from_edit_mesh(stage.data)
    
    # Get the UV layer
    uv_layer = bm.loops.layers.uv.verify()
    
    # Iterate over the faces and rescale the UVs
    for face in bm.faces:
        for loop in face.loops:
            uv = loop[uv_layer].uv
            uv.x *= scale_x
            uv.y *= scale_y
    
    # Update the mesh and return to object mode
    bmesh.update_edit_mesh(stage.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return stage

def apply_stage_material(stage, combination):
    """
    Applies the stage material to the given stage object based on the combination settings.
    """
    # Get the stage material settings from the combination
    stage_material = combination.get('stage_material', {})
    
    # Create a new material for the stage
    material = bpy.data.materials.new(name="StageMaterial")
    
    # Assign the material to the stage object
    stage.data.materials.append(material)
    
    # Set the material properties based on the combination settings
    material.use_nodes = True
    nodes = material.node_tree.nodes
    
    # Clear existing nodes
    for node in nodes:
        nodes.remove(node)
    
    # Create shader nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # Set the principled BSDF properties
    principled.inputs['Base Color'].default_value = stage_material.get('color', (0.8, 0.8, 0.8, 1))
    principled.inputs['Roughness'].default_value = stage_material.get('roughness', 0.5)
    principled.inputs['Metallic'].default_value = stage_material.get('metallic', 0)
    
    # Check if a texture image is specified in the combination
    if 'texture_image' in stage_material:
        # Load the texture image
        texture_path = stage_material['texture_image']
        texture_image = bpy.data.images.load(texture_path)
        
        # Create a texture coordinate node and a texture image node
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_image = nodes.new(type='ShaderNodeTexImage')
        tex_image.image = texture_image
        
        # Connect the texture nodes
        links = material.node_tree.links
        links.new(tex_coord.outputs['UV'], tex_image.inputs['Vector'])
        links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
    
    # Connect the nodes
    links = material.node_tree.links
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])