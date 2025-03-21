import cv2
import numpy as np
import os
import logging
from typing import Tuple, Dict, Any, Optional
import base64

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ThreadCounter:
    """Class to handle image processing for thread counting in fabric images"""
    
    def __init__(self, unit: str = 'cm', reference_length: float = 1.0):
        """
        Initialize the thread counter
        
        Args:
            unit: The unit of measurement ('cm' or 'inch')
            reference_length: The reference length in the unit specified
        """
        self.unit = unit
        self.reference_length = reference_length
        logger.info(f"ThreadCounter initialized with unit {unit} and reference length {reference_length}")
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess the image for analysis
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image as numpy array
        """
        logger.debug(f"Preprocessing image: {image_path}")
        
        # Check if image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive threshold to highlight threads
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        logger.debug("Image preprocessing completed")
        
        return thresh
    
    def count_threads(self, image_path: str) -> Dict[str, Any]:
        """
        Count the threads in a fabric image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with thread counting results
        """
        logger.info(f"Starting thread counting for image: {image_path}")
        
        # Preprocess the image
        preprocessed = self.preprocess_image(image_path)
        
        # Get image dimensions
        height, width = preprocessed.shape
        
        # Define regions for warp and weft analysis
        # Warp threads run vertically
        warp_region = preprocessed[int(height * 0.25):int(height * 0.75), int(width * 0.4):int(width * 0.6)]
        
        # Weft threads run horizontally
        weft_region = preprocessed[int(height * 0.4):int(height * 0.6), int(width * 0.25):int(width * 0.75)]
        
        # Count threads using frequency domain analysis
        warp_count = self._frequency_domain_analysis(warp_region, vertical=True)
        weft_count = self._frequency_domain_analysis(weft_region, vertical=False)
        
        # Calculate thread density
        total_count = warp_count + weft_count
        
        # For demo purposes, let's calculate a confidence score (this would be refined in production)
        confidence_score = min(0.95, max(0.5, 0.75 + np.random.normal(0, 0.1)))
        
        # Create visualization of detected threads
        visual_result = self._create_visual_result(image_path, warp_count, weft_count)
        
        result = {
            'warp_count': warp_count,
            'weft_count': weft_count,
            'thread_density': total_count / self.reference_length,
            'confidence_score': confidence_score,
            'measurement_unit': self.unit,
            'visual_result': visual_result
        }
        
        logger.info(f"Thread counting completed. Warp: {warp_count}, Weft: {weft_count}")
        
        return result
    
    def _frequency_domain_analysis(self, image_region: np.ndarray, vertical: bool = True) -> int:
        """
        Analyze thread frequency using FFT
        
        Args:
            image_region: Region of the image to analyze
            vertical: Whether to count vertical threads (True) or horizontal (False)
            
        Returns:
            Count of threads detected
        """
        if vertical:
            # For vertical threads, calculate column-wise sum and analyze
            profile = np.sum(image_region, axis=0)
        else:
            # For horizontal threads, calculate row-wise sum and analyze
            profile = np.sum(image_region, axis=1)
        
        # Apply FFT to find dominant frequency (thread spacing)
        fft = np.fft.fft(profile)
        freqs = np.fft.fftfreq(len(profile))
        
        # Only consider positive frequencies and exclude DC component
        pos_freqs = freqs[1:len(freqs)//2]
        amplitudes = np.abs(fft[1:len(fft)//2])
        
        # Find peak frequency
        peak_idx = np.argmax(amplitudes)
        peak_freq = pos_freqs[peak_idx]
        
        # Thread count is proportional to the peak frequency
        # Scale based on image region size
        if vertical:
            region_size = image_region.shape[1]
        else:
            region_size = image_region.shape[0]
        
        thread_count = int(peak_freq * region_size * self.reference_length)
        
        # Ensure minimum sensible thread count
        thread_count = max(10, thread_count)
        
        return thread_count
    
    def _create_visual_result(self, image_path: str, warp_count: int, weft_count: int) -> str:
        """
        Create a visual representation of the detected threads
        
        Args:
            image_path: Path to the original image
            warp_count: Count of warp threads
            weft_count: Count of weft threads
            
        Returns:
            Base64 encoded string of the visualization image
        """
        # Read original image
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Could not read image for visualization: {image_path}")
            return ""
        
        # Create a copy for visualization
        visual = img.copy()
        height, width = visual.shape[:2]
        
        # Draw grid lines to represent detected threads
        # Warp threads (vertical)
        warp_spacing = width // (warp_count + 1)
        for i in range(1, warp_count + 1):
            x = i * warp_spacing
            cv2.line(visual, (x, 0), (x, height), (0, 255, 0), 1)
        
        # Weft threads (horizontal)
        weft_spacing = height // (weft_count + 1)
        for i in range(1, weft_count + 1):
            y = i * weft_spacing
            cv2.line(visual, (0, y), (width, y), (0, 0, 255), 1)
        
        # Add text with thread count information
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(visual, f"Warp: {warp_count}", (10, 30), font, 1, (0, 255, 0), 2)
        cv2.putText(visual, f"Weft: {weft_count}", (10, 70), font, 1, (0, 0, 255), 2)
        cv2.putText(visual, f"Total: {warp_count + weft_count}", (10, 110), font, 1, (255, 0, 0), 2)
        
        # Encode the visualization as base64 string
        _, buffer = cv2.imencode('.jpg', visual)
        visual_b64 = base64.b64encode(buffer).decode('utf-8')
        
        return visual_b64
