import os
import sys
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))

# Append the simian directory to sys.path
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

from simian.scene import download_texture, create_stage, apply_stage_material
import bpy

# Setup test data
test_data = {
    "stage": {
        "material": {
            "maps": {
                "Diffuse": "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/4k/brick_wall_04/brick_wall_04_diff_4k.jpg",
                "nor_dx": "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/4k/brick_wall_04/brick_wall_04_nor_dx_4k.jpg",
                "nor_gl": "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/4k/brick_wall_04/brick_wall_04_nor_gl_4k.jpg",
                "arm": "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/4k/brick_wall_04/brick_wall_04_arm_4k.jpg",
                "AO": "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/4k/brick_wall_04/brick_wall_04_ao_4k.jpg",
                "Rough": "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/4k/brick_wall_04/brick_wall_04_rough_4k.jpg",
                "Displacement": "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/4k/brick_wall_04/brick_wall_04_disp_4k.jpg"
            },
            "name": "Brick Wall 04"
        }
    }
}


def test_download_texture():
    material_name = test_data["stage"]["material"]["name"]
    for texture_name, url in test_data["stage"]["material"]["maps"].items():
        expected_path = os.path.join("materials", material_name, f"{texture_name}.jpg")
        result_path = download_texture(url, material_name, texture_name)
        assert os.path.exists(result_path), f"Failed to download texture: {texture_name}"
        print(f"Texture {texture_name} downloaded successfully.")


def test_create_stage():
    """Test creating a stage and applying materials."""
    bpy.ops.wm.open_mainfile(filepath="../scenes/empty.blend")  # Make sure this path is correct
    stage = create_stage(test_data, (100, 100), 0.002)
    apply_stage_material(stage, test_data)
    
    assert stage.scale == (100, 100, 1), "Stage scale is incorrect"
    assert stage.location == (0, 0, 0.002), "Stage location is incorrect"
    assert stage.name == "Stage", "Stage name is not set correctly"

    print("Stage created and material applied successfully.")


# Run tests if this file is executed as a script
if __name__ == "__main__":
    pytest.main()