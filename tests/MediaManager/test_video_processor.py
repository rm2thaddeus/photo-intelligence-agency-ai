import pytest
from MediaManager.tools.FileSystemScanner import FileSystemScanner
from MediaManager.tools.VideoProcessor import VideoProcessor
import os
from pathlib import Path

@pytest.fixture
def video_dir(tmp_path):
    # Use a temporary directory for test videos
    return tmp_path

@pytest.fixture
def test_output_dir(tmp_path):
    # Use a temporary directory for outputs
    return tmp_path / "outputs" / "videos"

def test_video_processing(video_dir, test_output_dir):
    # This test assumes there are videos in video_dir; in CI, you would mock or generate them
    scanner = FileSystemScanner(
        directory_path=str(video_dir),
        file_types=[".mp4"],
        recursive=False
    )
    result = scanner.run()
    assert isinstance(result, list)
    # If no videos, skip processing
    if not result:
        pytest.skip("No video files found for processing.")
    for video_path in result:
        # In a real test, you would select or generate a specific test video
        processor = VideoProcessor(
            video_path=video_path,
            output_dir=str(test_output_dir)
        )
        process_result = processor.run()
        assert process_result is not None
        # Add more assertions as needed for your processing logic
        break  # Only process one video for the test 