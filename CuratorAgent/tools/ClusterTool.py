from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import List, Dict, Any, Optional
import numpy as np
import hdbscan
from sklearn.preprocessing import normalize
import json
from pathlib import Path

class ClusterTool(BaseTool):
    """
    Performs HDBSCAN clustering on CLIP embeddings to group similar media items.
    Handles both image and video embeddings, storing results for further processing.
    """
    
    items: List[Dict[str, Any]] = Field(
        ...,
        description="List of media items with embeddings and metadata from QdrantFetcherTool"
    )
    
    min_cluster_size: int = Field(
        default=5,
        description="Minimum number of items to form a cluster"
    )
    
    min_samples: int = Field(
        default=3,
        description="Number of samples in a neighborhood for a point to be considered a core point"
    )
    
    output_dir: str = Field(
        default="clusters",
        description="Directory to save clustering results"
    )

    def _prepare_embeddings(self) -> np.ndarray:
        """Prepare embeddings for clustering."""
        embeddings = []
        for item in self.items:
            if isinstance(item['embedding'], list):
                embeddings.append(item['embedding'])
            else:
                embeddings.append(json.loads(item['embedding']))
        
        # Convert to numpy array and normalize
        embeddings_array = np.array(embeddings)
        return normalize(embeddings_array)

    def run(self) -> Dict[str, Any]:
        """
        Performs clustering on the provided embeddings and saves results.
        Returns cluster assignments and statistics.
        """
        try:
            # Prepare embeddings
            embeddings = self._prepare_embeddings()
            
            # Perform clustering
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=self.min_cluster_size,
                min_samples=self.min_samples,
                metric='euclidean'
            )
            
            cluster_labels = clusterer.fit_predict(embeddings)
            
            # Prepare results
            clusters = {}
            noise_points = []
            
            for idx, (label, item) in enumerate(zip(cluster_labels, self.items)):
                if label == -1:
                    noise_points.append({
                        "id": item['id'],
                        "metadata": item['metadata']
                    })
                else:
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append({
                        "id": item['id'],
                        "metadata": item['metadata']
                    })
            
            # Create output directory
            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save results
            results = {
                "clusters": clusters,
                "noise_points": noise_points,
                "statistics": {
                    "total_items": len(self.items),
                    "num_clusters": len(clusters),
                    "noise_points": len(noise_points)
                }
            }
            
            with open(output_path / "clustering_results.json", 'w') as f:
                json.dump(results, f, indent=2)
            
            # Store in shared state for other tools
            self._shared_state.set("clustering_results", results)
            
            return {
                "status": "success",
                "clusters": clusters,
                "noise_points": noise_points,
                "statistics": results["statistics"],
                "output_file": str(output_path / "clustering_results.json")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

# Example test case
if __name__ == "__main__":
    # Create test data
    test_items = [
        {
            "id": f"test_{i}",
            "embedding": np.random.rand(512).tolist(),  # Simulating CLIP embeddings
            "metadata": {
                "file_path": f"/path/to/file_{i}",
                "media_type": "image"
            }
        }
        for i in range(20)
    ]
    
    # Test the tool
    cluster_tool = ClusterTool(
        items=test_items,
        min_cluster_size=3,
        min_samples=2,
        output_dir="test_clusters"
    )
    
    result = cluster_tool.run()
    print("\nClustering Result:")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Number of clusters: {result['statistics']['num_clusters']}")
        print(f"Number of noise points: {result['statistics']['noise_points']}")
        print(f"Results saved to: {result['output_file']}") 