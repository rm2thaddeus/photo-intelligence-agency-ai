from agency_swarm import Agent
from pathlib import Path

class MediaManager(Agent):
    """
    MediaManager Agent class responsible for processing media files, extracting metadata,
    generating embeddings, and storing data in the Qdrant vector database.
    """
    
    def __init__(self):
        super().__init__(
            name="MediaManager",
            description="Scans media files, extracts metadata, generates embeddings, and stores them in Qdrant.",
            instructions=str(Path(__file__).parent / "instructions.md"),
            tools_folder=str(Path(__file__).parent / "tools"),
            # Removed explicit tools list to use only tools_folder which is more compatible with version 0.4.2
            model='gpt-4.1-nano',
            temperature=0.3,  # Lower temperature for more deterministic behavior
            max_prompt_tokens=25000,
        ) 