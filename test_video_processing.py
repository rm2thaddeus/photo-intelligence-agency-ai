from MediaManager.tools.FileSystemScanner import FileSystemScanner
from MediaManager.tools.VideoProcessor import VideoProcessor
import os
from pathlib import Path

# Set the video directory
video_dir = "C:\\Users\\aitor\\Downloads"

# Initialize FileSystemScanner with parameters
scanner = FileSystemScanner(
    directory_path=video_dir,
    file_types=[".mp4"],
    recursive=False
)

# Run the scanner
result = scanner.run()
print(f"Found videos: {result}")

# Process the first video found
if result and isinstance(result, list):
    video_path = result[0]
    output_dir = str(Path(video_path).parent / "video_output")
    
    # Initialize VideoProcessor
    processor = VideoProcessor(
        video_path=video_path,
        output_dir=output_dir,
        save_frames=True
    )
    
    # Process the video
    result = processor.run()
    print("\nVideo Processing Result:")
    print(result)
else:
    print("No video files found or error in scanning") 