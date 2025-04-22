from agency_swarm import Agency
from pathlib import Path

from CEOAgent.CEOAgent import CEOAgent
# Remove CuratorAgent import if no longer used directly in the agency chart
# from CuratorAgent.CuratorAgent import CuratorAgent 
from MediaManager.MediaManager import MediaManager

# Initialize agents
ceo = CEOAgent()
# curator = CuratorAgent() # Remove instantiation if not used
media_manager = MediaManager()

# Create agency with updated communication flows
agency = Agency(
    [
        ceo,  # CEO is the entry point
        [ceo, media_manager],  # CEO can communicate with MediaManager
        # Add other flows if needed, e.g., [media_manager, curator] if MediaManager needs Curator
    ],
    shared_instructions=str(Path(__file__).parent / "agency_manifesto.md"),
    temperature=0.4,  
    max_prompt_tokens=4000, 
)

if __name__ == "__main__":
    # Launch Gradio UI with specified height
    agency.demo_gradio(height=900)