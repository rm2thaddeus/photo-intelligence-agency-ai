"""
📌 Purpose: Isolated test script for verifying CLIP and Qdrant setup
🔄 Latest Changes: Initial creation to test basic functionality
⚙️ Key Logic: Directly imports libraries to test them without existing modules
📂 Expected File Path: MediaManager/isolated_test.py
🧠 Reasoning: Created to test core dependencies without module import issues
"""

import os
import torch
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check for CUDA
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Test importing transformers
try:
    from transformers import CLIPProcessor, CLIPModel
    print("Successfully imported transformers")
except ImportError:
    print("Failed to import transformers")

# Test importing qdrant_client
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams, PointStruct
    print("Successfully imported qdrant_client")
except ImportError:
    print("Failed to import qdrant_client")

# Try loading CLIP model
try:
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model.to(device)
    print("Successfully loaded CLIP model")
except Exception as e:
    print(f"Failed to load CLIP model: {e}")

# Try connecting to Qdrant
try:
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
    
    qdrant_client = QdrantClient(
        host=qdrant_host,
        port=qdrant_port,
        timeout=5.0
    )
    
    # Simple health check
    collections = qdrant_client.get_collections()
    print(f"Successfully connected to Qdrant and got collections: {collections}")
except Exception as e:
    print(f"Failed to connect to Qdrant: {e}")

print("\nTest completed.") 