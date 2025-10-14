"""
Image Preprocessing Utilities for IC Detection
"""

import cv2
import numpy as np
from typing import Tuple, Optional


class ImagePreprocessor:
    """Image preprocessing utilities"""
    
    @staticmethod
    def resize_image(image: np.ndarray, target_size: Tuple[int, int], 
                    maintain_aspect: bool = True) -> np.ndarray:
        """
        Resize image to target size
        
        Args:
            image: Input image
            target_size: (width, height)
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Resized image
        """
        if maintain_aspect:
            h, w = image.shape[:2]
            target_w, target_h = target_size
            
            # Calculate scaling factor
            scale = min(target_w / w, target_h / h)
            new_w, new_h = int(w * scale), int(h * scale)
            
            # Resize
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            
            # Create padded image
            result = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            y_offset = (target_h - new_h) // 2
            x_offset = (target_w - new_w) // 2
            result[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
            
            return result
        else:
            return cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)
    
    @staticmethod
    def denoise(image: np.ndarray, method: str = 'fastNlMeans') -> np.ndarray:
        """
        Remove noise from image
        
        Args:
            image: Input image
            method: Denoising method ('fastNlMeans', 'bilateral', 'gaussian')
            
        Returns:
            Denoised image
        """
        if method == 'fastNlMeans':
            if len(image.shape) == 3:
                return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
            else:
                return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        
        elif method == 'bilateral':
            return cv2.bilateralFilter(image, 9, 75, 75)
        
        elif method == 'gaussian':
            return cv2.GaussianBlur(image, (5, 5), 0)
        
        return image
    
    @staticmethod
    def sharpen(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """
        Sharpen image
        
        Args:
            image: Input image
            kernel_size: Kernel size for unsharp mask
            
        Returns:
            Sharpened image
        """
        # Create sharpening kernel
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        
        return cv2.filter2D(image, -1, kernel)
    
    @staticmethod
    def enhance_contrast(image: np.ndarray, method: str = 'clahe') -> np.ndarray:
        """
        Enhance image contrast
        
        Args:
            image: Input image
            method: Enhancement method ('clahe', 'histogram', 'adaptive')
            
        Returns:
            Contrast-enhanced image
        """
        if method == 'clahe':
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge and convert back
            lab = cv2.merge([l, a, b])
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        elif method == 'histogram':
            # Histogram equalization
            if len(image.shape) == 3:
                ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
                ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
                return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
            else:
                return cv2.equalizeHist(image)
        
        elif method == 'adaptive':
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
            return cv2.cvtColor(adaptive, cv2.COLOR_GRAY2BGR)
        
        return image
    
    @staticmethod
    def gamma_correction(image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
        """
        Apply gamma correction
        
        Args:
            image: Input image
            gamma: Gamma value (< 1 = darker, > 1 = brighter)
            
        Returns:
            Gamma-corrected image
        """
        inv_gamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** inv_gamma * 255
                         for i in range(256)]).astype("uint8")
        
        return cv2.LUT(image, table)
    
    @staticmethod
    def normalize(image: np.ndarray) -> np.ndarray:
        """
        Normalize image to [0, 1] range
        
        Args:
            image: Input image
            
        Returns:
            Normalized image
        """
        return image.astype(np.float32) / 255.0
    
    @staticmethod
    def enhance_image(image: np.ndarray,
                     resize: bool = False,
                     target_size: Tuple[int, int] = (640, 640),
                     denoise: bool = False,
                     sharpen: bool = False,
                     contrast: bool = False,
                     gamma: Optional[float] = None) -> np.ndarray:
        """
        Apply multiple enhancement techniques
        
        Args:
            image: Input image
            resize: Whether to resize
            target_size: Target size for resizing
            denoise: Whether to denoise
            sharpen: Whether to sharpen
            contrast: Whether to enhance contrast
            gamma: Gamma correction value (None = no correction)
            
        Returns:
            Enhanced image
        """
        result = image.copy()
        
        # Resize
        if resize:
            result = ImagePreprocessor.resize_image(result, target_size)
        
        # Denoise
        if denoise:
            result = ImagePreprocessor.denoise(result)
        
        # Enhance contrast
        if contrast:
            result = ImagePreprocessor.enhance_contrast(result)
        
        # Sharpen
        if sharpen:
            result = ImagePreprocessor.sharpen(result)
        
        # Gamma correction
        if gamma is not None:
            result = ImagePreprocessor.gamma_correction(result, gamma)
        
        return result
