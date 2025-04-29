import pytest
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse
import logging
import time

@pytest.fixture
def qdrant_client():
    return QdrantClient(host="localhost", port=6333, timeout=5.0)

def wait_for_qdrant(client, max_retries=5, delay=2):
    for i in range(max_retries):
        try:
            client.get_collections()
            return True
        except Exception:
            if i < max_retries - 1:
                time.sleep(delay)
    return False

def test_qdrant_connection(qdrant_client):
    client = qdrant_client
    assert wait_for_qdrant(client), "Failed to connect to Qdrant after multiple attempts"
    collection_name = "test_collection"
    # Clean up if exists
    try:
        client.get_collection(collection_name)
        client.delete_collection(collection_name)
    except UnexpectedResponse:
        pass
    # Create collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=512, distance=Distance.COSINE)
    )
    info = client.get_collection(collection_name)
    assert info is not None
    # Clean up
    client.delete_collection(collection_name) 