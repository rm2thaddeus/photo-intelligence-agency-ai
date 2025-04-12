from MediaManager.tools.FileSystemScanner import FileSystemScanner
from MediaManager.tools.VideoProcessor import VideoProcessor
import os
from pathlib import Path

# Set the video directory and output directory
video_dir = "H:\\Phone Videos"  # Updated directory path
test_output_dir = os.path.join(os.path.dirname(__file__), "outputs", "videos")

# Create output directory if it doesn't exist
os.makedirs(test_output_dir, exist_ok=True)

# Initialize FileSystemScanner with parameters
scanner = FileSystemScanner(
    directory_path=video_dir,
    file_types=[".mp4"],
    recursive=False
)

# Run the scanner
result = scanner.run()
print(f"\nFound videos: {result}")

# Process found videos
if result and isinstance(result, list):
    for video_path in result:
        if "VID_20240113_140945.mp4" in video_path:  # Updated video filename
            print(f"\nProcessing video: {video_path}")
            
            # Initialize VideoProcessor with the video path
            processor = VideoProcessor(
                video_path=video_path,
                output_dir=test_output_dir
            )
            
            # Process the video
            result = processor.run()
            print("\nProcessing Results:")
            print(result)
            break  # Stop after processing our test video
    else:
        print("\nTest video 'VID_20240113_140945.mp4' not found in the scanned directory")
else:
    print("No video files found or error in scanning") 