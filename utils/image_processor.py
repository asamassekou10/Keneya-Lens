"""
Medical Image Processing Utilities
Supports skin lesion analysis and other medical image types
"""
import io
from typing import Dict, Optional, Tuple
from PIL import Image
import base64
import logging

logger = logging.getLogger(__name__)


def validate_image(image_data: bytes, max_size_mb: int = 10) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded image.
    
    Args:
        image_data: Image file bytes
        max_size_mb: Maximum file size in MB
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check file size
        size_mb = len(image_data) / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"Image size ({size_mb:.2f}MB) exceeds maximum ({max_size_mb}MB)"
        
        # Try to open image
        image = Image.open(io.BytesIO(image_data))
        image.verify()
        
        # Check format
        if image.format not in ['JPEG', 'PNG', 'JPG']:
            return False, f"Unsupported image format: {image.format}. Supported: JPEG, PNG"
        
        # Check dimensions
        width, height = image.size
        if width < 64 or height < 64:
            return False, "Image dimensions too small (minimum 64x64)"
        if width > 4096 or height > 4096:
            return False, "Image dimensions too large (maximum 4096x4096)"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False, f"Invalid image file: {str(e)}"


def preprocess_image(image_data: bytes, target_size: Tuple[int, int] = (224, 224)) -> Optional[Image.Image]:
    """
    Preprocess image for model input.
    
    Args:
        image_data: Image file bytes
        target_size: Target size for resizing
        
    Returns:
        Preprocessed PIL Image or None if failed
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize maintaining aspect ratio
        image.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # Create a new image with target size and paste centered
        new_image = Image.new('RGB', target_size, (255, 255, 255))
        offset = ((target_size[0] - image.size[0]) // 2, (target_size[1] - image.size[1]) // 2)
        new_image.paste(image, offset)
        
        return new_image
        
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}")
        return None


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def analyze_image_metadata(image_data: bytes) -> Dict:
    """
    Extract metadata from medical image.
    
    Args:
        image_data: Image file bytes
        
    Returns:
        Dictionary with image metadata
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        
        metadata = {
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
            'width': image.width,
            'height': image.height,
            'has_transparency': image.mode in ('RGBA', 'LA', 'P')
        }
        
        # Try to extract EXIF data if available
        if hasattr(image, '_getexif') and image._getexif():
            metadata['has_exif'] = True
        
        return metadata
        
    except Exception as e:
        logger.error(f"Metadata extraction failed: {e}")
        return {'error': str(e)}


def create_image_description_prompt(image_path: Optional[str] = None, 
                                    image_data: Optional[bytes] = None,
                                    image_type: str = "skin lesion") -> str:
    """
    Create a prompt for describing a medical image.
    
    Args:
        image_path: Path to image file
        image_data: Image file bytes
        image_type: Type of medical image (skin lesion, xray, etc.)
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""A medical image has been uploaded for analysis. The image appears to be a {image_type}.

Please analyze this image and provide:
1. Visual description of what you observe
2. Notable features or characteristics
3. Any concerning patterns or signs
4. Recommendations for further evaluation

Note: This analysis is for educational purposes only and should not replace professional medical evaluation."""
    
    return prompt
