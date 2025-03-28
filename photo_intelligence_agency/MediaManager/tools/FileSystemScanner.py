import os
from pydantic import Field
from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
import fnmatch

load_dotenv()

# Define common media file extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg'}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS.union(VIDEO_EXTENSIONS)

class FileSystemScanner(BaseTool):
    """
    Scans a specified directory path for media files (images and videos)
    based on common file extensions and returns a list of their full paths.
    It can optionally scan recursively and apply include/exclude patterns.
    """
    directory_path: str = Field(
        ..., description="The absolute or relative path to the directory to scan."
    )
    recursive: bool = Field(
        default=True, description="Whether to scan subdirectories recursively."
    )
    include_patterns: list[str] = Field(
        default=None, description="Optional list of glob patterns to include files. If None, all media files are considered."
    )
    exclude_patterns: list[str] = Field(
        default=None, description="Optional list of glob patterns to exclude files or directories."
    )

    def _matches_patterns(self, file_path: str, patterns: list[str]) -> bool:
        """Check if the file path matches any of the glob patterns."""
        if not patterns:
            return False
        for pattern in patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
        return False

    def run(self) -> list[str]:
        """
        Executes the directory scan based on the provided path and options.
        Returns a list of full paths to the found media files.
        """
        media_files = []
        normalized_path = os.path.abspath(self.directory_path)

        if not os.path.isdir(normalized_path):
            return f"Error: Directory not found at {normalized_path}"

        for root, dirs, files in os.walk(normalized_path):
            # Apply exclude patterns to directories
            if self.exclude_patterns:
                # Modify dirs in-place to prevent os.walk from traversing them
                dirs[:] = [d for d in dirs if not self._matches_patterns(os.path.join(root, d), self.exclude_patterns)]

            for filename in files:
                file_path = os.path.join(root, filename)
                _, ext = os.path.splitext(filename.lower())

                # Check if the file should be excluded
                if self.exclude_patterns and self._matches_patterns(file_path, self.exclude_patterns):
                    continue

                # Check if the file matches include patterns (if any)
                passes_include = True
                if self.include_patterns and not self._matches_patterns(file_path, self.include_patterns):
                    passes_include = False

                # Check if it's a media file and passes include filter
                if ext in MEDIA_EXTENSIONS and passes_include:
                    media_files.append(file_path)

            # If not recursive, break after the first level
            if not self.recursive:
                break

        return media_files

# Example Test Case
if __name__ == "__main__":
    # Create dummy directories and files for testing
    test_dir = "test_media_scan"
    os.makedirs(os.path.join(test_dir, "subdir"), exist_ok=True)
    open(os.path.join(test_dir, "image1.jpg"), 'a').close()
    open(os.path.join(test_dir, "image2.png"), 'a').close()
    open(os.path.join(test_dir, "document.txt"), 'a').close()
    open(os.path.join(test_dir, "subdir", "video1.mp4"), 'a').close()
    open(os.path.join(test_dir, "subdir", "image3_archive.jpeg"), 'a').close()
    open(os.path.join(test_dir, "exclude_me.jpg"), 'a').close()
    os.makedirs(os.path.join(test_dir, "excluded_dir"), exist_ok=True)
    open(os.path.join(test_dir, "excluded_dir", "image4.png"), 'a').close()


    print("--- Test Case 1: Basic Recursive Scan ---")
    scanner = FileSystemScanner(directory_path=test_dir)
    result = scanner.run()
    print(f"Found {len(result)} media files:")
    for f in result: print(f"- {f}")
    # Expected: image1.jpg, image2.png, subdir/video1.mp4, subdir/image3_archive.jpeg, exclude_me.jpg, excluded_dir/image4.png (paths will be absolute)

    print("\n--- Test Case 2: Non-Recursive Scan ---")
    scanner = FileSystemScanner(directory_path=test_dir, recursive=False)
    result = scanner.run()
    print(f"Found {len(result)} media files:")
    for f in result: print(f"- {f}")
    # Expected: image1.jpg, image2.png, exclude_me.jpg (paths will be absolute)

    print("\n--- Test Case 3: Include Pattern Scan ---")
    scanner = FileSystemScanner(directory_path=test_dir, include_patterns=["*.png", "*.mp4"])
    result = scanner.run()
    print(f"Found {len(result)} media files:")
    for f in result: print(f"- {f}")
    # Expected: image2.png, subdir/video1.mp4, excluded_dir/image4.png (paths will be absolute)

    print("\n--- Test Case 4: Exclude Pattern Scan (File) ---")
    scanner = FileSystemScanner(directory_path=test_dir, exclude_patterns=["exclude_me.jpg", "*_archive.*"])
    result = scanner.run()
    print(f"Found {len(result)} media files:")
    for f in result: print(f"- {f}")
    # Expected: image1.jpg, image2.png, subdir/video1.mp4, excluded_dir/image4.png (paths will be absolute)

    print("\n--- Test Case 5: Exclude Pattern Scan (Directory) ---")
    scanner = FileSystemScanner(directory_path=test_dir, exclude_patterns=["excluded_dir/*", "*/subdir/*archive*"])
    result = scanner.run()
    print(f"Found {len(result)} media files:")
    for f in result: print(f"- {f}")
    # Expected: image1.jpg, image2.png, subdir/video1.mp4, exclude_me.jpg (paths will be absolute)

    # Cleanup dummy files and directories
    import shutil
    shutil.rmtree(test_dir)
    print(f"\nCleaned up test directory: {test_dir}") 