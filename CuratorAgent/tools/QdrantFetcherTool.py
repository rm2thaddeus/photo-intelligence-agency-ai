from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from qdrant_client.http.models import Range

load_dotenv()

# Initialize Qdrant client
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "media_collection")

qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

class QdrantFetcherTool(BaseTool):
    """
    Retrieves media items and their metadata from Qdrant database.
    Supports filtering by various criteria and pagination.
    """
    
    limit: int = Field(
        default=100,
        description="Maximum number of items to retrieve"
    )
    
    offset: int = Field(
        default=0,
        description="Number of items to skip"
    )
    
    media_type: Optional[str] = Field(
        default=None,
        description="Filter by media type ('image' or 'video')"
    )
    
    date_range: Optional[Dict[str, str]] = Field(
        default=None,
        description="Filter by date range with 'start' and 'end' dates in ISO format"
    )
    
    def _build_filter(self) -> Optional[Filter]:
        """Builds Qdrant filter based on provided parameters."""
        must_conditions = []
        
        if self.media_type:
            must_conditions.append(
                FieldCondition(
                    key="media_type",
                    match=MatchValue(value=self.media_type)
                )
            )
            
        if self.date_range:
            must_conditions.append(
                FieldCondition(
                    key="file_creation_time",
                    range=Range(
                        gte=self.date_range.get("start"),
                        lte=self.date_range.get("end")
                    )
                )
            )
            
        return Filter(must=must_conditions) if must_conditions else None

    def run(self) -> Dict[str, Any]:
        """
        Retrieves media items from Qdrant based on specified filters.
        Returns dictionary with items and total count.
        """
        try:
            # Build filter
            search_filter = self._build_filter()
            
            # Get total count
            collection_info = qdrant_client.get_collection(QDRANT_COLLECTION_NAME)
            total_points = collection_info.points_count
            
            # Retrieve points
            response = qdrant_client.scroll(
                collection_name=QDRANT_COLLECTION_NAME,
                limit=self.limit,
                offset=self.offset,
                with_payload=True,
                with_vectors=True,
                filter=search_filter
            )
            
            # Extract points data
            items = []
            for point in response[0]:
                item_data = {
                    "id": point.id,
                    "embedding": point.vector,
                    "metadata": point.payload
                }
                items.append(item_data)
            
            return {
                "status": "success",
                "total_items": total_points,
                "items": items,
                "offset": self.offset,
                "limit": self.limit
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

# Example test case
if __name__ == "__main__":
    # Test the tool
    fetcher = QdrantFetcherTool(
        limit=5,
        media_type="image",
        date_range={
            "start": "2024-01-01T00:00:00",
            "end": "2024-12-31T23:59:59"
        }
    )
    result = fetcher.run()
    print("\nFetch Result:")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Total items: {result['total_items']}")
        print(f"Retrieved items: {len(result['items'])}")
        if result['items']:
            print("\nFirst item metadata:")
            print(result['items'][0]['metadata']) 