from agency_swarm import Agent
from pathlib import Path

class CEOAgent(Agent):
    """
    CEO Agent class responsible for managing user interactions and coordinating tasks
    between other agents in the Photo Intelligence Agency.
    """
    
    def __init__(self):
        super().__init__(
            name="CEO",
            description="Human-in-the-loop controller. Manages user input, project settings, and delegates tasks.",
            instructions=str(Path(__file__).parent / "instructions.md"),
            tools_folder=str(Path(__file__).parent / "tools"),
            temperature=0.5,
            max_prompt_tokens=25000,
        )