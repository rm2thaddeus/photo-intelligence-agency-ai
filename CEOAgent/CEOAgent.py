from agency_swarm import Agent
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class CEOAgent(Agent):
    """
    CEO Agent class responsible for managing user interactions and coordinating tasks
    between other agents in the Photo Intelligence Agency.
    """
    
    def __init__(self):
        super().__init__(
            name="CEO",
            description="Responsible for client communication, task planning and management.",
            instructions=str(Path(__file__).parent / "instructions.md"),
            tools_folder=str(Path(__file__).parent / "tools"),
            model='gpt-4o-mini',
            temperature=0.4,
            max_prompt_tokens=4000,
        )