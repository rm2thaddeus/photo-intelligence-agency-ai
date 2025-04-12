from MediaManager.tools.FileSystemScanner import FileSystemScanner

# Test with the image directory
scanner = FileSystemScanner(directory_path=r"C:\Users\aitor\OneDrive\Escritorio\test images")
result = scanner.run()
print("Found files:", result) 