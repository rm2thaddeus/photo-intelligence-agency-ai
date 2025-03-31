from agency_swarm import Agent
from pathlib import Path

class CuratorAgent(Agent):
    """
    Curator Agent class responsible for organizing and analyzing both image and video content through 
    advanced clustering, semantic analysis, and interactive gallery generation. Handles both images 
    and videos with their specific metadata, CLIP embeddings, and presentation requirements.
    """
    
    def __init__(self):
        super().__init__(
            name="Curator",
            description=(
                "Advanced media curator that processes both images and videos. "
                "Fetches data from Qdrant, performs semantic clustering, generates "
                "content-aware summaries, and creates rich HTML galleries with "
                "video previews and detailed metadata display."
            ),
            instructions=str(Path(__file__).parent / "instructions.md"),
            tools_folder=str(Path(__file__).parent / "tools"),
            temperature=0.4,  # Balanced temperature for creativity and consistency
            max_prompt_tokens=25000,
        ) 