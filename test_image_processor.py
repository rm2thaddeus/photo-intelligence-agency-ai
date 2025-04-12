from MediaManager.tools.FileSystemScanner import FileSystemScanner
from MediaManager.tools.ImageProcessor import ImageProcessor

# First, scan for images
scanner = FileSystemScanner(directory_path=r"C:\Users\aitor\OneDrive\Escritorio\test images")
image_paths = scanner.run()

print("Found images:", image_paths)

# Now process the images
processor = ImageProcessor(input_paths=image_paths)
result = processor.run()
print("\nProcessing results:", result) 