# Photo Intelligence Agency

A modular, agent-based Python system for intelligent media management, curation, and presentation. The agency leverages specialized agents for file discovery, media processing, clustering, semantic search, and gallery generation, with robust test coverage and CI/CD readiness.

## Features
- Image and video processing with CLIP embeddings
- Scene detection and metadata extraction
- Semantic clustering and gallery generation
- Vector storage and search using Qdrant
- Modular agent-based architecture (MediaManager, CuratorAgent, CEOAgent)
- Production-quality, framework-based test suite

## Installation

```bash
pip install -e .
```

## Requirements
- Python 3.10 or higher
- Docker (for Qdrant vector storage)
- FFmpeg (for video processing)
- OpenAI API key (for summary generation)

## Quick Start

1. Start Qdrant:
```bash
docker-compose up -d
```

2. Run all tests:
```bash
pytest tests/
```

## Directory Structure

```
PhotoIntelligenceAgency/
├── MediaManager/
│   └── tools/
├── CuratorAgent/
│   └── tools/
├── CEOAgent/
├── tests/
│   ├── MediaManager/
│   │   ├── test_image_processor.py
│   │   ├── test_video_processor.py
│   │   └── test_qdrant_connection.py
│   └── CuratorAgent/
│       ├── test_cluster_tool.py
│       ├── test_html_gallery_writer_tool.py
│       ├── test_qdrant_fetcher_tool.py
│       └── test_summary_writer_tool.py
├── agency_manifesto.md
├── docs/
│   ├── ROADMAP.md
│   └── TECHNICAL_DESIGN.md
└── README.md
```

## Agent Roles & Collaboration
- **CEOAgent**: Orchestrates overall operations and agent collaboration
- **MediaManager**: Handles file discovery, image/video processing, and metadata extraction
- **CuratorAgent**: Performs clustering, summary generation, and gallery creation
- Agents communicate via structured protocols and maintain clear separation of concerns

## Documentation
- See `agency_manifesto.md` for agency principles and collaboration guidelines
- See `docs/ROADMAP.md` and `docs/TECHNICAL_DESIGN.md` for development plans and architecture

## Testing & Quality Assurance
- All tests are organized by agent/module in the `tests/` folder
- Run all tests with `pytest tests/`
- The test suite is CI/CD ready and ensures production-level reliability