import unittest
from pathlib import Path
import json
import shutil
from CuratorAgent.tools.HTMLGalleryWriterTool import HTMLGalleryWriterTool

class TestHTMLGalleryWriterTool(unittest.TestCase):
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
        
        self.test_summaries = {
            "0": {
                "summary": "A collection of beach-related media including images and videos.",
                "item_count": 2,
                "media_types": {
                    "image": 1,
                    "video": 1
                }
            },
            "1": {
                "summary": "Mountain landscape photographs.",
                "item_count": 1,
                "media_types": {
                    "image": 1
                }
            }
        }
        
        self.test_output_dir = "test_gallery"
    
    def tearDown(self):
        # Clean up test directory
        if Path(self.test_output_dir).exists():
            shutil.rmtree(self.test_output_dir)
    
    def test_basic_gallery_generation(self):
        """Test basic gallery generation functionality"""
        gallery_tool = HTMLGalleryWriterTool(
            clusters=self.test_clusters,
            summaries=self.test_summaries,
            output_dir=self.test_output_dir,
            title="Test Gallery"
        )
        
        result = gallery_tool.run()
        
        # Check basic result structure
        self.assertEqual(result["status"], "success")
        self.assertIn("gallery_path", result)
        self.assertIn("statistics", result)
        
        # Check gallery structure
        gallery_path = Path(self.test_output_dir)
        self.assertTrue(gallery_path.exists())
        self.assertTrue((gallery_path / "index.html").exists())
        self.assertTrue((gallery_path / "css").exists())
        self.assertTrue((gallery_path / "js").exists())
        self.assertTrue((gallery_path / "media").exists())
        
        # Check CSS and JS files
        self.assertTrue((gallery_path / "css" / "style.css").exists())
        self.assertTrue((gallery_path / "js" / "gallery.js").exists())
    
    def test_html_content(self):
        """Test HTML content generation"""
        gallery_tool = HTMLGalleryWriterTool(
            clusters=self.test_clusters,
            summaries=self.test_summaries,
            output_dir=self.test_output_dir,
            title="Test Gallery"
        )
        
        result = gallery_tool.run()
        
        # Read and check HTML content
        html_file = Path(self.test_output_dir) / "index.html"
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Check basic HTML structure
        self.assertIn("<!DOCTYPE html>", html_content)
        self.assertIn("<title>Test Gallery</title>", html_content)
        self.assertIn("Test Gallery", html_content)  # Title in body
        
        # Check cluster content
        self.assertIn("beach_1.jpg", html_content)
        self.assertIn("beach_2.mp4", html_content)
        self.assertIn("mountain_1.jpg", html_content)
        
        # Check summaries
        self.assertIn("A collection of beach-related media", html_content)
        self.assertIn("Mountain landscape photographs", html_content)
    
    def test_empty_clusters(self):
        """Test handling of empty clusters"""
        empty_clusters = {}
        empty_summaries = {}
        
        gallery_tool = HTMLGalleryWriterTool(
            clusters=empty_clusters,
            summaries=empty_summaries,
            output_dir=self.test_output_dir,
            title="Empty Gallery"
        )
        
        result = gallery_tool.run()
        
        # Check result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["statistics"]["total_clusters"], 0)
        self.assertEqual(result["statistics"]["total_items"], 0)
        
        # Check empty gallery structure
        html_file = Path(self.test_output_dir) / "index.html"
        with open(html_file, 'r') as f:
            html_content = f.read()
        self.assertIn("No media clusters found", html_content)
    
    def test_error_handling(self):
        """Test error handling for invalid input"""
        # Test with invalid clusters format
        invalid_clusters = "not a dictionary"
        
        gallery_tool = HTMLGalleryWriterTool(
            clusters=invalid_clusters,
            summaries=self.test_summaries,
            output_dir=self.test_output_dir,
            title="Error Gallery"
        )
        
        result = gallery_tool.run()
        
        # Check error response
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result["message"].lower())
    
    def test_media_type_handling(self):
        """Test handling of different media types"""
        gallery_tool = HTMLGalleryWriterTool(
            clusters=self.test_clusters,
            summaries=self.test_summaries,
            output_dir=self.test_output_dir,
            title="Media Types Gallery"
        )
        
        result = gallery_tool.run()
        
        # Read HTML content
        html_file = Path(self.test_output_dir) / "index.html"
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Check image handling
        self.assertIn('data-type="image"', html_content)
        self.assertIn('beach_1.jpg', html_content)
        
        # Check video handling
        self.assertIn('data-type="video"', html_content)
        self.assertIn('beach_2.mp4', html_content)
        self.assertIn('video-overlay', html_content)

if __name__ == '__main__':
    unittest.main() 