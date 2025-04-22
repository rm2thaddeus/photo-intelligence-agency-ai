"""
📌 Purpose: Direct test script for processing_utils module
🔄 Latest Changes: Initial creation to test processing_utils.py directly
⚙️ Key Logic: Imports processing_utils directly without agency_swarm dependency
📂 Expected File Path: MediaManager/direct_test.py
🧠 Reasoning: Created to verify processing_utils module is working correctly without dependency issues
"""

import sys
import os

# Add the current directory to the path so we can import the modules directly
sys.path.insert(0, os.path.abspath('.'))

try:
    # Direct import of the module (not through the package structure)
    import tools.processing_utils as utils
    
    print(f"DEVICE: {utils.DEVICE}")
    print(f"EMBEDDING_DIM: {utils.EMBEDDING_DIM}")
    print(f"QDRANT_COLLECTION_NAME: {utils.QDRANT_COLLECTION_NAME}")
    print(f"Model is loaded: {utils.model is not None}")
    print(f"Processor is loaded: {utils.processor is not None}")
    print(f"Qdrant client is configured: {utils.qdrant_client is not None}")
    
    print("\nRunning test_processing_utils():")
    result = utils.test_processing_utils()
    print(f"Test result: {'PASSED' if result else 'FAILED'}")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 