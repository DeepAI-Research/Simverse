from unittest.mock import MagicMock

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

from simian.postprocessing import setup_compositor_for_black_and_white, setup_compositor_for_cel_shading, setup_compositor_for_depth


def mock_new_node(*args, **kwargs):
    """
    Mock for the nodes.new function in Blender.
    """
    node_type = kwargs.get('type', 'UnknownType')
    node = MagicMock()
    node.type = node_type
    node.inputs = MagicMock()
    node.outputs = MagicMock()
    return node


def test_setup_compositor_for_black_and_white():
    """
    Test the setup_compositor_for_black_and_white function.
    """
    context = MagicMock()
    scene = MagicMock()
    nodes = MagicMock()
    links = MagicMock()

    context.scene = scene
    scene.node_tree.nodes = nodes
    scene.node_tree.links = links
    nodes.new.side_effect = mock_new_node  # This now handles keyword arguments

    setup_compositor_for_black_and_white(context)

    # Assertions to ensure nodes are created and links are made
    nodes.new.assert_any_call(type="CompositorNodeRLayers")
    nodes.new.assert_any_call(type="CompositorNodeHueSat")
    nodes.new.assert_any_call(type="CompositorNodeComposite")
    assert links.new.called, "Links between nodes should be created"


def test_setup_compositor_for_cel_shading():
    """
    Test the setup_compositor_for_cel_shading function.
    """
    context = MagicMock()
    scene = MagicMock()
    nodes = MagicMock()
    links = MagicMock()

    context.scene = scene
    scene.node_tree.nodes = nodes
    scene.node_tree.links = links
    nodes.new.side_effect = mock_new_node

    setup_compositor_for_cel_shading(context)

    nodes.new.assert_any_call(type="CompositorNodeRLayers")
    nodes.new.assert_any_call(type="CompositorNodeNormal")
    nodes.new.assert_any_call(type="CompositorNodeValToRGB")
    nodes.new.assert_any_call(type="CompositorNodeMixRGB")
    nodes.new.assert_any_call(type="CompositorNodeAlphaOver")
    nodes.new.assert_any_call(type="CompositorNodeComposite")
    assert links.new.called
    print("============ Test Passed: test_setup_compositor_for_cel_shading ============")


def test_setup_compositor_for_depth():
    """
    Test the setup_compositor_for_depth function.
    """
    context = MagicMock()
    scene = MagicMock()
    nodes = MagicMock()
    links = MagicMock()

    context.scene = scene
    scene.node_tree.nodes = nodes
    scene.node_tree.links = links
    nodes.new.side_effect = mock_new_node

    setup_compositor_for_depth(context)

    nodes.new.assert_any_call(type="CompositorNodeRLayers")
    nodes.new.assert_any_call(type="CompositorNodeNormalize")
    nodes.new.assert_any_call(type="CompositorNodeComposite")
    assert links.new.called
    print("============ Test Passed: test_setup_compositor_for_depth ============")


if __name__ == "__main__":
    test_setup_compositor_for_black_and_white()
    test_setup_compositor_for_cel_shading()
    test_setup_compositor_for_depth()
    print("============ ALL TESTS PASSED ============")
