from MediaManager.tools.FileSystemScanner import FileSystemScanner
from MediaManager.tools.ImageProcessor import ImageProcessor
import os
from pathlib import Path

# Set the image directory and output directory
image_dir = "C:\\Users\\aitor\\OneDrive\\Escritorio\\test images"
test_output_dir = os.path.join(os.path.dirname(__file__), "outputs", "images")

# Initialize FileSystemScanner with parameters
scanner = FileSystemScanner(
    directory_path=image_dir,
    file_types=[".jpg", ".jpeg", ".png"],
    recursive=False
)

# Run the scanner
result = scanner.run()
print(f"Found images: {result}")

# Process all found images
if result and isinstance(result, list):
    # Initialize ImageProcessor with all found images
    processor = ImageProcessor(input_paths=result)
    
    # Process all images
    result = processor.run()
    print("\nProcessing Results:")
    print(result)
else:
    print("No image files found or error in scanning") 