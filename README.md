# MediaManager

A Python package for managing and processing media files, with support for:
- Image processing and analysis using CLIP embeddings
- Video processing with scene detection
- Vector storage using Qdrant
- File system scanning and organization

## Installation

```bash
pip install -e .
```

## Requirements

- Python 3.8 or higher
- Docker (for Qdrant vector storage)
- FFmpeg (for video processing)

## Quick Start

1. Start Qdrant:
```bash
docker-compose up -d
```

2. Run tests:
```bash
python tests/test_qdrant_connection.py
python tests/test_image_processor.py
python tests/test_video_processing.py
```

## Directory Structure

```
MediaManager/
├── tools/
│   ├── FileSystemScanner.py
│   ├── ImageProcessor.py
│   ├── VideoProcessor.py
│   └── processing_utils.py
└── tests/
    ├── outputs/
    │   ├── images/
    │   └── videos/
    ├── test_image_processor.py
    ├── test_video_processing.py
    └── test_qdrant_connection.py
```