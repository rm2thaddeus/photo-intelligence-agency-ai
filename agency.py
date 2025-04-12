from agency_swarm import Agency
from pathlib import Path

from CEOAgent.CEOAgent import CEOAgent
from MediaMinerAgent.MediaMinerAgent import MediaMinerAgent
from CuratorAgent.CuratorAgent import CuratorAgent

# Initialize agents with optimized temperatures
ceo = CEOAgent()  # Uses default temperature for decision making
miner = MediaMinerAgent()  # Lower temperature for precise operations
curator = CuratorAgent()  # Higher temperature for creative tasks

# Create agency with communication flows
agency = Agency(
    [
        ceo,  # CEO is the entry point for user communication
        [ceo, miner],  # CEO can communicate with MediaMiner
        [ceo, curator],  # CEO can communicate with Curator
        [miner, curator],  # MediaMiner can communicate with Curator
    ],
    shared_instructions=str(Path(__file__).parent / "agency_manifesto.md"),
    temperature=0.4,  # Default temperature for general communication
    max_prompt_tokens=4000,  # Reduced for cost efficiency while maintaining context
)

if __name__ == "__main__":
    agency.run_demo()  # Start the agency in terminal mode