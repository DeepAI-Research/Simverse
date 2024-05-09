import os
from unittest.mock import patch
import pandas as pd
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

from simian.batch import render_objects
from simian.utils import get_combination_objects

def test_get_combination_objects():
    """
    Test the get_combination_objects function.
    """
    # Setup the expected DataFrame
    expected_df = pd.DataFrame({'id': [1, 2], 'name': ['Object1', 'Object2']})
    
    # Mock pd.read_json to return a specific DataFrame
    with patch('pandas.read_json', return_value=expected_df):
        df = get_combination_objects()
        pd.testing.assert_frame_equal(df, expected_df)
        print("============ Test Passed: test_get_combination_objects ============")


def test_render_objects():
    """
    Test the render_objects function.
    """
    download_dir = "/fake/download/path"
    processes = 4
    save_repo_format = "zip"
    render_timeout = 3000
    width = 1920
    height = 1080
    start_index = 0
    end_index = 1
    start_frame = 1
    end_frame = 65

    # Call the function
    try:
        render_objects(
            download_dir=download_dir,
            processes=processes,
            save_repo_format=save_repo_format,
            render_timeout=render_timeout,
            width=width,
            height=height,
            start_index=start_index,
            end_index=end_index,
            start_frame=start_frame,
            end_frame=end_frame,
        )
        print("============ Test Passed: render_objects ============")
    except Exception as e:
        print("============ Test Failed: render_objects ============")
        print(f"Error: {e}")
        raise e


if __name__ == "__main__":
    test_get_combination_objects()
    test_render_objects()
    print("============ ALL TESTS PASSED ============")