"""
Test script to verify the MediaManager and its tools are working correctly.
"""
import os
import sys
from MediaManager.MediaManager import MediaManager
from MediaManager.tools.FileSystemScanner import FileSystemScanner

def test_media_manager():
    # Initialize the MediaManager
    print("Initializing MediaManager...")
    try:
        media_manager = MediaManager()
        print("✓ MediaManager initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize MediaManager: {str(e)}")
        return
    
    # Let's test the FileSystemScanner directly
    test_dir = os.path.expanduser("~")  # Use user's home directory for testing
    print(f"\nTesting FileSystemScanner on directory: {test_dir}")
    
    try:
        # Create a simple scanner instance directly
        scanner = FileSystemScanner(directory_path=test_dir, recursive=False)
        result = scanner.run()
        print("✓ FileSystemScanner direct test succeeded!")
        print(f"Result sample (first 200 chars): {result[:200]}...")
    except Exception as e:
        print(f"✗ FileSystemScanner direct test failed with error: {str(e)}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_media_manager() 