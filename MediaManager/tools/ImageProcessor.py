from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import os
import torch
from PIL import Image, ExifTags, UnidentifiedImageError
import rawpy
from datetime import datetime
from pydantic import Field, validator
from agency_swarm.tools import BaseTool
from qdrant_client.http.models import PointStruct
import json

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
    Creates and manages the image database in Qdrant:
    - Handles various image formats (JPEG, PNG, RAW/DNG)
    - Extracts comprehensive metadata
    - Generates CLIP embeddings
    - Stores and updates image data in the Qdrant vector database, creating the image database if it does not exist
    This tool is responsible for initializing, populating, and updating the image database as needed. Requires initialized CLIP model and Qdrant client from processing_utils.
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
        Process all images in input_paths, generates embeddings, stores in Qdrant,
        and returns a status summary.
        """
        try:
            # Validate model and processor
            if not model or not processor:
                logger.error("CLIP model/processor not initialized")
                return {
                    'status': 'error',
                    'message': 'CLIP model or processor not initialized'
                }
            if not qdrant_client:
                 logger.error("Qdrant client not initialized")
                 return {
                    'status': 'error',
                    'message': 'Qdrant client not initialized'
                 }

            # Process images in batches
            all_results = []
            successfully_processed_paths = []
            failed_paths = []
            
            valid_input_paths = self.validate_paths(self.input_paths) # Re-validate here to ensure we have the full list
            
            logger.info(f"Starting processing for {len(valid_input_paths)} images...")

            for i in range(0, len(valid_input_paths), self.batch_size):
                batch_paths_str = valid_input_paths[i:i + self.batch_size]
                batch_paths_obj = [Path(p) for p in batch_paths_str]
                logger.info(f"Processing batch {i // self.batch_size + 1} ({len(batch_paths_obj)} images)")
                batch_results = self._process_batch(batch_paths_obj)
                all_results.extend(batch_results)
                # Keep track of which paths succeeded in this batch
                for res in batch_results:
                    successfully_processed_paths.append(res['metadata']['file_path'])
            
            # Determine failed paths
            failed_paths = [p for p in valid_input_paths if p not in successfully_processed_paths]

            if not all_results:
                logger.warning("No images were successfully processed during embedding generation.")
                return {
                    'status': 'warning',
                    'message': 'No images were successfully processed for embedding.',
                    'processed_count': 0,
                    'failed_count': len(failed_paths),
                    'failed_paths': failed_paths
                }

            # Upsert results to Qdrant
            logger.info(f"Upserting {len(all_results)} processed images to Qdrant...")
            upsert_success = self._upsert_to_qdrant(all_results)

            if upsert_success:
                logger.info(f"Successfully upserted {len(all_results)} items to Qdrant.")
                final_status = 'success'
                final_message = f"Successfully processed and stored {len(all_results)} images."
            else:
                logger.error("Failed to upsert data to Qdrant.")
                final_status = 'error'
                final_message = f"Processed {len(all_results)} images, but failed to store them in Qdrant."
                # Add successfully processed paths to failed paths if Qdrant fails
                failed_paths.extend(successfully_processed_paths)
                successfully_processed_paths = [] # Reset success list

            return {
                'status': final_status,
                'message': final_message,
                'processed_count': len(successfully_processed_paths),
                'failed_count': len(failed_paths),
                'failed_paths': failed_paths
            }

        except Exception as e:
            logger.error(f"Error during image processing pipeline: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': f"An unexpected error occurred: {e}",
                'processed_count': 0,
                'failed_count': len(self.input_paths), # Assume all failed on major error
                'failed_paths': self.input_paths
            }

# Example Test Case
if __name__ == "__main__":
    # NOTE: This test requires a running Qdrant instance and proper environment setup
    #       (CLIP models downloaded, .env file with QDRANT_URL, QDRANT_API_KEY)
    
    # Ensure processing_utils initializes correctly
    if not model or not processor or not qdrant_client:
        print("ERROR: CLIP model/processor or Qdrant client not initialized.")
        print("Please ensure processing_utils.py runs correctly and Qdrant is accessible.")
        exit()
    
    # Create test directory with dummy images
    test_dir = Path("./temp_image_test_integration")
    test_dir.mkdir(exist_ok=True)
    img1_path = test_dir / "test1.png"
    img2_path = test_dir / "test2.jpg"
    invalid_path = test_dir / "not_an_image.txt"
    try:
        Image.new('RGB', (60, 30), color = 'red').save(img1_path)
        Image.new('RGB', (100, 100), color = 'blue').save(img2_path)
        with open(invalid_path, "w") as f:
            f.write("hello")
        print(f"Created test files in: {test_dir.resolve()}")
    except Exception as e:
        print(f"Error creating test files: {e}")
        # Potentially clean up if creation failed partially
        if test_dir.exists():
             shutil.rmtree(test_dir)
        exit()

    # Instantiate the tool
    image_processor_tool = ImageProcessor(
        input_paths=[str(test_dir.resolve())] # Process the whole directory
    )

    # Run the tool
    print("\n--- Running ImageProcessor Tool ---")
    result = image_processor_tool.run()
    print("\n--- Result ---")
    print(json.dumps(result, indent=2))

    # Verification (Optional - requires direct Qdrant query)
    if result['status'] == 'success' and result['processed_count'] > 0:
        try:
            # Check if points exist in Qdrant (example for one file)
            fetch_result = qdrant_client.retrieve(
                collection_name=QDRANT_COLLECTION_NAME,
                ids=[str(img1_path.resolve())]
            )
            if fetch_result:
                print(f"\nVerification: Successfully retrieved point for {img1_path.name} from Qdrant.")
            else:
                print(f"\nVerification WARNING: Could not retrieve point for {img1_path.name} from Qdrant.")
        except Exception as e:
            print(f"\nVerification ERROR: Could not query Qdrant - {e}")
            
    # Cleanup
    print("\n--- Cleaning up --- ")
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"Removed test directory: {test_dir.resolve()}")