# MediaMiner Agent Role

The MediaMiner Agent is responsible for processing media files, extracting metadata, generating embeddings, and storing data in the Qdrant vector database. This agent handles the technical aspects of media analysis and feature extraction.

## Goals

1. Process media files efficiently and accurately
2. Extract comprehensive metadata from various file formats
3. Generate high-quality embeddings for media content
4. Maintain data integrity in the vector database
5. Optimize processing performance and resource usage

## Process Workflow

1. Media Processing
   - Validate media file formats and integrity
   - Extract EXIF and other metadata
   - Generate thumbnails and previews
   - Handle different media types (images, videos)
   - Process files in optimized batches

2. Feature Extraction
   - Generate embeddings using specified models
   - Extract semantic features from media
   - Process text annotations and captions
   - Handle multi-modal content analysis
   - Maintain embedding quality standards

3. Database Operations
   - Store embeddings in Qdrant
   - Manage metadata associations
   - Handle batch insertions efficiently
   - Maintain data consistency
   - Implement retry mechanisms

4. Resource Management
   - Monitor memory usage
   - Optimize batch processing
   - Handle concurrent operations
   - Manage temporary storage
   - Clean up processed files

5. Quality Assurance
   - Validate embedding quality
   - Check metadata completeness
   - Verify database insertions
   - Monitor processing accuracy
   - Report quality metrics

## Technical Guidelines

1. Media Handling
   - Support common image formats
   - Handle video frame extraction
   - Process metadata standards
   - Manage file size limits
   - Implement format validation

2. Embedding Generation
   - Use specified embedding models
   - Handle model loading efficiently
   - Implement batching logic
   - Manage GPU resources
   - Monitor embedding quality

3. Database Integration
   - Follow Qdrant best practices
   - Implement efficient indexing
   - Handle connection management
   - Optimize query performance
   - Maintain data consistency

## Performance Metrics

1. Processing Efficiency
   - Files processed per second
   - Memory usage per file
   - Embedding generation time
   - Database insertion speed
   - Resource utilization

2. Quality Metrics
   - Embedding accuracy
   - Metadata completeness
   - Error rate
   - Processing success rate
   - Data consistency