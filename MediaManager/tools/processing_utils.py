import logging
import os
import torch
from transformers import CLIPProcessor, CLIPModel
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
EMBEDDING_DIM = 512
QDRANT_COLLECTION_NAME = "media_embeddings"

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

# Initialize CLIP model and processor
try:
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model.to(DEVICE)
    logger.info(f"CLIP model loaded successfully on {DEVICE}")
except Exception as e:
    logger.error(f"Error loading CLIP model: {e}")
    model = None
    processor = None

# Initialize Qdrant client
try:
    # Get host and port from environment variables with defaults
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
    
    qdrant_client = QdrantClient(
        host=qdrant_host,
        port=qdrant_port,
        timeout=5.0
    )
    
    # Wait for Qdrant to be available
    if wait_for_qdrant(qdrant_client):
        # Check if collection exists, create if it doesn't
        try:
            qdrant_client.get_collection(QDRANT_COLLECTION_NAME)
            logger.info(f"Connected to existing Qdrant collection: {QDRANT_COLLECTION_NAME}")
        except UnexpectedResponse:
            # Collection doesn't exist, create it
            qdrant_client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIM,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created new Qdrant collection: {QDRANT_COLLECTION_NAME}")
    else:
        logger.error("Failed to connect to Qdrant")
        qdrant_client = None
except Exception as e:
    logger.error(f"Error initializing Qdrant client: {e}")
    qdrant_client = None

# Add a test function for verifying the processing_utils module
def test_processing_utils():
    """Test function to verify processing_utils functionality"""
    if model is None or processor is None:
        logger.error("CLIP model or processor not initialized")
        return False
    
    if qdrant_client is None:
        logger.error("Qdrant client not initialized")
        return False
    
    logger.info(f"Processing utils initialized successfully - Device: {DEVICE}")
    return True

# If this file is run directly, execute the test function
if __name__ == "__main__":
    result = test_processing_utils()
    print(f"Processing utils test: {'PASSED' if result else 'FAILED'}") 