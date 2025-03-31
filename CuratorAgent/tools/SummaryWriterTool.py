from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from pathlib import Path

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SummaryWriterTool(BaseTool):
    """
    Generates descriptive summaries for media clusters using OpenAI.
    Takes into account both image and video content, creating concise
    and meaningful descriptions for each cluster.
    """
    
    clusters: Dict[str, List[Dict[str, Any]]] = Field(
        ...,
        description="Dictionary of clusters with their items from ClusterTool"
    )
    
    output_dir: str = Field(
        default="summaries",
        description="Directory to save cluster summaries"
    )
    
    def _generate_cluster_summary(self, cluster_items: List[Dict[str, Any]], cluster_id: str) -> str:
        """Generate a summary for a cluster using OpenAI."""
        # Prepare cluster information for the prompt
        media_types = {}
        for item in cluster_items:
            media_type = item['metadata'].get('media_type', 'unknown')
            media_types[media_type] = media_types.get(media_type, 0) + 1
            
        # Create a detailed prompt
        prompt = f"""Analyze this media cluster and create a concise summary:

Cluster Statistics:
- Total items: {len(cluster_items)}
- Media types: {', '.join(f'{k}: {v}' for k, v in media_types.items())}

Key Metadata:
"""
        
        # Add sample metadata from a few items
        for item in cluster_items[:3]:
            metadata = item['metadata']
            prompt += f"- {metadata.get('file_path', 'Unknown path')}\n"
            if 'creation_time' in metadata:
                prompt += f"  Created: {metadata['creation_time']}\n"
            if metadata.get('media_type') == 'video' and 'duration' in metadata:
                prompt += f"  Duration: {metadata['duration']}\n"
                
        prompt += "\nPlease provide a concise summary (2-3 sentences) describing the content and characteristics of this cluster."
        
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a media curator assistant. Create concise, descriptive summaries of media clusters."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def run(self) -> Dict[str, Any]:
        """
        Generates summaries for all clusters and saves them.
        Returns dictionary with cluster summaries and statistics.
        """
        try:
            # Create output directory
            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate summaries for each cluster
            summaries = {}
            for cluster_id, items in self.clusters.items():
                summary = self._generate_cluster_summary(items, cluster_id)
                summaries[cluster_id] = {
                    "summary": summary,
                    "item_count": len(items),
                    "media_types": {}
                }
                
                # Count media types
                for item in items:
                    media_type = item['metadata'].get('media_type', 'unknown')
                    summaries[cluster_id]["media_types"][media_type] = \
                        summaries[cluster_id]["media_types"].get(media_type, 0) + 1
            
            # Save results
            results = {
                "summaries": summaries,
                "statistics": {
                    "total_clusters": len(summaries),
                    "total_items": sum(s["item_count"] for s in summaries.values())
                }
            }
            
            with open(output_path / "cluster_summaries.json", 'w') as f:
                json.dump(results, f, indent=2)
            
            # Store in shared state for other tools
            self._shared_state.set("cluster_summaries", results)
            
            return {
                "status": "success",
                "summaries": summaries,
                "statistics": results["statistics"],
                "output_file": str(output_path / "cluster_summaries.json")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

# Example test case
if __name__ == "__main__":
    # Create test clusters
    test_clusters = {
        "0": [
            {
                "id": "test_1",
                "metadata": {
                    "file_path": "/path/to/beach_1.jpg",
                    "media_type": "image",
                    "creation_time": "2024-01-01T12:00:00"
                }
            },
            {
                "id": "test_2",
                "metadata": {
                    "file_path": "/path/to/beach_2.mp4",
                    "media_type": "video",
                    "creation_time": "2024-01-01T13:00:00",
                    "duration": "00:02:30"
                }
            }
        ]
    }
    
    # Test the tool
    summary_tool = SummaryWriterTool(
        clusters=test_clusters,
        output_dir="test_summaries"
    )
    
    result = summary_tool.run()
    print("\nSummary Generation Result:")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Number of clusters summarized: {result['statistics']['total_clusters']}")
        print("\nFirst cluster summary:")
        print(result['summaries']['0']['summary']) 