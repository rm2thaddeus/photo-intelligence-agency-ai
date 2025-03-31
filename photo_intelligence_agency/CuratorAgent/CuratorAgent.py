from agency_swarm import Agent
from pathlib import Path

class CuratorAgent(Agent):
    """
    Curator Agent class responsible for organizing media content through clustering,
    generating summaries, and creating interactive HTML galleries.
    """
    
    def __init__(self):
        super().__init__(
            name="Curator",
            description="Fetches data from Qdrant, clusters media, generates summaries, and creates HTML galleries.",
            instructions=str(Path(__file__).parent / "instructions.md"),
            tools_folder=str(Path(__file__).parent / "tools"),
            temperature=0.4,  # Balanced temperature for creativity and consistency
            max_prompt_tokens=25000,
        ) 