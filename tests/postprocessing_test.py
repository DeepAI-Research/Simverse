import bpy
from simian.object import setup_compositor_for_black_and_white, setup_compositor_for_cel_shading, setup_compositor_for_depth, enable_effect


def test_setup_compositor_for_black_and_white():
    bpy.ops.wm.open_mainfile(filepath="../scenes/empty.blend")
    context = bpy.context  # Using Blender's context
    setup_compositor_for_black_and_white(context)
    tree = context.scene.node_tree

    # Check if the correct nodes exist
    assert "CompositorNodeRLayers" in [node.bl_idname for node in tree.nodes]
    assert "CompositorNodeHueSat" in [node.bl_idname for node in tree.nodes]
    assert "CompositorNodeComposite" in [node.bl_idname for node in tree.nodes]

    # Assert connections between nodes
    hue_sat = next(node for node in tree.nodes if node.bl_idname == 'CompositorNodeHueSat')
    assert hue_sat.inputs['Saturation'].default_value == 0
    assert hue_sat.inputs['Value'].default_value == 2.0

    print("test_setup_compositor_for_black_and_white passed")


def test_setup_compositor_for_cel_shading():
    bpy.ops.wm.open_mainfile(filepath="../scenes/empty.blend")
    context = bpy.context
    setup_compositor_for_cel_shading(context)
    tree = context.scene.node_tree

    # Check if the correct nodes exist
    assert "CompositorNodeRLayers" in [node.bl_idname for node in tree.nodes]
    assert "CompositorNodeNormal" in [node.bl_idname for node in tree.nodes]
    assert "CompositorNodeValToRGB" in [node.bl_idname for node in tree.nodes]  # Assuming multiple color ramps
    assert "CompositorNodeMixRGB" in [node.bl_idname for node in tree.nodes]  # Assuming multiple mixes
    assert "CompositorNodeAlphaOver" in [node.bl_idname for node in tree.nodes]
    assert "CompositorNodeComposite" in [node.bl_idname for node in tree.nodes]

    print("test_setup_compositor_for_cel_shading passed")


def test_setup_compositor_for_depth():
    bpy.ops.wm.open_mainfile(filepath="../scenes/empty.blend")
    context = bpy.context
    setup_compositor_for_depth(context)
    tree = context.scene.node_tree

    # Check if the correct nodes exist
    assert "CompositorNodeRLayers" in [node.bl_idname for node in tree.nodes]
    assert "CompositorNodeNormalize" in [node.bl_idname for node in tree.nodes]
    assert "CompositorNodeComposite" in [node.bl_idname for node in tree.nodes]

    # Verify depth pass is enabled in the view layer
    assert context.view_layer.use_pass_z == True

    print("test_setup_compositor_for_depth passed")


def test_enable_effect():
    bpy.ops.wm.open_mainfile(filepath="../scenes/empty.blend")
    context = bpy.context

    # List of effects to test
    effects_to_test = ["black_and_white", "cel_shading", "depth"]

    for effect in effects_to_test:
        # Reset scene to default
        bpy.ops.wm.read_factory_settings(use_empty=True)
        context.scene.use_nodes = True
        context.view_layer.use_pass_normal = False
        context.view_layer.use_pass_diffuse_color = False
        context.view_layer.use_pass_environment = False
        context.view_layer.use_pass_z = False

        # Enable the effect
        enable_effect(context, effect)

        # Check if the scene nodes are set up correctly
        tree = context.scene.node_tree
        nodes = tree.nodes
        links = tree.links

        # Check if nodes specific to each effect are present
        if effect == "black_and_white":
            assert "CompositorNodeRLayers" in [node.bl_idname for node in nodes]
            assert "CompositorNodeHueSat" in [node.bl_idname for node in nodes]
            assert "CompositorNodeComposite" in [node.bl_idname for node in nodes]
            assert context.view_layer.use_pass_z == False
        elif effect == "cel_shading":
            assert "CompositorNodeRLayers" in [node.bl_idname for node in nodes]
            assert "CompositorNodeNormal" in [node.bl_idname for node in nodes]
            assert "CompositorNodeMixRGB" in [node.bl_idname for node in nodes]
            assert "CompositorNodeAlphaOver" in [node.bl_idname for node in nodes]
            assert context.view_layer.use_pass_normal == True
            assert context.view_layer.use_pass_diffuse_color == True
            assert context.view_layer.use_pass_environment == True
        elif effect == "depth":
            assert "CompositorNodeRLayers" in [node.bl_idname for node in nodes]
            assert "CompositorNodeNormalize" in [node.bl_idname for node in nodes]
            assert "CompositorNodeComposite" in [node.bl_idname for node in nodes]
            assert context.view_layer.use_pass_z == True
        
        print(f"Test passed for enabling {effect} effect.")


# Execute tests
if __name__ == "__main__":
    test_setup_compositor_for_black_and_white()
    test_setup_compositor_for_cel_shading()
    test_setup_compositor_for_depth()
    test_enable_effect()