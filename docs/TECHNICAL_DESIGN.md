# 🏗️ Photo Intelligence Agency Technical Design

## System Architecture

### Overview
The Photo Intelligence Agency is built on a modular, agent-based architecture for robust, scalable, and maintainable media processing. The system is inspired by microservices principles but is deployed as a monolithic application for simplicity and performance.

### Core Components

- **FileSystemScanner**: Responsible for discovering media files (images and videos) in the file system. Supports recursive and pattern-based scanning.

- **ImageProcessor**: Handles all image processing tasks, including:
  - Metadata extraction (EXIF, file stats, etc.)
  - Embedding generation using CLIP
  - Uploading results and embeddings to Qdrant
  - Batch processing and error handling

- **VideoProcessor**: Handles all video processing tasks, including:
  - Metadata extraction (via ffmpeg)
  - Scene detection and frame extraction
  - Embedding generation for representative frames using CLIP
  - Uploading results and embeddings to Qdrant
  - Batch processing and error handling

- **processing_utils.py**: Provides shared resources and utilities, including:
  - CLIP model and processor initialization
  - Qdrant client setup and collection management
  - Device management (CPU/GPU)
  - Logging and environment configuration

### Design Principles

- **Encapsulation**: Each processor encapsulates all steps required for its media type (discovery, metadata, embedding, upload), reducing the need for separate tool modules like `MetadataExtractor`, `EmbeddingGenerator`, or `QdrantUploader`.
- **Reusability**: Shared logic (model loading, database connection) is centralized in `processing_utils.py`.
- **Extensibility**: New processors or tools can be added with minimal changes to the core system.
- **Agent-based Orchestration**: The system is designed to support agent-based workflows, enabling future expansion with more complex orchestration and collaboration between agents (e.g., CuratorAgent).

### Data Flow

1. **Discovery**: `FileSystemScanner` identifies relevant media files.
2. **Processing**: `ImageProcessor` and `VideoProcessor` extract metadata, generate embeddings, and prepare data for storage.
3. **Storage**: Results and embeddings are uploaded to Qdrant for fast semantic search and retrieval.
4. **Orchestration**: Agents coordinate the workflow, enabling batch operations, error recovery, and future integration with UI or curator modules.

### Alignment with Roadmap
- The current focus is on refining and optimizing the existing processors, not on building redundant or separate extraction/upload tools.
- All core processing steps are already integrated into the main processor modules.
- Future work will focus on UI, curator agent development, and advanced analytics, as outlined in the roadmap.

---

This design ensures a maintainable, extensible, and production-ready foundation for advanced media intelligence workflows.