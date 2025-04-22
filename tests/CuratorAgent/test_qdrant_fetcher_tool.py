import unittest
from unittest.mock import patch, MagicMock
from CuratorAgent.tools.QdrantFetcherTool import QdrantFetcherTool
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, Range
from datetime import datetime

class TestQdrantFetcherTool(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_client.get_collection.return_value = self.mock_collection
        
        # Setup default scroll response
        self.mock_points = [
            {"id": 1, "payload": {"url": "test1.jpg", "type": "image", "timestamp": "2024-01-01"}},
            {"id": 2, "payload": {"url": "test2.jpg", "type": "image", "timestamp": "2024-01-02"}}
        ]
        self.mock_client.scroll.return_value = (self.mock_points, None)
        
        self.tool = QdrantFetcherTool(
            collection_name="test_collection",
            limit=10,
            media_type=None,
            start_date=None,
            end_date=None
        )
        self.tool._qdrant_client = self.mock_client

    @patch('CuratorAgent.tools.QdrantFetcherTool.QdrantClient')
    def test_basic_fetch(self, mock_qdrant):
        mock_qdrant.return_value = self.mock_client
        result = self.tool.run()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["media_items"]), 2)
        self.mock_client.scroll.assert_called_once()

    @patch('CuratorAgent.tools.QdrantFetcherTool.QdrantClient')
    def test_media_type_filter(self, mock_qdrant):
        mock_qdrant.return_value = self.mock_client
        self.tool.media_type = "image"
        result = self.tool.run()
        
        # Get the filter argument from the last call
        call_args = self.mock_client.scroll.call_args
        self.assertIsNotNone(call_args)
        filter_args = call_args[1]["filter"]
        
        # Verify filter conditions
        self.assertIsInstance(filter_args, Filter)
        self.assertEqual(len(filter_args.must), 1)
        self.assertIsInstance(filter_args.must[0], FieldCondition)
        self.assertEqual(filter_args.must[0].key, "type")
        self.assertEqual(filter_args.must[0].match.value, "image")

    @patch('CuratorAgent.tools.QdrantFetcherTool.QdrantClient')
    def test_date_range_filter(self, mock_qdrant):
        mock_qdrant.return_value = self.mock_client
        self.tool.start_date = "2024-01-01"
        self.tool.end_date = "2024-01-31"
        result = self.tool.run()
        
        call_args = self.mock_client.scroll.call_args
        self.assertIsNotNone(call_args)
        filter_args = call_args[1]["filter"]
        
        self.assertIsInstance(filter_args, Filter)
        self.assertEqual(len(filter_args.must), 1)  # Only date range filter
        date_condition = filter_args.must[0]
        self.assertIsInstance(date_condition, FieldCondition)
        self.assertEqual(date_condition.key, "timestamp")
        self.assertIsInstance(date_condition.range, Range)
        self.assertEqual(date_condition.range.gte, "2024-01-01")
        self.assertEqual(date_condition.range.lte, "2024-01-31")

    @patch('CuratorAgent.tools.QdrantFetcherTool.QdrantClient')
    def test_combined_filters(self, mock_qdrant):
        mock_qdrant.return_value = self.mock_client
        self.tool.media_type = "image"
        self.tool.start_date = "2024-01-01"
        self.tool.end_date = "2024-01-31"
        result = self.tool.run()
        
        call_args = self.mock_client.scroll.call_args
        self.assertIsNotNone(call_args)
        filter_args = call_args[1]["filter"]
        
        self.assertIsInstance(filter_args, Filter)
        self.assertEqual(len(filter_args.must), 2)  # Both type and date range filters

    @patch('CuratorAgent.tools.QdrantFetcherTool.QdrantClient')
    def test_pagination(self, mock_qdrant):
        mock_qdrant.return_value = self.mock_client
        self.tool.limit = 10
        result = self.tool.run()
        
        call_args = self.mock_client.scroll.call_args
        self.assertIsNotNone(call_args)
        self.assertEqual(call_args[1]["limit"], 10)
        self.assertIsNone(call_args[1]["offset"])

    @patch('CuratorAgent.tools.QdrantFetcherTool.QdrantClient')
    def test_error_handling(self, mock_qdrant):
        mock_qdrant.return_value = self.mock_client
        self.mock_client.scroll.side_effect = Exception("Database error")
        result = self.tool.run()
        
        self.assertEqual(result["status"], "error")
        self.assertIn("Database error", result["message"])

if __name__ == '__main__':
    unittest.main() 