import os
from pydantic import Field
from agency_swarm.tools import BaseTool
import fnmatch

# Define common media file extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg'}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS.union(VIDEO_EXTENSIONS)

# Maximum output size to stay well below OpenAI's limit
MAX_OUTPUT_SIZE = 500000  # Set to 500KB, which is about half of the allowed 1MB

class FileSystemScanner(BaseTool):
    """
    Scans a specified directory path for media files (images and videos)
    based on common file extensions and returns a list of their full paths.
    It can optionally scan recursively and apply include/exclude patterns.
    Results are limited to stay within OpenAI's API size limits.
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
    max_files: int = Field(
        default=100, description="Maximum number of files to return in the results."
    )

    def _matches_patterns(self, file_path: str, patterns: list[str]) -> bool:
        """Check if the file path matches any of the glob patterns."""
        if not patterns:
            return False
        for pattern in patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
        return False

    def run(self) -> str:
        """
        Executes the directory scan based on the provided path and options.
        Returns a formatted string with the scan results, limiting the output size
        to stay within API limits.
        """
        media_files = []
        normalized_path = os.path.abspath(self.directory_path)

        if not os.path.isdir(normalized_path):
            return f"Error: Directory not found at {normalized_path}"

        try:
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
                        
                        # Stop collecting if we've reached the max number of files
                        if len(media_files) >= self.max_files:
                            break
                
                # Stop if we've already collected enough files
                if len(media_files) >= self.max_files:
                    break
                
                # If not recursive, break after the first level
                if not self.recursive:
                    break

            # Format the results as a string
            if not media_files:
                return "No media files found in the specified directory."
            
            result = f"Found {len(media_files)} media files"
            total_found = len(media_files)
            
            # Truncate the list if there are too many files to display
            if len(media_files) > 50:
                result += f" (showing first 50 of {total_found}):\n"
                media_files = media_files[:50]
            else:
                result += ":\n"
            
            # Add files to the result, keeping track of output size
            output_size = len(result)
            truncated = False
            
            for file_path in media_files:
                line = f"- {file_path}\n"
                if output_size + len(line) < MAX_OUTPUT_SIZE:
                    result += line
                    output_size += len(line)
                else:
                    truncated = True
                    break
            
            if truncated or total_found > 50:
                result += f"\n(Output truncated. Total files found: {total_found})"
            
            return result

        except Exception as e:
            return f"Error scanning directory: {str(e)}"

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
    print(result)
    
    print("\n--- Test Case 2: Max Files Limit ---")
    scanner = FileSystemScanner(directory_path=test_dir, max_files=2)
    result = scanner.run()
    print(result)

    print("\n--- Test Case 3: Include Pattern Scan ---")
    scanner = FileSystemScanner(directory_path=test_dir, include_patterns=["*.png", "*.mp4"])
    result = scanner.run()
    print(result)

    # Cleanup dummy files and directories
    import shutil
    shutil.rmtree(test_dir)
    print(f"\nCleaned up test directory: {test_dir}") 