import unittest
import os
import sys
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

from simian.distributed_vast import rent_nodes, start_workers, terminate_nodes, headers
from simian.utils import get_env_vars

class TestDistributedVast(unittest.TestCase):
    def test_rent_run_terminate(self):
        env_vars = get_env_vars()
        vast_api_key = os.getenv("VAST_API_KEY") or env_vars.get("VAST_API_KEY")
        
        # Assert that vast_api_key exists
        self.assertIsNotNone(vast_api_key, "Vast API key not found.")
        
        headers["Authorization"] = "Bearer " + vast_api_key
        
        max_price = 0.5
        max_nodes = 1
        image = "arfx/simian-worker:latest"
        env = None
        
        nodes = rent_nodes(max_price, max_nodes, image, vast_api_key, env)

        self.assertEqual(len(nodes), 1)
        
        start_workers(nodes, image)
        # Perform any additional assertions or checks here
        
        terminate_nodes(nodes)

if __name__ == "__main__":
    unittest.main()