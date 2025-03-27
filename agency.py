from agency_swarm import Agency
from pathlib import Path

from CEOAgent.CEOAgent import CEOAgent
from MediaMinerAgent.MediaMinerAgent import MediaMinerAgent
from CuratorAgent.CuratorAgent import CuratorAgent

# Initialize agents
ceo = CEOAgent()
miner = MediaMinerAgent()
curator = CuratorAgent()

# Create agency with communication flows
agency = Agency(
    [
        ceo,  # CEO is the entry point for user communication
        [ceo, miner],  # CEO can communicate with MediaMiner
        [ceo, curator],  # CEO can communicate with Curator
        [miner, curator],  # MediaMiner can communicate with Curator
    ],
    shared_instructions=str(Path(__file__).parent / "agency_manifesto.md"),
    temperature=0.5,
    max_prompt_tokens=25000,
)

if __name__ == "__main__":
    agency.run_demo()  # Start the agency in terminal mode