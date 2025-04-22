import unittest
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import base test module first to set up mocks
from test_base import MockAgencySwarm

# Import test modules
from test_cluster_tool import TestClusterTool
from test_qdrant_fetcher_tool import TestQdrantFetcherTool
from test_summary_writer_tool import TestSummaryWriterTool
from test_html_gallery_writer_tool import TestHTMLGalleryWriterTool

def run_tests():
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestClusterTool))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQdrantFetcherTool))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSummaryWriterTool))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestHTMLGalleryWriterTool))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return 0 if all tests passed, 1 if any failed
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests()) 