# 📌 Purpose: Processes a single video file: extracts metadata, detects scenes, generates representative embeddings using CLIP (leveraging CUDA), and stores data in Qdrant for efficient retrieval.
# 🔄 Latest Changes: Enhanced scene detection, improved frame storage, added output directory structure
# ⚙️ Key Logic: Uses ffmpeg-python for metadata/frame extraction, scenedetect for scene boundaries, CLIP for embeddings (CUDA), and Qdrant for searchable storage
# 📂 Expected File Path: photo_intelligence_agency/MediaManager/tools/VideoProcessor.py
# 🧠 Reasoning: Centralizes video processing with efficient storage/retrieval via Qdrant

import os
import json
import shutil
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import ffmpeg
from PIL import Image
import torch
from pydantic import Field, validator
from agency_swarm.tools import BaseTool
from qdrant_client.http.models import PointStruct

try:
    from scenedetect import detect, ContentDetector, SceneManager, open_video
    SCENEDETECT_AVAILABLE = True
except ImportError:
    SCENEDETECT_AVAILABLE = False

# Import shared resources
from .processing_utils import (
    logger,
    qdrant_client,
    processor,
    model,
    DEVICE,
    EMBEDDING_DIM,
    QDRANT_COLLECTION_NAME
)

# Constants
SCENE_DETECTION_THRESHOLD = 27.0  # Default threshold for content-aware scene detection

class SceneInfo:
    """Data class for scene information"""
    def __init__(self, scene_number: int, start_time_sec: float, end_time_sec: float, duration_sec: float):
        self.scene_number = scene_number
        self.start_time_sec = start_time_sec
        self.end_time_sec = end_time_sec
        self.duration_sec = duration_sec
        
    def dict(self):
        return {
            'scene_number': self.scene_number,
            'start_time_sec': self.start_time_sec,
            'end_time_sec': self.end_time_sec,
            'duration_sec': self.duration_sec
        }

class VideoMetadata:
    """Data class for video metadata"""
    def __init__(self, **kwargs):
        self.filename: str = kwargs.get('filename', '')
        self.file_path: str = kwargs.get('file_path', '')
        self.file_size_bytes: int = kwargs.get('file_size_bytes', 0)
        self.duration_seconds: float = kwargs.get('duration_seconds', 0.0)
        self.width: int = kwargs.get('width', 0)
        self.height: int = kwargs.get('height', 0)
        self.fps: float = kwargs.get('fps', 0.0)
        self.codec_name: str = kwargs.get('codec_name', '')
        self.bitrate: int = kwargs.get('bitrate', 0)
        self.scenes: List[SceneInfo] = kwargs.get('scenes', [])
        self.creation_time: datetime = kwargs.get('creation_time')
        self.modification_time: datetime = kwargs.get('modification_time')
        
    def dict(self, exclude_none: bool = True):
        data = {
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size_bytes': self.file_size_bytes,
            'duration_seconds': self.duration_seconds,
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'codec_name': self.codec_name,
            'bitrate': self.bitrate,
            'scenes': [scene.dict() for scene in self.scenes] if self.scenes else [],
            'creation_time': self.creation_time.isoformat() if self.creation_time else None,
            'modification_time': self.modification_time.isoformat() if self.modification_time else None
        }
        if exclude_none:
            return {k: v for k, v in data.items() if v is not None}
        return data

class VideoProcessor(BaseTool):
    """
    Processes a single video file: extracts metadata using FFmpeg, detects scenes
    using PySceneDetect, generates CLIP embeddings (using CUDA) for each scene.
    Creates a structured output directory containing frames, metadata, and scene information.
    Requires FFmpeg and CUDA-enabled environment.
    """
    video_path: str = Field(
        ...,
        description="The absolute path to the video file to be processed."
    )
    output_dir: Optional[str] = Field(
        None,
        description="Directory to store output files (frames, metadata, etc.). If None, creates one based on video name."
    )
    scene_detection_threshold: float = Field(
        SCENE_DETECTION_THRESHOLD,
        description="Threshold for PySceneDetect's ContentDetector (lower means more sensitive)."
    )
    save_frames: bool = Field(
        True,
        description="Whether to save extracted frames to disk."
    )

    @validator('output_dir', pre=True, always=True)
    def setup_output_dir(cls, v, values):
        if v is None and 'video_path' in values:
            video_path = Path(values['video_path'])
            v = str(video_path.parent / f"{video_path.stem}_output")
        if isinstance(v, (str, Path)):
            v = str(v)  # Convert Path to string
            os.makedirs(v, exist_ok=True)
            os.makedirs(os.path.join(v, "frames"), exist_ok=True)
            os.makedirs(os.path.join(v, "metadata"), exist_ok=True)
        return v

    def _extract_metadata(self, vid_path: Path) -> Optional[VideoMetadata]:
        """Extracts comprehensive metadata using FFmpeg."""
        try:
            probe = ffmpeg.probe(str(vid_path))
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            # Calculate duration
            duration = float(probe['format'].get('duration', 0))
            
            # Get file stats
            file_stats = vid_path.stat()
            
            return VideoMetadata(
                filename=vid_path.name,
                file_path=str(vid_path.resolve()),
                file_size_bytes=file_stats.st_size,
                duration_seconds=duration,
                width=int(video_info.get('width', 0)),
                height=int(video_info.get('height', 0)),
                fps=eval(video_info.get('r_frame_rate', '0/1')),
                codec_name=video_info.get('codec_name', ''),
                bitrate=int(probe['format'].get('bit_rate', 0)),
                creation_time=datetime.fromtimestamp(file_stats.st_ctime),
                modification_time=datetime.fromtimestamp(file_stats.st_mtime)
            )
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return None

    def _detect_scenes(self, vid_path: Path) -> Optional[Tuple[List[SceneInfo], List[Tuple[float, Path]]]]:
        """Detects scenes using PySceneDetect and saves representative frames."""
        if not SCENEDETECT_AVAILABLE:
            logger.warning("Scene detection skipped as PySceneDetect is not available.")
            return None, None

        scene_list_info = []
        scene_frame_paths = []
        frames_dir = os.path.join(self.output_dir, "frames") if self.save_frames else tempfile.mkdtemp(prefix="scene_frames_")
        
        try:
            logger.info(f"Detecting scenes for {vid_path.name}...")
            video = open_video(str(vid_path))
            scene_manager = SceneManager()
            scene_manager.add_detector(ContentDetector(threshold=self.scene_detection_threshold))
            scene_manager.detect_scenes(video=video, show_progress=True)
            scene_list_tuples = scene_manager.get_scene_list()

            if not scene_list_tuples:
                logger.info(f"No scenes detected for {vid_path.name} (or only one scene).")
                middle_time_sec = video.duration.get_seconds() / 2
                scene_list_tuples = [(video.base_timecode, video.duration)]
            else:
                logger.info(f"Detected {len(scene_list_tuples)} scenes for {vid_path.name}.")

            for i, (start, end) in enumerate(scene_list_tuples):
                scene_num = i + 1
                start_sec = start.get_seconds()
                end_sec = end.get_seconds()
                duration_sec = end_sec - start_sec

                scene_list_info.append(SceneInfo(
                    scene_number=scene_num,
                    start_time_sec=start_sec,
                    end_time_sec=end_sec,
                    duration_sec=duration_sec
                ))

                # Extract multiple frames per scene for better representation
                frame_times = [
                    start_sec + (duration_sec * j / 4) for j in range(1, 4)  # 3 frames per scene
                ]
                
                for frame_idx, frame_time in enumerate(frame_times):
                    frame_path = os.path.join(frames_dir, f"scene_{scene_num:04d}_frame_{frame_idx:02d}.jpg")
                    try:
                        (
                            ffmpeg
                            .input(str(vid_path), ss=frame_time)
                            .output(str(frame_path), vframes=1, format='image2', vcodec='mjpeg', q=2)
                            .overwrite_output()
                            .run(capture_stdout=True, capture_stderr=True)
                        )
                        if os.path.exists(frame_path):
                            scene_frame_paths.append((frame_time, Path(frame_path)))
                            logger.debug(f"Saved frame {frame_idx} for scene {scene_num} at {frame_time:.2f}s")
                        else:
                            logger.warning(f"Failed to save frame {frame_idx} for scene {scene_num}")
                    except Exception as e:
                        logger.warning(f"Error saving frame {frame_idx} for scene {scene_num}: {e}")

            if not scene_frame_paths:
                logger.warning("Could not extract any frames. Scene detection failed.")
                return scene_list_info, None

            return scene_list_info, scene_frame_paths

        except Exception as e:
            logger.error(f"Failed during scene detection: {e}", exc_info=True)
            if not self.save_frames and os.path.exists(frames_dir):
                shutil.rmtree(frames_dir)
            return None, None

    def _generate_embedding_from_frames(self, frame_paths: List[Path]) -> Optional[List[float]]:
        """Generate a single embedding from multiple frames using CLIP."""
        if not model or not processor:
            logger.error("CLIP model/processor not initialized")
            return None
            
        try:
            # Load and preprocess all frames
            processed_frames = []
            for frame_path in frame_paths:
                try:
                    img = Image.open(frame_path)
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    inputs = processor(images=img, return_tensors="pt", padding=True)
                    processed_frames.append(inputs)
                except Exception as e:
                    logger.warning(f"Error processing frame {frame_path}: {e}")
                    continue
                    
            if not processed_frames:
                return None
                
            # Combine all preprocessed frames
            batch_inputs = {
                k: torch.cat([frame[k] for frame in processed_frames]).to(DEVICE)
                for k in processed_frames[0].keys()
            }
            
            # Generate embeddings
            with torch.no_grad():
                outputs = model.get_image_features(**batch_inputs)
            embeddings = outputs.cpu().numpy()
            
            # Average all frame embeddings
            avg_embedding = embeddings.mean(axis=0)
            return avg_embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return None

    def _upsert_to_qdrant(self, metadata: VideoMetadata, embedding: List[float]) -> bool:
        """Upsert processed video data (metadata + embedding) to Qdrant."""
        if not qdrant_client:
            logger.error("Qdrant client not initialized")
            return False
        if embedding is None:
            logger.error(f"Cannot upsert {metadata.filename}, embedding is None.")
            return False

        try:
            point = PointStruct(
                id=str(metadata.file_path), # Use file path as unique ID
                vector=embedding,
                payload={
                    **metadata.dict(), # Include all metadata
                    'media_type': 'video'
                }
            )
            
            qdrant_client.upsert(
                collection_name=QDRANT_COLLECTION_NAME,
                points=[point],
                wait=True
            )
            logger.info(f"Successfully upserted video data for {metadata.filename} to Qdrant.")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting video data for {metadata.filename} to Qdrant: {e}")
            return False

    def run(self) -> Dict[str, Any]:
        """
        Processes the video: extracts metadata, detects scenes, generates embedding,
        stores in Qdrant, and returns a status summary.
        """
        vid_path = Path(self.video_path)
        if not vid_path.is_file():
            return {"status": "error", "message": f"Video file not found: {self.video_path}"}
            
        logger.info(f"Starting processing for video: {vid_path.name}")

        # 1. Extract Metadata
        metadata = self._extract_metadata(vid_path)
        if not metadata:
            return {"status": "error", "message": f"Failed to extract metadata for {vid_path.name}"}

        # 2. Detect Scenes and Extract Frames
        scene_info_list, frame_data = self._detect_scenes(vid_path)
        if scene_info_list is not None:
            metadata.scenes = scene_info_list # Add scene info to metadata
        
        frames_to_process = [fp for _, fp in frame_data] if frame_data else []
        temp_frames_dir = None
        if not self.save_frames and frame_data: # If frames were saved temporarily
            # Extract the temporary directory path from one of the frame paths
            if frames_to_process:
                 temp_frames_dir = frames_to_process[0].parent

        if not frames_to_process:
            logger.warning(f"No frames extracted for {vid_path.name}, cannot generate embedding.")
            # Still try to save metadata without embedding if scene detection failed?
            # For now, let's return an error if no embedding can be made.
            if temp_frames_dir and os.path.exists(temp_frames_dir):
                shutil.rmtree(temp_frames_dir)
            return {"status": "error", "message": f"No frames extracted for {vid_path.name}, cannot generate embedding."}

        # 3. Generate Embedding
        logger.info(f"Generating embedding from {len(frames_to_process)} frames for {vid_path.name}...")
        embedding = self._generate_embedding_from_frames(frames_to_process)

        # Clean up temporary frames if they were created
        if temp_frames_dir and os.path.exists(temp_frames_dir):
            shutil.rmtree(temp_frames_dir)
            logger.info(f"Cleaned up temporary frames directory: {temp_frames_dir}")

        if not embedding:
            return {"status": "error", "message": f"Failed to generate embedding for {vid_path.name}"}
        
        # 4. Save Metadata Locally (Optional but good practice)
        metadata_file = Path(self.output_dir) / "metadata" / f"{vid_path.stem}_metadata.json"
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata.dict(), f, indent=4)
            logger.info(f"Saved metadata to {metadata_file}")
        except Exception as e:
             logger.warning(f"Could not save metadata JSON to {metadata_file}: {e}")

        # 5. Upsert to Qdrant
        upsert_success = self._upsert_to_qdrant(metadata, embedding)

        if upsert_success:
            return {
                "status": "success",
                "message": f"Successfully processed and stored video {vid_path.name}",
                "output_directory": self.output_dir,
                "qdrant_id": str(metadata.file_path)
            }
        else:
             return {
                "status": "error",
                "message": f"Processed video {vid_path.name}, but failed to store in Qdrant.",
                "output_directory": self.output_dir
            }

# Example Test Case
if __name__ == "__main__":
    # NOTE: Requires ffmpeg, ffprobe, PySceneDetect (optional), CLIP model, Qdrant
    print("VideoProcessor Test Case")
    
    # Ensure shared resources are available
    if not model or not processor or not qdrant_client:
        print("ERROR: CLIP model/processor or Qdrant client not initialized.")
        exit()
    if not SCENEDETECT_AVAILABLE:
         print("WARNING: PySceneDetect not installed, scene detection will be skipped.")
         
    # Create a dummy video file for testing (requires ffmpeg installed)
    temp_dir = Path("./temp_video_test_integration")
    temp_dir.mkdir(exist_ok=True)
    dummy_video_path = temp_dir / "dummy_video.mp4"
    output_dir = temp_dir / "dummy_video_output"
    
    try:
        # Generate a short black video with ffmpeg
        ffmpeg.input('color=c=black:s=64x64:r=1', f='lavfi', t=5).output(str(dummy_video_path), vcodec='libx264').overwrite_output().run(capture_stdout=True, capture_stderr=True)
        print(f"Created dummy video: {dummy_video_path.resolve()}")
    except Exception as e:
        print(f"Error creating dummy video (ffmpeg might be missing or misconfigured): {e}")
        if temp_dir.exists():
             shutil.rmtree(temp_dir)
        exit()

    # Instantiate and run the tool
    processor_tool = VideoProcessor(
        video_path=str(dummy_video_path.resolve()), 
        output_dir=str(output_dir.resolve()), 
        save_frames=False # Don't save frames in test by default
    )
    print("\n--- Running VideoProcessor Tool ---")
    result = processor_tool.run()
    print("\n--- Result ---")
    print(json.dumps(result, indent=2))
    
    # Verification (Optional)
    if result.get('status') == 'success' and result.get('qdrant_id'):
        try:
            fetch_result = qdrant_client.retrieve(
                collection_name=QDRANT_COLLECTION_NAME,
                ids=[result['qdrant_id']]
            )
            if fetch_result:
                print(f"\nVerification: Successfully retrieved point for {result['qdrant_id']} from Qdrant.")
            else:
                print(f"\nVerification WARNING: Could not retrieve point for {result['qdrant_id']} from Qdrant.")
        except Exception as e:
            print(f"\nVerification ERROR: Could not query Qdrant - {e}")

    # Cleanup
    print("\n--- Cleaning up ---")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print(f"Removed test directory: {temp_dir.resolve()}")