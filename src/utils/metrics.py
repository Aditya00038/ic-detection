"""
Quality Metrics for IC Detection
"""

import cv2
import numpy as np
from typing import Dict, Tuple


class QualityMetrics:
    """Calculate image quality metrics"""
    
    @staticmethod
    def calculate_blur(image: np.ndarray) -> float:
        """
        Calculate blur score using Laplacian variance
        Lower score = more blurry
        
        Args:
            image: Input image
            
        Returns:
            Blur score (higher = sharper)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_score = laplacian.var()
        
        return float(blur_score)
    
    @staticmethod
    def calculate_brightness(image: np.ndarray) -> float:
        """
        Calculate average brightness
        
        Args:
            image: Input image
            
        Returns:
            Brightness value [0-255]
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        return float(np.mean(gray))
    
    @staticmethod
    def calculate_contrast(image: np.ndarray) -> float:
        """
        Calculate contrast (standard deviation)
        
        Args:
            image: Input image
            
        Returns:
            Contrast value
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        return float(np.std(gray))
    
    @staticmethod
    def calculate_sharpness(image: np.ndarray) -> float:
        """
        Calculate sharpness using gradient magnitude
        
        Args:
            image: Input image
            
        Returns:
            Sharpness score
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Sobel gradients
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Gradient magnitude
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        sharpness = magnitude.mean()
        
        return float(sharpness)
    
    @staticmethod
    def estimate_noise(image: np.ndarray) -> float:
        """
        Estimate image noise level
        
        Args:
            image: Input image
            
        Returns:
            Noise estimate
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Use Median Absolute Deviation (MAD) method
        h, w = gray.shape
        m = (h // 2) * (w // 2)
        
        # Get high-frequency components
        hh = cv2.resize(gray, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
        noise = np.median(np.abs(hh - np.median(hh)))
        
        return float(noise * 1.4826)
    
    @staticmethod
    def calculate_entropy(image: np.ndarray) -> float:
        """
        Calculate image entropy (information content)
        
        Args:
            image: Input image
            
        Returns:
            Entropy value
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist / hist.sum()
        
        # Remove zeros
        hist = hist[hist > 0]
        
        # Calculate entropy
        entropy = -np.sum(hist * np.log2(hist))
        
        return float(entropy)
    
    @staticmethod
    def check_overexposure(image: np.ndarray, threshold: float = 240) -> Tuple[bool, float]:
        """
        Check if image is overexposed
        
        Args:
            image: Input image
            threshold: Brightness threshold
            
        Returns:
            (is_overexposed, percentage_of_overexposed_pixels)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        overexposed = np.sum(gray > threshold)
        percentage = (overexposed / gray.size) * 100
        
        is_overexposed = percentage > 5  # More than 5% overexposed
        
        return is_overexposed, float(percentage)
    
    @staticmethod
    def check_underexposure(image: np.ndarray, threshold: float = 30) -> Tuple[bool, float]:
        """
        Check if image is underexposed
        
        Args:
            image: Input image
            threshold: Darkness threshold
            
        Returns:
            (is_underexposed, percentage_of_underexposed_pixels)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        underexposed = np.sum(gray < threshold)
        percentage = (underexposed / gray.size) * 100
        
        is_underexposed = percentage > 10  # More than 10% underexposed
        
        return is_underexposed, float(percentage)
    
    @staticmethod
    def calculate_all_metrics(image: np.ndarray) -> Dict[str, float]:
        """
        Calculate all quality metrics
        
        Args:
            image: Input image
            
        Returns:
            Dictionary of all metrics
        """
        metrics = {
            'blur_score': QualityMetrics.calculate_blur(image),
            'brightness': QualityMetrics.calculate_brightness(image),
            'contrast': QualityMetrics.calculate_contrast(image),
            'sharpness': QualityMetrics.calculate_sharpness(image),
            'noise': QualityMetrics.estimate_noise(image),
            'entropy': QualityMetrics.calculate_entropy(image)
        }
        
        # Check exposure
        is_overexposed, over_pct = QualityMetrics.check_overexposure(image)
        is_underexposed, under_pct = QualityMetrics.check_underexposure(image)
        
        metrics['is_overexposed'] = is_overexposed
        metrics['overexposure_percentage'] = over_pct
        metrics['is_underexposed'] = is_underexposed
        metrics['underexposure_percentage'] = under_pct
        
        # Quality assessment
        metrics['is_blurry'] = metrics['blur_score'] < 100
        metrics['has_high_noise'] = metrics['noise'] > 20
        metrics['has_low_contrast'] = metrics['contrast'] < 20
        
        # Overall quality score (0-100)
        quality_score = 0
        quality_score += min((metrics['blur_score'] / 500) * 30, 30)  # Blur (30 points)
        quality_score += min((metrics['sharpness'] / 50) * 20, 20)    # Sharpness (20 points)
        quality_score += min((metrics['contrast'] / 80) * 20, 20)     # Contrast (20 points)
        quality_score += min((metrics['entropy'] / 8) * 15, 15)       # Entropy (15 points)
        quality_score += 15 if not (is_overexposed or is_underexposed) else 5  # Exposure (15 points)
        
        metrics['overall_quality'] = float(quality_score)
        
        return metrics
    
    @staticmethod
    def is_good_quality(image: np.ndarray,
                       min_blur: float = 100,
                       min_brightness: float = 40,
                       max_brightness: float = 220,
                       min_contrast: float = 20) -> Tuple[bool, str]:
        """
        Check if image meets quality standards
        
        Args:
            image: Input image
            min_blur: Minimum blur score
            min_brightness: Minimum brightness
            max_brightness: Maximum brightness
            min_contrast: Minimum contrast
            
        Returns:
            (is_good_quality, reason_if_bad)
        """
        metrics = QualityMetrics.calculate_all_metrics(image)
        
        if metrics['blur_score'] < min_blur:
            return False, f"Image is too blurry (score: {metrics['blur_score']:.1f}, required: {min_blur})"
        
        if metrics['brightness'] < min_brightness:
            return False, f"Image is too dark (brightness: {metrics['brightness']:.1f}, required: {min_brightness})"
        
        if metrics['brightness'] > max_brightness:
            return False, f"Image is too bright (brightness: {metrics['brightness']:.1f}, max: {max_brightness})"
        
        if metrics['contrast'] < min_contrast:
            return False, f"Image has low contrast (contrast: {metrics['contrast']:.1f}, required: {min_contrast})"
        
        if metrics['is_overexposed']:
            return False, f"Image is overexposed ({metrics['overexposure_percentage']:.1f}% pixels overexposed)"
        
        if metrics['is_underexposed']:
            return False, f"Image is underexposed ({metrics['underexposure_percentage']:.1f}% pixels underexposed)"
        
        return True, "Image quality is acceptable"
