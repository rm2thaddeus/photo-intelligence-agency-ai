from unittest.mock import MagicMock
from typing import Any, Dict, Optional, List
import json
from pathlib import Path

class SharedState:
    def __init__(self):
        self._state = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        self._state[key] = value

class MockBaseTool:
    def __init__(self, **kwargs):
        self._shared_state = SharedState()
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def run(self) -> Dict[str, Any]:
        raise NotImplementedError

class MockAgent:
    def __init__(self, name=None, description=None, instructions=None, tools_folder=None, model=None, temperature=None, max_prompt_tokens=None):
        self.name = name
        self.description = description
        self.instructions = instructions
        self.tools_folder = tools_folder
        self.model = model
        self.temperature = temperature
        self.max_prompt_tokens = max_prompt_tokens

class MockFilter:
    def __init__(self, must=None):
        self.must = must or []

class MockFieldCondition:
    def __init__(self, key=None, match=None, range=None):
        self.key = key
        self.match = match
        self.range = range

class MockMatchValue:
    def __init__(self, value=None):
        self.value = value

class MockRange:
    def __init__(self, gte=None, lte=None):
        self.gte = gte
        self.lte = lte

class MockPoint:
    def __init__(self, id: str, vector: List[float], payload: Dict[str, Any]):
        self.id = id
        self.vector = vector
        self.payload = payload

class MockCollectionInfo:
    def __init__(self, points_count: int):
        self.points_count = points_count

class MockQdrantClient:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.host = host
        self.port = port
        self._mock = MagicMock()
    
    def get_collection(self, collection_name: str) -> MockCollectionInfo:
        if hasattr(self._mock.get_collection, 'side_effect'):
            raise self._mock.get_collection.side_effect
        return MockCollectionInfo(points_count=100)
    
    def scroll(
        self,
        collection_name: str,
        limit: int = 10,
        offset: int = 0,
        with_payload: bool = True,
        with_vectors: bool = True,
        filter: Optional[MockFilter] = None
    ) -> tuple[List[MockPoint], Optional[str]]:
        if hasattr(self._mock.scroll, 'side_effect'):
            raise self._mock.scroll.side_effect
        
        point = MockPoint(
            id="test_1",
            vector=[0.1] * 512,
            payload={
                "file_path": "/path/to/test.jpg",
                "media_type": "image",
                "file_creation_time": "2024-01-01T00:00:00"
            }
        )
        return [point], None
    
    def __getattr__(self, name):
        return getattr(self._mock, name)

class MockOpenAIClient:
    def __init__(self, api_key: str = None):
        self._mock = MagicMock()
        self.chat = MagicMock()
        self.chat.completions = MagicMock()
        self.chat.completions.create = MagicMock()
    
    def __getattr__(self, name):
        return getattr(self._mock, name)

# Mock the agency_swarm module
class MockAgencySwarm:
    class tools:
        BaseTool = MockBaseTool
    
    Agent = MockAgent

# Mock the qdrant_client.http.models module
class MockQdrantModels:
    Filter = MockFilter
    FieldCondition = MockFieldCondition
    MatchValue = MockMatchValue
    Range = MockRange

# Create mocks for the packages
import sys
sys.modules['agency_swarm'] = MockAgencySwarm
sys.modules['agency_swarm.tools'] = MockAgencySwarm.tools
sys.modules['qdrant_client'] = type('MockQdrantClientModule', (), {'QdrantClient': MockQdrantClient})
sys.modules['qdrant_client.http.models'] = MockQdrantModels
sys.modules['openai'] = type('MockOpenAIModule', (), {'OpenAI': MockOpenAIClient}) 