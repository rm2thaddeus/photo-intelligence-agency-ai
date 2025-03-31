# 📌 Purpose: Processes a single video file: extracts metadata, detects scenes, generates representative embeddings using CLIP (leveraging CUDA), and stores data in Qdrant for efficient retrieval.
# 🔄 Latest Changes: Enhanced scene detection, improved frame storage, added output directory structure
# ⚙️ Key Logic: Uses ffmpeg-python for metadata/frame extraction, scenedetect for scene boundaries, CLIP for embeddings (CUDA), and Qdrant for searchable storage
# 📂 Expected File Path: photo_intelligence_agency/MediaManager/tools/VideoProcessor.py
# 🧠 Reasoning: Centralizes video processing with efficient storage/retrieval via Qdrant

// ... existing code ...

class VideoProcessor(BaseTool):
    """
    Processes a single video file: extracts metadata using FFmpeg, detects scenes
    using PySceneDetect, generates CLIP embeddings (using CUDA) for each scene,
    and stores everything in Qdrant for efficient retrieval. Creates a structured
    output directory containing frames, metadata, and scene information.
    Requires FFmpeg and CUDA-enabled environment.
    """
    video_path: FilePath = Field(
        ...,
        description="The absolute path to the video file to be processed."
    )
    output_dir: Optional[Path] = Field(
        None,
        description="Directory to store output files (frames, metadata, etc.). If None, creates one based on video name."
    )
    scene_detection_threshold: float = Field(
        SCENE_DETECTION_THRESHOLD,
        description="Threshold for PySceneDetect's ContentDetector (lower means more sensitive)."
    )
    save_frames: bool = Field(
        True,
        description="Whether to save extracted frames to disk in addition to Qdrant storage."
    )

    @validator('output_dir', pre=True, always=True)
    def setup_output_dir(cls, v, values):
        if v is None and 'video_path' in values:
            video_path = Path(values['video_path'])
            v = video_path.parent / f"{video_path.stem}_output"
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        # Create subdirectories
        (v / "frames").mkdir(exist_ok=True)
        (v / "metadata").mkdir(exist_ok=True)
        return v

// ... existing code ...

    def _detect_scenes(self, vid_path: Path) -> Optional[Tuple[List[SceneInfo], List[Tuple[float, Path]]]]:
        """Detects scenes using PySceneDetect and saves representative frames."""
        if not SCENEDETECT_AVAILABLE:
            logger.warning("Scene detection skipped as PySceneDetect is not available.")
            return None, None

        scene_list_info = []
        scene_frame_paths = []
        frames_dir = self.output_dir / "frames" if self.save_frames else Path(tempfile.mkdtemp(prefix="scene_frames_"))
        
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
                    frame_path = frames_dir / f"scene_{scene_num:04d}_frame_{frame_idx:02d}.jpg"
                    try:
                        (
                            ffmpeg
                            .input(str(vid_path), ss=frame_time)
                            .output(str(frame_path), vframes=1, format='image2', vcodec='mjpeg', q=2)
                            .overwrite_output()
                            .run(capture_stdout=True, capture_stderr=True)
                        )
                        if frame_path.exists():
                            scene_frame_paths.append((frame_time, frame_path))
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
            if not self.save_frames and frames_dir.exists():
                shutil.rmtree(frames_dir)
            return None, None

// ... existing code ...

    def run(self) -> Dict[str, Any]:
        """
        Executes the video processing pipeline: metadata extraction, scene detection,
        frame extraction, embedding generation, and Qdrant storage. Creates a structured
        output directory with all extracted data.
        """
        vid_path = Path(self.video_path)
        logger.info(f"Processing video: {vid_path.name}")
        temp_dir_scenes = None

        try:
            # Extract metadata
            metadata = self._extract_metadata(vid_path)
            if not metadata:
                return {"status": "error", "message": "Failed to extract metadata", "file_path": str(vid_path)}

            # Save metadata to JSON
            metadata_file = self.output_dir / "metadata" / "video_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata.dict(exclude_none=True), f, indent=2)

            # Detect scenes and extract frames
            scene_info_list, scene_frames_data = self._detect_scenes(vid_path)
            if scene_info_list:
                metadata.scenes = scene_info_list

            # Save scene information
            if scene_info_list:
                scenes_file = self.output_dir / "metadata" / "scenes.json"
                with open(scenes_file, 'w') as f:
                    json.dump([scene.dict() for scene in scene_info_list], f, indent=2)

            frame_paths_to_embed = []
            if scene_frames_data:
                frame_paths_to_embed = [fp for _, fp in scene_frames_data]
                if not self.save_frames:
                    temp_dir_scenes = frame_paths_to_embed[0].parent
            else:
                return {"status": "error", "message": "No frames extracted", "file_path": str(vid_path)}

            # Generate embeddings
            embedding = self._generate_embedding_from_frames(frame_paths_to_embed)
            if not embedding:
                return {"status": "error", "message": "Failed to generate embedding", "file_path": str(vid_path)}

            if len(embedding) != EMBEDDING_DIM and model is not None:
                return {"status": "error", "message": f"Embedding dimension mismatch", "file_path": str(vid_path)}

            # Store in Qdrant
            upsert_success = self._upsert_to_qdrant(metadata, embedding)
            if not upsert_success:
                return {"status": "error", "message": "Failed to store in Qdrant", "file_path": str(vid_path)}

            logger.info(f"Successfully processed video: {vid_path.name}")
            return {
                "status": "success",
                "message": "Video processed and data stored",
                "file_path": str(vid_path),
                "output_dir": str(self.output_dir),
                "metadata_file": str(metadata_file),
                "num_scenes": len(scene_info_list) if scene_info_list else 0,
                "num_frames": len(frame_paths_to_embed)
            }

        finally:
            if not self.save_frames and temp_dir_scenes and temp_dir_scenes.exists():
                try:
                    shutil.rmtree(temp_dir_scenes)
                    logger.info(f"Cleaned up temporary directory: {temp_dir_scenes}")
                except Exception as cleanup_err:
                    logger.error(f"Error cleaning up temporary directory: {cleanup_err}")

// ... existing code ...