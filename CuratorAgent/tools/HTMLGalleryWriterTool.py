from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import json
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class HTMLGalleryWriterTool(BaseTool):
    """
    Creates interactive HTML galleries for media clusters.
    Supports both images and videos with previews and metadata display.
    Uses responsive design for optimal viewing on various devices.
    """
    
    clusters: Dict[str, List[Dict[str, Any]]] = Field(
        ...,
        description="Dictionary of clusters with their items"
    )
    
    summaries: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Dictionary of cluster summaries"
    )
    
    output_dir: str = Field(
        default="gallery",
        description="Directory to save the HTML gallery"
    )
    
    title: str = Field(
        default="Media Gallery",
        description="Title for the gallery"
    )
    
    def _create_gallery_structure(self) -> Path:
        """Creates the gallery directory structure."""
        gallery_path = Path(self.output_dir)
        
        # Create directories
        (gallery_path / "css").mkdir(parents=True, exist_ok=True)
        (gallery_path / "js").mkdir(parents=True, exist_ok=True)
        (gallery_path / "media").mkdir(exist_ok=True)
        
        return gallery_path

    def _write_css(self, gallery_path: Path) -> None:
        """Writes the CSS file for the gallery."""
        css = """
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #34495e;
            --accent-color: #3498db;
            --text-color: #333;
            --background-color: #f5f6fa;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--background-color);
            color: var(--text-color);
        }

        .header {
            background-color: var(--primary-color);
            color: white;
            padding: 2rem;
            text-align: center;
        }

        .cluster-container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }

        .cluster {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            overflow: hidden;
        }

        .cluster-header {
            background-color: var(--secondary-color);
            color: white;
            padding: 1rem;
        }

        .cluster-summary {
            padding: 1rem;
            border-bottom: 1px solid #eee;
            font-style: italic;
        }

        .media-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1rem;
            padding: 1rem;
        }

        .media-item {
            position: relative;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }

        .media-item:hover {
            transform: scale(1.02);
        }

        .media-preview {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }

        .video-overlay {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 48px;
            height: 48px;
            background: rgba(0,0,0,0.7);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .media-info {
            padding: 0.5rem;
            background: rgba(255,255,255,0.9);
        }

        .media-info h4 {
            margin: 0;
            font-size: 0.9rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .media-info p {
            margin: 0.2rem 0;
            font-size: 0.8rem;
            color: #666;
        }

        @media (max-width: 768px) {
            .media-grid {
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            }
            
            .media-preview {
                height: 150px;
            }
        }
        """
        
        with open(gallery_path / "css" / "style.css", 'w') as f:
            f.write(css)

    def _write_javascript(self, gallery_path: Path) -> None:
        """Writes the JavaScript file for the gallery."""
        js = """
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize lightbox or video player
            const mediaItems = document.querySelectorAll('.media-item');
            
            mediaItems.forEach(item => {
                item.addEventListener('click', function() {
                    const mediaPath = this.dataset.path;
                    const mediaType = this.dataset.type;
                    
                    if (mediaType === 'video') {
                        // Open video in a new window/player
                        window.open(mediaPath, '_blank');
                    } else {
                        // Show image in a lightbox
                        const img = new Image();
                        img.src = mediaPath;
                        
                        const lightbox = document.createElement('div');
                        lightbox.style.position = 'fixed';
                        lightbox.style.top = '0';
                        lightbox.style.left = '0';
                        lightbox.style.width = '100%';
                        lightbox.style.height = '100%';
                        lightbox.style.backgroundColor = 'rgba(0,0,0,0.9)';
                        lightbox.style.display = 'flex';
                        lightbox.style.alignItems = 'center';
                        lightbox.style.justifyContent = 'center';
                        lightbox.style.zIndex = '1000';
                        
                        img.style.maxWidth = '90%';
                        img.style.maxHeight = '90%';
                        img.style.objectFit = 'contain';
                        
                        lightbox.appendChild(img);
                        document.body.appendChild(lightbox);
                        
                        lightbox.addEventListener('click', function() {
                            document.body.removeChild(lightbox);
                        });
                    }
                });
            });
        });
        """
        
        with open(gallery_path / "js" / "gallery.js", 'w') as f:
            f.write(js)

    def _create_html_template(self) -> str:
        """Creates the HTML template for the gallery."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ title }}</title>
            <link rel="stylesheet" href="css/style.css">
        </head>
        <body>
            <div class="header">
                <h1>{{ title }}</h1>
                <p>Generated on {{ generation_date }}</p>
            </div>
            
            <div class="cluster-container">
                {% for cluster_id, cluster in clusters.items() %}
                <div class="cluster">
                    <div class="cluster-header">
                        <h2>Cluster {{ cluster_id }}</h2>
                        <p>{{ summaries[cluster_id].item_count }} items</p>
                    </div>
                    
                    <div class="cluster-summary">
                        <p>{{ summaries[cluster_id].summary }}</p>
                    </div>
                    
                    <div class="media-grid">
                        {% for item in cluster %}
                        <div class="media-item" data-path="{{ item.metadata.file_path }}" data-type="{{ item.metadata.media_type }}">
                            <img class="media-preview" src="{{ item.metadata.file_path }}" alt="Media preview">
                            {% if item.metadata.media_type == 'video' %}
                            <div class="video-overlay">▶</div>
                            {% endif %}
                            <div class="media-info">
                                <h4>{{ item.metadata.file_path.split('/')[-1] }}</h4>
                                <p>Type: {{ item.metadata.media_type }}</p>
                                {% if item.metadata.creation_time %}
                                <p>Created: {{ item.metadata.creation_time }}</p>
                                {% endif %}
                                {% if item.metadata.media_type == 'video' and item.metadata.duration %}
                                <p>Duration: {{ item.metadata.duration }}</p>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <script src="js/gallery.js"></script>
        </body>
        </html>
        """

    def run(self) -> Dict[str, Any]:
        """
        Creates an interactive HTML gallery with the provided clusters and summaries.
        Returns the path to the generated gallery.
        """
        try:
            # Create gallery structure
            gallery_path = self._create_gallery_structure()
            
            # Write CSS and JavaScript
            self._write_css(gallery_path)
            self._write_javascript(gallery_path)
            
            # Create Jinja2 environment
            env = Environment(loader=FileSystemLoader(str(gallery_path)))
            template = env.from_string(self._create_html_template())
            
            # Render HTML
            html = template.render(
                title=self.title,
                clusters=self.clusters,
                summaries=self.summaries,
                generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Write HTML file
            with open(gallery_path / "index.html", 'w') as f:
                f.write(html)
            
            return {
                "status": "success",
                "gallery_path": str(gallery_path),
                "index_file": str(gallery_path / "index.html"),
                "statistics": {
                    "total_clusters": len(self.clusters),
                    "total_items": sum(len(items) for items in self.clusters.values())
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            } 