import unittest
import numpy as np
from pathlib import Path
import json
import shutil
from CuratorAgent.tools.ClusterTool import ClusterTool

class TestClusterTool(unittest.TestCase):
    def setUp(self):
        # Create test data
        self.test_items = [
            {
                "id": f"test_{i}",
                "embedding": np.random.rand(512).tolist(),  # Simulating CLIP embeddings
                "metadata": {
                    "file_path": f"/path/to/file_{i}",
                    "media_type": "image" if i % 2 == 0 else "video"
                }
            }
            for i in range(20)
        ]
        
        self.test_output_dir = "test_clusters"
        
    def tearDown(self):
        # Clean up test directory
        if Path(self.test_output_dir).exists():
            shutil.rmtree(self.test_output_dir)
    
    def test_clustering_basic(self):
        """Test basic clustering functionality"""
        cluster_tool = ClusterTool(
            items=self.test_items,
            min_cluster_size=3,
            min_samples=2,
            output_dir=self.test_output_dir
        )
        
        result = cluster_tool.run()
        
        # Check basic result structure
        self.assertEqual(result["status"], "success")
        self.assertIn("clusters", result)
        self.assertIn("noise_points", result)
        self.assertIn("statistics", result)
        self.assertIn("output_file", result)
        
        # Check statistics
        stats = result["statistics"]
        self.assertEqual(stats["total_items"], 20)
        self.assertGreaterEqual(stats["num_clusters"], 0)
        self.assertGreaterEqual(stats["noise_points"], 0)
        
        # Check output file
        output_file = Path(result["output_file"])
        self.assertTrue(output_file.exists())
        
        # Verify file content
        with open(output_file) as f:
            saved_data = json.load(f)
        self.assertIn("clusters", saved_data)
        self.assertIn("noise_points", saved_data)
        self.assertIn("statistics", saved_data)
    
    def test_clustering_edge_cases(self):
        """Test clustering with edge cases"""
        # Test with single item
        single_item = [self.test_items[0]]
        cluster_tool = ClusterTool(
            items=single_item,
            min_cluster_size=1,
            min_samples=1,
            output_dir=self.test_output_dir
        )
        result = cluster_tool.run()
        self.assertEqual(result["status"], "success")
        
        # Test with empty list
        empty_cluster_tool = ClusterTool(
            items=[],
            min_cluster_size=2,
            min_samples=1,
            output_dir=self.test_output_dir
        )
        result = empty_cluster_tool.run()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["statistics"]["total_items"], 0)
    
    def test_clustering_parameters(self):
        """Test clustering with different parameters"""
        # Test with larger min_cluster_size
        cluster_tool = ClusterTool(
            items=self.test_items,
            min_cluster_size=10,  # Larger cluster size
            min_samples=2,
            output_dir=self.test_output_dir
        )
        result = cluster_tool.run()
        self.assertEqual(result["status"], "success")
        
        # Test with larger min_samples
        cluster_tool = ClusterTool(
            items=self.test_items,
            min_cluster_size=3,
            min_samples=5,  # Larger min_samples
            output_dir=self.test_output_dir
        )
        result = cluster_tool.run()
        self.assertEqual(result["status"], "success")
    
    def test_shared_state(self):
        """Test if clustering results are stored in shared state"""
        cluster_tool = ClusterTool(
            items=self.test_items,
            min_cluster_size=3,
            min_samples=2,
            output_dir=self.test_output_dir
        )
        
        result = cluster_tool.run()
        shared_results = cluster_tool._shared_state.get("clustering_results")
        
        self.assertIsNotNone(shared_results)
        self.assertEqual(shared_results["statistics"], result["statistics"])

if __name__ == '__main__':
    unittest.main() 