import os
import logging
import base64
import uuid
from typing import Dict, Any, Optional, Tuple
import cv2
import numpy as np

logger = logging.getLogger(__name__)

def ensure_upload_dir(upload_folder: str) -> None:
    """Ensure the upload directory exists"""
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        logger.info(f"Created upload directory: {upload_folder}")

def delete_old_files(folder: str, max_age_days: int = 7) -> None:
    """Delete files older than max_age_days from the specified folder"""
    import time
    from datetime import datetime, timedelta
    
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 60 * 60
    
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        
        # Skip if it's not a file
        if not os.path.isfile(file_path):
            continue
        
        # Get file modification time
        file_age = current_time - os.path.getmtime(file_path)
        
        # If file is older than max_age_days, delete it
        if file_age > max_age_seconds:
            try:
                os.remove(file_path)
                logger.info(f"Deleted old file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {str(e)}")

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename with UUID to prevent collisions"""
    unique_id = str(uuid.uuid4())
    if '.' in original_filename:
        extension = original_filename.rsplit('.', 1)[1].lower()
        return f"{unique_id}.{extension}"
    return unique_id

def image_to_base64(image_path: str) -> Optional[str]:
    """Convert an image file to a base64 encoded string"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error converting image to base64: {str(e)}")
        return None

def base64_to_cv2(base64_string: str) -> Optional[np.ndarray]:
    """Convert a base64 encoded image to a cv2 image object"""
    try:
        # Decode base64 string
        img_data = base64.b64decode(base64_string)
        
        # Convert to numpy array
        nparr = np.frombuffer(img_data, np.uint8)
        
        # Decode the numpy array as an image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return img
    except Exception as e:
        logger.error(f"Error converting base64 to cv2 image: {str(e)}")
        return None

def calculate_confidence(warp_count: int, weft_count: int, 
                         warp_std: float, weft_std: float) -> float:
    """
    Calculate a confidence score based on thread count and consistency
    
    Args:
        warp_count: Count of warp threads
        weft_count: Count of weft threads
        warp_std: Standard deviation of warp thread spacing
        weft_std: Standard deviation of weft thread spacing
        
    Returns:
        Confidence score between 0 and 1
    """
    # Check for unrealistic thread counts
    if warp_count < 5 or weft_count < 5:
        return 0.3
    
    # Calculate coefficient of variation (normalized standard deviation)
    warp_cv = warp_std / warp_count if warp_count > 0 else 1.0
    weft_cv = weft_std / weft_count if weft_count > 0 else 1.0
    
    # Low CV indicates consistent thread spacing (higher confidence)
    # Map CV to confidence score: lower CV = higher confidence
    warp_conf = max(0, min(1, 1 - warp_cv))
    weft_conf = max(0, min(1, 1 - weft_cv))
    
    # Average the confidence scores
    return (warp_conf + weft_conf) / 2.0
