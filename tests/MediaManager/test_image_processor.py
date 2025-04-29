import pytest
from MediaManager.tools.FileSystemScanner import FileSystemScanner
from MediaManager.tools.ImageProcessor import ImageProcessor
import os
from pathlib import Path

@pytest.fixture
def image_dir(tmp_path):
    # Use a temporary directory for test images
    return tmp_path

@pytest.fixture
def test_output_dir(tmp_path):
    # Use a temporary directory for outputs
    return tmp_path / "outputs" / "images"

def test_image_processing(image_dir, test_output_dir):
    # This test assumes there are images in image_dir; in CI, you would mock or generate them
    scanner = FileSystemScanner(
        directory_path=str(image_dir),
        file_types=[".jpg", ".jpeg", ".png"],
        recursive=False
    )
    result = scanner.run()
    assert isinstance(result, list)
    # If no images, skip processing
    if not result:
        pytest.skip("No image files found for processing.")
    processor = ImageProcessor(input_paths=result)
    process_result = processor.run()
    assert process_result is not None
    # Add more assertions as needed for your processing logic 