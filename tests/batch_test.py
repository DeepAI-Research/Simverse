import multiprocessing
import os
import subprocess
from unittest.mock import patch, MagicMock
import pytest
import pandas as pd
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
# Append the simian directory to sys.path
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

from simian.batch import render_objects, get_combination_objects


def test_get_combination_objects():
    # Setup the expected DataFrame
    expected_df = pd.DataFrame({'id': [1, 2], 'name': ['Object1', 'Object2']})
    
    # Mock pd.read_json to return a specific DataFrame
    with patch('pandas.read_json', return_value=expected_df):
        df = get_combination_objects()
        pd.testing.assert_frame_equal(df, expected_df)


if __name__ == "__main__":
    test_get_combination_objects()
    print("All tests passed")
