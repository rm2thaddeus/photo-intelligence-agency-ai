from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import os
import torch
from PIL import Image, ExifTags, UnidentifiedImageError
import rawpy
from datetime import datetime
from pydantic import Field, validator
from agency_swarm.tools import BaseTool

# --- Import Shared Resources ---
from .processing_utils import (
    logger,
    qdrant_client,
    processor,
    model,
    DEVICE,
    EMBEDDING_DIM,
    QDRANT_COLLECTION_NAME
)

class ImageProcessor(BaseTool):
    """
    Processes multiple images from a directory or list of paths:
    - Handles various image formats (JPEG, PNG, RAW/DNG)
    - Extracts comprehensive metadata
    - Generates CLIP embeddings
    - Stores data in Qdrant vector database
    Requires initialized CLIP model and Qdrant client from processing_utils.
    """
    
    input_paths: List[str] = Field(
        ...,
        description="List of image file paths or directories to process"
    )
    
    batch_size: int = Field(
        default=32,
        description="Batch size for processing images (adjust based on available GPU memory)"
    )

    @validator('input_paths')
    def validate_paths(cls, paths):
        valid_paths = []
        for path in paths:
            p = Path(path)
            if p.exists():
                if p.is_file() and p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.dng', '.raw', '.arw', '.cr2', '.nef'}:
                    valid_paths.append(str(p.resolve()))
                elif p.is_dir():
                    # Add all valid image files from directory
                    valid_paths.extend([
                        str(f.resolve()) for f in p.rglob('*')
                        if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.dng', '.raw', '.arw', '.cr2', '.nef'}
                    ])
        if not valid_paths:
            raise ValueError("No valid image files found in the provided paths")
        return valid_paths

    def _extract_metadata(self, img_path: Path) -> Dict[str, Any]:
        """Extracts comprehensive metadata from image file."""
        metadata = {
            'filename': img_path.name,
            'file_path': str(img_path.resolve()),
            'file_size_bytes': img_path.stat().st_size,
            'file_creation_time': datetime.fromtimestamp(img_path.stat().st_ctime),
            'file_modification_time': datetime.fromtimestamp(img_path.stat().st_mtime),
            'media_type': 'image'
        }
        
        try:
            # Handle RAW files
            if img_path.suffix.lower() in {'.dng', '.raw', '.arw', '.cr2', '.nef'}:
                with rawpy.imread(str(img_path)) as raw:
                    metadata.update({
                        'image_width': raw.sizes.width,
                        'image_height': raw.sizes.height,
                        'image_format': 'RAW',
                        'raw_type': img_path.suffix.lower(),
                        'bits_per_pixel': raw.raw_image.dtype.itemsize * 8,
                        'color_description': str(raw.color_desc)
                    })
            else:
                # Handle regular image files
                with Image.open(img_path) as img:
                    metadata.update({
                        'image_width': img.width,
                        'image_height': img.height,
                        'image_format': img.format,
                        'image_mode': img.mode,
                    })
                    
                    # Extract EXIF data
                    if hasattr(img, '_getexif') and img._getexif():
                        exif = {}
                        for tag_id, value in img._getexif().items():
                            tag = ExifTags.TAGS.get(tag_id, tag_id)
                            # Handle bytes and long strings
                            if isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8', errors='replace')
                                except:
                                    value = str(value)
                            elif isinstance(value, str) and len(value) > 1000:
                                value = value[:1000] + '...'
                            exif[str(tag)] = str(value)
                        metadata['exif_data'] = exif
                    
        except Exception as e:
            logger.warning(f"Error extracting metadata from {img_path.name}: {e}")
            
        return metadata

    def _process_batch(self, image_paths: List[Path]) -> List[Dict[str, Any]]:
        """Process a batch of images: load, generate embeddings, prepare for database."""
        results = []
        
        # Load and preprocess images
        valid_images = []
        valid_paths = []
        for img_path in image_paths:
            try:
                if img_path.suffix.lower() in {'.dng', '.raw', '.arw', '.cr2', '.nef'}:
                    with rawpy.imread(str(img_path)) as raw:
                        # Convert RAW to RGB
                        rgb = raw.postprocess()
                        img = Image.fromarray(rgb)
                else:
                    img = Image.open(img_path)
                    
                if img.mode != "RGB":
                    img = img.convert("RGB")
                    
                # Extract metadata first
                metadata = self._extract_metadata(img_path)
                
                # Prepare for CLIP
                inputs = processor(images=img, return_tensors="pt", padding=True)
                valid_images.append(inputs)
                valid_paths.append((img_path, metadata))
                
            except Exception as e:
                logger.error(f"Error processing {img_path.name}: {e}")
                continue
                
        if not valid_images:
            return []
            
        try:
            # Combine all preprocessed images
            batch_inputs = {
                k: torch.cat([img[k] for img in valid_images]).to(DEVICE)
                for k in valid_images[0].keys()
            }
            
            # Generate embeddings
            with torch.no_grad():
                outputs = model.get_image_features(**batch_inputs)
            embeddings = outputs.cpu().numpy()
            
            # Prepare results with metadata and embeddings
            for idx, (img_path, metadata) in enumerate(valid_paths):
                results.append({
                    'metadata': metadata,
                    'embedding': embeddings[idx].tolist()
                })
                
        except Exception as e:
            logger.error(f"Error generating embeddings for batch: {e}")
            
        return results

    def _upsert_to_qdrant(self, processed_data: List[Dict[str, Any]]) -> bool:
        """Upsert processed image data to Qdrant."""
        if not qdrant_client:
            logger.error("Qdrant client not initialized")
            return False
            
        try:
            points = []
            for data in processed_data:
                metadata = data['metadata']
                # Convert datetime objects to ISO format strings
                if metadata.get('file_creation_time'):
                    metadata['file_creation_time'] = metadata['file_creation_time'].isoformat()
                if metadata.get('file_modification_time'):
                    metadata['file_modification_time'] = metadata['file_modification_time'].isoformat()
                
                points.append(PointStruct(
                    id=str(metadata['file_path']),
                    vector=data['embedding'],
                    payload=metadata
                ))
                
            if points:
                qdrant_client.upsert(
                    collection_name=QDRANT_COLLECTION_NAME,
                    points=points,
                    wait=True
                )
            return True
            
        except Exception as e:
            logger.error(f"Error upserting to Qdrant: {e}")
            return False

    def run(self) -> Dict[str, Any]:
        """
        Process all images in input_paths:
        1. Validate and collect image paths
        2. Process images in batches
        3. Generate embeddings
        4. Store in Qdrant
        Returns summary of processing results.
        """
        if not model or not processor:
            return {"status": "error", "message": "CLIP model/processor not initialized"}
        if not qdrant_client:
            return {"status": "error", "message": "Qdrant client not initialized"}
            
        total_processed = 0
        total_failed = 0
        processed_paths = []
        failed_paths = []
        
        # Process in batches
        current_batch = []
        for path in self.input_paths:
            current_batch.append(Path(path))
            
            if len(current_batch) >= self.batch_size:
                results = self._process_batch(current_batch)
                if results:
                    if self._upsert_to_qdrant(results):
                        total_processed += len(results)
                        processed_paths.extend([r['metadata']['file_path'] for r in results])
                    else:
                        total_failed += len(results)
                        failed_paths.extend([r['metadata']['file_path'] for r in results])
                current_batch = []
        
        # Process remaining images
        if current_batch:
            results = self._process_batch(current_batch)
            if results:
                if self._upsert_to_qdrant(results):
                    total_processed += len(results)
                    processed_paths.extend([r['metadata']['file_path'] for r in results])
                else:
                    total_failed += len(results)
                    failed_paths.extend([r['metadata']['file_path'] for r in results])
        
        return {
            "status": "success" if total_processed > 0 else "error",
            "total_processed": total_processed,
            "total_failed": total_failed,
            "processed_paths": processed_paths,
            "failed_paths": failed_paths
        }

# Example Test Case
if __name__ == "__main__":
    # Create test directory with dummy images
    test_dir = Path("./temp_image_test")
    test_dir.mkdir(exist_ok=True)
    
    # Create a few test images
    test_images = []
    for i in range(3):
        img_path = test_dir / f"test_image_{i}.png"
        img = Image.new('RGB', (60, 30), color=f'#{i*20:02x}0000')
        img.save(img_path)
        test_images.append(str(img_path.resolve()))
        
    try:
        print("\n--- Testing ImageProcessor ---")
        processor_tool = ImageProcessor(input_paths=test_images, batch_size=2)
        result = processor_tool.run()
        print("\nProcessing Result:")
        print(result)
        
        if result["status"] == "success":
            # Verify in Qdrant
            try:
                for path in result["processed_paths"]:
                    search_result = qdrant_client.retrieve(
                        collection_name=QDRANT_COLLECTION_NAME,
                        ids=[path],
                        with_payload=True
                    )
                    if search_result:
                        print(f"\nVerified in Qdrant: {path}")
                        print("Metadata:", search_result[0].payload)
            except Exception as q_err:
                print(f"\nQdrant verification error: {q_err}")
                
    except Exception as e:
        print(f"\nTest error: {e}")
    finally:
        # Cleanup
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print("\n--- Cleanup Complete ---")