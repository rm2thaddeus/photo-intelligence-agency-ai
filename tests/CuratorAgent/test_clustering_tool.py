import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from pathlib import Path
import json
import shutil
from CuratorAgent.tools.ClusterTool import ClusterTool

class TestClusterTool(unittest.TestCase):
    def setUp(self):
        # Create test data with proper CLIP-like embeddings
        self.test_items = [
            {
                "id": f"test_{i}",
                "embedding": np.random.rand(512).tolist(),  # 512-dim CLIP embeddings
                "metadata": {
                    "file_path": f"/path/to/file_{i}",
                    "media_type": "image" if i % 2 == 0 else "video"
                }
            }
            for i in range(20)
        ]
        
        self.test_output_dir = "test_clusters"
        
    def tearDown(self):
        # Clean up test directory and shared state
        if Path(self.test_output_dir).exists():
            shutil.rmtree(self.test_output_dir)
    
    def test_prepare_embeddings(self):
        """Test the embedding preparation method"""
        cluster_tool = ClusterTool(
            items=self.test_items,
            output_dir=self.test_output_dir
        )
        
        # Test with list embeddings
        embeddings = cluster_tool._prepare_embeddings()
        self.assertIsInstance(embeddings, np.ndarray)
        self.assertEqual(embeddings.shape, (20, 512))
        
        # Test with JSON string embeddings
        json_items = self.test_items.copy()
        for item in json_items:
            item['embedding'] = json.dumps(item['embedding'])
        
        cluster_tool.items = json_items
        embeddings = cluster_tool._prepare_embeddings()
        self.assertIsInstance(embeddings, np.ndarray)
        self.assertEqual(embeddings.shape, (20, 512))
    
    def test_clustering_basic(self):
        """Test basic clustering functionality"""
        cluster_tool = ClusterTool(
            items=self.test_items,
            min_cluster_size=3,
            min_samples=2,
            output_dir=self.test_output_dir
        )
        
        result = cluster_tool.run()
        
        # Check result structure
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
        
        # Check cluster structure
        for cluster_id, items in result["clusters"].items():
            for item in items:
                self.assertIn("id", item)
                self.assertIn("metadata", item)
                self.assertNotIn("embedding", item)  # Embeddings should not be in output
        
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
        self.assertEqual(len(result["noise_points"]), 1)  # Single item should be noise
        
        # Test with empty list
        empty_cluster_tool = ClusterTool(
            items=[],
            output_dir=self.test_output_dir
        )
        result = empty_cluster_tool.run()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["statistics"]["total_items"], 0)
        self.assertEqual(len(result["clusters"]), 0)
        self.assertEqual(len(result["noise_points"]), 0)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with invalid embeddings
        invalid_items = [{
            "id": "test_1",
            "embedding": "invalid_embedding",
            "metadata": {"file_path": "/test/path"}
        }]
        
        cluster_tool = ClusterTool(
            items=invalid_items,
            output_dir=self.test_output_dir
        )
        result = cluster_tool.run()
        self.assertEqual(result["status"], "error")
        self.assertIn("message", result)
        
        # Test with invalid min_cluster_size
        cluster_tool = ClusterTool(
            items=self.test_items,
            min_cluster_size=0,  # Invalid size
            output_dir=self.test_output_dir
        )
        result = cluster_tool.run()
        self.assertEqual(result["status"], "error")
    
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
        self.assertEqual(
            len(shared_results["clusters"]), 
            result["statistics"]["num_clusters"]
        )

if __name__ == '__main__':
    unittest.main() 