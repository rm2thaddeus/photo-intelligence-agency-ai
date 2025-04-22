# 🗺️ Photo Intelligence Agency Roadmap

## Current Version: 0.2.0-alpha

## Development Phases

### Phase 1: Foundation (Q1 2024) ✅
- ✅ Initial project setup and repository structure
- ✅ Basic agent architecture setup
- ✅ Environment configuration and dependency management
- ✅ Core tool development
  - ✅ File system scanning
  - ✅ Metadata extraction
  - ✅ Embedding generation
  - ✅ Qdrant integration
- ✅ Basic workflow implementation
  - ✅ Image processing pipeline
  - ✅ Video processing pipeline
  - ✅ CUDA acceleration integration
  - ✅ Structured output organization

### Phase 2: MediaManager Enhancement & Curator Foundation (Current Focus)
- ✅ **MediaManager Robustness (Priority)**
  - ✅ File system scanning (`DirectoryInspector` tool implemented)
  - [ ] Metadata extraction tool refinement/creation (`MetadataExtractor`)
  - [ ] Embedding generation tool (`EmbeddingGenerator` - e.g., using sentence-transformers)
  - [ ] Qdrant integration tool (`QdrantUploader`)
  - [ ] Update MediaManager workflow instructions to use processing tools
  - [ ] Add necessary dependencies (qdrant-client, sentence-transformers) to requirements.txt
- 🔄 **CuratorAgent Foundation**
  - [ ] Initial CuratorAgent implementation skeleton
  - [ ] Design data structures for curated outputs (clusters, galleries)
  - [ ] *Defer full implementation of Curator tools (Clustering, Gallery Gen, Search, Analytics) until MediaManager pipeline is stable.*
- [ ] **UI Development (Initial)**
  - [ ] Implement basic Gradio UI via `agency.run_demo(gradio=True)` for interaction and logging.
- [ ] Integration between MediaManager and Curator
  - [ ] Define data flow from MediaManager's storage (Qdrant) to Curator
- [ ] Enhanced metadata organization (Deferred slightly)
  - [ ] Custom metadata fields
  - [ ] Metadata validation
  - [ ] Batch updates

### Phase 3: Curator Development & UI Enhancement (Q3 2024)
- [ ] **CuratorAgent Tooling**
  - [ ] Media clustering tool (HDBSCAN, etc.)
  - [ ] Gallery generation tool (HTML templates)
  - [ ] Search and retrieval tool (Qdrant semantic search)
  - [ ] Analytics tool
- [ ] **UI Enhancements**
  - [ ] Explore more custom UI options if needed (Streamlit, Flask, etc.)
  - [ ] Gallery customization options
  - [ ] Interactive filters
  - [ ] Advanced search interface
- [ ] Performance optimization
  - Batch processing improvements
  - Memory usage optimization
  - Processing queue management

### Phase 4: Optimization & Scale (Late Q3/Q4 2024)
- [ ] Distributed computing support
- [ ] Error handling and recovery improvements
- [ ] Monitoring and logging enhancements
- [ ] Security enhancements

### Phase 5: Advanced Features (Q4 2024 / Q1 2025)
- [ ] Advanced AI capabilities
  - Object detection
  - Face recognition
  - Scene understanding
- [ ] Integration capabilities
  - Cloud storage providers
  - Social media platforms
  - Photo management software
- [ ] Collaboration features
  - Multi-user support
  - Shared collections
  - Access management

### Phase 6: Future Vision (2025+)
- [ ] Mobile support
- [ ] Cloud deployment
- [ ] API ecosystem
- [ ] Plugin architecture

## Ongoing Priorities
- 🔄 Documentation maintenance
- 🔄 Code quality and testing
- 🔄 Performance monitoring
- 🔄 Security updates
- 🔄 User feedback integration

## Next Steps (Immediate Focus)
1.  Implement/Refine `MediaManager` tools (`MetadataExtractor`, `EmbeddingGenerator`, `QdrantUploader`).
2.  Update `MediaManager` instructions & `requirements.txt`.
3.  Implement basic Gradio UI in `agency.py`.
4.  Test the data ingestion pipeline (scan -> metadata -> embedding -> Qdrant).
5.  Begin skeleton implementation of `CuratorAgent`.