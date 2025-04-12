from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse
import logging
import time
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_qdrant(client, max_retries=5, delay=2):
    """Wait for Qdrant to become available"""
    for i in range(max_retries):
        try:
            # Simple health check
            client.get_collections()
            logger.info("Successfully connected to Qdrant!")
            return True
        except Exception as e:
            logger.warning(f"Attempt {i+1}/{max_retries} failed: {str(e)}")
            if i < max_retries - 1:
                time.sleep(delay)
    return False

def test_qdrant_connection():
    try:
        # Initialize Qdrant client
        client = QdrantClient(
            host="localhost",
            port=6333,
            timeout=5.0  # 5 second timeout
        )
        
        # Wait for Qdrant to become available
        if not wait_for_qdrant(client):
            logger.error("Failed to connect to Qdrant after multiple attempts")
            return False
        
        # Test collection name
        collection_name = "test_collection"
        
        try:
            # Try to get collection info (will fail if it doesn't exist)
            client.get_collection(collection_name)
            # If we get here, collection exists, so delete it
            client.delete_collection(collection_name)
            logger.info(f"Deleted existing collection: {collection_name}")
        except UnexpectedResponse:
            # Collection doesn't exist, which is fine
            pass
        
        # Create a test collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=512, distance=Distance.COSINE)
        )
        logger.info(f"Created test collection: {collection_name}")
        
        # Get collection info
        collection_info = client.get_collection(collection_name)
        logger.info(f"Collection info: {collection_info}")
        
        # Clean up
        client.delete_collection(collection_name)
        logger.info(f"Cleaned up test collection: {collection_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in Qdrant test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_qdrant_connection()
    sys.exit(0 if success else 1) 