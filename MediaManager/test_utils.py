"""
📌 Purpose: Test script for processing_utils module
🔄 Latest Changes: Initial creation to test processing_utils.py
⚙️ Key Logic: Imports and tests the processing_utils module
📂 Expected File Path: MediaManager/test_utils.py
🧠 Reasoning: Created to verify processing_utils module is working correctly
"""

from tools.processing_utils import (
    logger, 
    qdrant_client, 
    processor, 
    model, 
    DEVICE, 
    EMBEDDING_DIM, 
    QDRANT_COLLECTION_NAME,
    test_processing_utils
)

def main():
    print(f"DEVICE: {DEVICE}")
    print(f"EMBEDDING_DIM: {EMBEDDING_DIM}")
    print(f"QDRANT_COLLECTION_NAME: {QDRANT_COLLECTION_NAME}")
    print(f"Model is loaded: {model is not None}")
    print(f"Processor is loaded: {processor is not None}")
    print(f"Qdrant client is configured: {qdrant_client is not None}")
    
    print("\nRunning test_processing_utils():")
    result = test_processing_utils()
    print(f"Test result: {'PASSED' if result else 'FAILED'}")

if __name__ == "__main__":
    main() 