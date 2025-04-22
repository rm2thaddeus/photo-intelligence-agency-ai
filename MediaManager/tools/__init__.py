"""
Tools for media processing and management.
"""

# Import all tools with error handling
try:
    from .FileSystemScanner import FileSystemScanner
    from .ImageProcessor import ImageProcessor
    from .VideoProcessor import VideoProcessor
    
    __all__ = ['FileSystemScanner', 'ImageProcessor', 'VideoProcessor']
except ImportError as e:
    import sys
    print(f"Error importing MediaManager tools: {e}", file=sys.stderr)
    # Provide fallback minimal imports if possible
    __all__ = [] 