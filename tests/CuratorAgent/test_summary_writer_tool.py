import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
import shutil
from CuratorAgent.tools.SummaryWriterTool import SummaryWriterTool

class TestSummaryWriterTool(unittest.TestCase):
    def setUp(self):
        # Create test data
        self.test_clusters = {
            "0": [
                {
                    "id": "test_1",
                    "metadata": {
                        "file_path": "/path/to/beach_1.jpg",
                        "media_type": "image",
                        "creation_time": "2024-01-01T12:00:00"
                    }
                },
                {
                    "id": "test_2",
                    "metadata": {
                        "file_path": "/path/to/beach_2.mp4",
                        "media_type": "video",
                        "creation_time": "2024-01-01T13:00:00",
                        "duration": "00:02:30"
                    }
                }
            ],
            "1": [
                {
                    "id": "test_3",
                    "metadata": {
                        "file_path": "/path/to/mountain_1.jpg",
                        "media_type": "image",
                        "creation_time": "2024-01-02T12:00:00"
                    }
                }
            ]
        }
        
        self.test_output_dir = "test_summaries"
        
        # Mock OpenAI response
        self.mock_response = MagicMock()
        self.mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="This is a test summary for the cluster."
                )
            )
        ]
    
    def tearDown(self):
        # Clean up test directory
        if Path(self.test_output_dir).exists():
            shutil.rmtree(self.test_output_dir)
    
    @patch('CuratorAgent.tools.SummaryWriterTool.client')
    def test_basic_summary_generation(self, mock_client):
        """Test basic summary generation functionality"""
        mock_client.chat.completions.create.return_value = self.mock_response
        
        summary_tool = SummaryWriterTool(
            clusters=self.test_clusters,
            output_dir=self.test_output_dir
        )
        
        result = summary_tool.run()
        
        # Check basic result structure
        self.assertEqual(result["status"], "success")
        self.assertIn("summaries", result)
        self.assertIn("statistics", result)
        self.assertIn("output_file", result)
        
        # Check statistics
        stats = result["statistics"]
        self.assertEqual(stats["total_clusters"], 2)
        self.assertEqual(stats["total_items"], 3)
        
        # Check summaries
        summaries = result["summaries"]
        self.assertEqual(len(summaries), 2)
        self.assertIn("0", summaries)
        self.assertIn("1", summaries)
        
        # Check output file
        output_file = Path(result["output_file"])
        self.assertTrue(output_file.exists())
        
        # Verify file content
        with open(output_file) as f:
            saved_data = json.load(f)
        self.assertIn("summaries", saved_data)
        self.assertIn("statistics", saved_data)
    
    @patch('CuratorAgent.tools.SummaryWriterTool.client')
    def test_cluster_metadata_analysis(self, mock_client):
        """Test cluster metadata analysis"""
        mock_client.chat.completions.create.return_value = self.mock_response
        
        summary_tool = SummaryWriterTool(
            clusters=self.test_clusters,
            output_dir=self.test_output_dir
        )
        
        result = summary_tool.run()
        
        # Check media type counts in summaries
        cluster_0_summary = result["summaries"]["0"]
        self.assertEqual(cluster_0_summary["media_types"]["image"], 1)
        self.assertEqual(cluster_0_summary["media_types"]["video"], 1)
        
        cluster_1_summary = result["summaries"]["1"]
        self.assertEqual(cluster_1_summary["media_types"]["image"], 1)
        self.assertNotIn("video", cluster_1_summary["media_types"])
    
    @patch('CuratorAgent.tools.SummaryWriterTool.client')
    def test_empty_clusters(self, mock_client):
        """Test handling of empty clusters"""
        mock_client.chat.completions.create.return_value = self.mock_response
        
        empty_clusters = {}
        summary_tool = SummaryWriterTool(
            clusters=empty_clusters,
            output_dir=self.test_output_dir
        )
        
        result = summary_tool.run()
        
        # Check empty result
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["summaries"]), 0)
        self.assertEqual(result["statistics"]["total_clusters"], 0)
        self.assertEqual(result["statistics"]["total_items"], 0)
    
    @patch('CuratorAgent.tools.SummaryWriterTool.client')
    def test_api_error_handling(self, mock_client):
        """Test handling of OpenAI API errors"""
        # Simulate API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        summary_tool = SummaryWriterTool(
            clusters=self.test_clusters,
            output_dir=self.test_output_dir
        )
        
        result = summary_tool.run()
        
        # Check error handling
        self.assertEqual(result["status"], "error")
        self.assertIn("API Error", result["message"])
    
    @patch('CuratorAgent.tools.SummaryWriterTool.client')
    def test_shared_state(self, mock_client):
        """Test if summaries are stored in shared state"""
        mock_client.chat.completions.create.return_value = self.mock_response
        
        summary_tool = SummaryWriterTool(
            clusters=self.test_clusters,
            output_dir=self.test_output_dir
        )
        
        result = summary_tool.run()
        shared_results = summary_tool._shared_state.get("cluster_summaries")
        
        self.assertIsNotNone(shared_results)
        self.assertEqual(shared_results["statistics"], result["statistics"])

if __name__ == '__main__':
    unittest.main() 