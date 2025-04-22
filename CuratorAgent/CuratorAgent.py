from agency_swarm import Agent
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class CuratorAgent(Agent):
    """
    Curator Agent class responsible for organizing and analyzing both image and video content through 
    advanced clustering, semantic analysis, and interactive gallery generation. Handles both images 
    and videos with their specific metadata, CLIP embeddings, and presentation requirements.
    """
    
    def __init__(self):
        super().__init__(
            name="Curator",
            description="Responsible for organizing and managing media content.",
            instructions=str(Path(__file__).parent / "instructions.md"),
            tools_folder=str(Path(__file__).parent / "tools"),
            model='gpt-4.1-nano',
            temperature=0.4,
            max_prompt_tokens=4000,
        ) 