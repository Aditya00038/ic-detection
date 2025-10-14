"""
IC Detection Script using YOLOv8
Author: Your Name
Description: Detect ICs in images using trained YOLOv8 model
"""

import os
import cv2
import yaml
import argparse
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ICDetector:
    """YOLOv8 IC Detector"""
    
    def __init__(self, model_path='models/best.pt', config_path='config/config.yaml'):
        """
        Initialize detector
        
        Args:
            model_path: Path to trained model
            config_path: Path to configuration file
        """
        self.model_path = model_path
        self.config = self.load_config(config_path)
        self.model = self.load_model()
        
        # Detection parameters
        self.conf_threshold = self.config['detection']['confidence_threshold']
        self.iou_threshold = self.config['detection']['iou_threshold']
        self.max_detections = self.config['detection']['max_detections']
        
        # Output settings
        self.output_dir = Path(self.config['output']['output_dir'])
        self.setup_output_dirs()
        
    def load_config(self, config_path):
        """Load configuration"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"✓ Config loaded from {config_path}")
            return config
        except Exception as e:
            logger.warning(f"⚠ Could not load config: {e}. Using defaults.")
            return self.get_default_config()
    
    def get_default_config(self):
        """Get default configuration"""
        return {
            'detection': {
                'confidence_threshold': 0.5,
                'iou_threshold': 0.45,
                'max_detections': 10
            },
            'output': {
                'output_dir': 'results',
                'save_images': True,
                'save_crops': True,
                'save_reports': True,
                'box_thickness': 2,
                'box_color': [0, 255, 0],
                'text_size': 0.6,
                'text_color': [255, 255, 255]
            }
        }
    
    def setup_output_dirs(self):
        """Create output directories"""
        dirs = [
            self.output_dir,
            self.output_dir / 'images',
            self.output_dir / 'crops',
            self.output_dir / 'reports'
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def load_model(self):
        """Load YOLO model"""
        try:
            model = YOLO(self.model_path)
            logger.info(f"✓ Model loaded: {self.model_path}")
            return model
        except Exception as e:
            logger.error(f"✗ Error loading model: {e}")
            raise
    
    def detect(self, image_path, save_output=True):
        """
        Detect ICs in image
        
        Args:
            image_path: Path to input image
            save_output: Whether to save results
            
        Returns:
            dict: Detection results
        """
        try:
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                logger.error(f"✗ Could not read image: {image_path}")
                return None
            
            # Run detection
            results = self.model.predict(
                source=image,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                max_det=self.max_detections,
                verbose=False
            )[0]
            
            # Process results
            detections = self.process_results(results, image)
            
            # Save outputs
            if save_output:
                self.save_results(image, detections, Path(image_path).stem)
            
            logger.info(f"✓ Detected {len(detections)} IC(s) in {Path(image_path).name}")
            
            return detections
            
        except Exception as e:
            logger.error(f"✗ Detection error: {e}")
            return None
    
    def process_results(self, results, image):
        """
        Process YOLO results
        
        Args:
            results: YOLO detection results
            image: Input image
            
        Returns:
            list: Processed detections
        """
        detections = []
        
        boxes = results.boxes
        if boxes is None or len(boxes) == 0:
            return detections
        
        for i, box in enumerate(boxes):
            # Extract box data
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            
            # Get class name
            class_name = results.names[cls] if hasattr(results, 'names') else f"Class_{cls}"
            
            detection = {
                'id': i,
                'class': class_name,
                'class_id': cls,
                'confidence': conf,
                'bbox': {
                    'x1': int(x1),
                    'y1': int(y1),
                    'x2': int(x2),
                    'y2': int(y2),
                    'width': int(x2 - x1),
                    'height': int(y2 - y1)
                }
            }
            
            # Calculate center
            detection['bbox']['center_x'] = int((x1 + x2) / 2)
            detection['bbox']['center_y'] = int((y1 + y2) / 2)
            
            # Extract quality metrics if enabled
            if self.config.get('quality_metrics', {}).get('enabled', False):
                crop = image[int(y1):int(y2), int(x1):int(x2)]
                detection['quality'] = self.calculate_quality_metrics(crop)
            
            detections.append(detection)
        
        return detections
    
    def calculate_quality_metrics(self, image_crop):
        """Calculate quality metrics for detected IC"""
        if image_crop.size == 0:
            return {}
        
        metrics = {}
        
        # Blur detection (Laplacian variance)
        gray = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        metrics['blur_score'] = float(blur_score)
        metrics['is_blurry'] = blur_score < 100
        
        # Brightness
        brightness = np.mean(gray)
        metrics['brightness'] = float(brightness)
        
        # Contrast
        contrast = gray.std()
        metrics['contrast'] = float(contrast)
        
        # Sharpness (using gradient magnitude)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sharpness = np.sqrt(sobelx**2 + sobely**2).mean()
        metrics['sharpness'] = float(sharpness)
        
        return metrics
    
    def draw_detections(self, image, detections):
        """
        Draw bounding boxes on image
        
        Args:
            image: Input image
            detections: List of detections
            
        Returns:
            np.ndarray: Annotated image
        """
        annotated = image.copy()
        
        box_thickness = self.config['output'].get('box_thickness', 2)
        box_color = tuple(self.config['output'].get('box_color', [0, 255, 0]))
        text_size = self.config['output'].get('text_size', 0.6)
        text_color = tuple(self.config['output'].get('text_color', [255, 255, 255]))
        
        for det in detections:
            bbox = det['bbox']
            x1, y1 = bbox['x1'], bbox['y1']
            x2, y2 = bbox['x2'], bbox['y2']
            
            # Draw rectangle
            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, box_thickness)
            
            # Create label
            label = f"{det['class']}: {det['confidence']:.2f}"
            
            # Draw label background
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, text_size, 1)
            cv2.rectangle(annotated, (x1, y1 - text_h - 10), (x1 + text_w, y1), box_color, -1)
            
            # Draw label text
            cv2.putText(annotated, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, text_size, text_color, 1)
        
        return annotated
    
    def save_results(self, image, detections, filename):
        """
        Save detection results
        
        Args:
            image: Input image
            detections: List of detections
            filename: Output filename (without extension)
        """
        # Save annotated image
        if self.config['output'].get('save_images', True):
            annotated = self.draw_detections(image, detections)
            output_path = self.output_dir / 'images' / f"{filename}_detected.jpg"
            cv2.imwrite(str(output_path), annotated)
        
        # Save crops
        if self.config['output'].get('save_crops', True):
            for i, det in enumerate(detections):
                bbox = det['bbox']
                crop = image[bbox['y1']:bbox['y2'], bbox['x1']:bbox['x2']]
                crop_path = self.output_dir / 'crops' / f"{filename}_crop_{i}_{det['class']}.jpg"
                cv2.imwrite(str(crop_path), crop)
        
        # Save report
        if self.config['output'].get('save_reports', True):
            report = {
                'filename': filename,
                'timestamp': datetime.now().isoformat(),
                'num_detections': len(detections),
                'detections': detections
            }
            report_path = self.output_dir / 'reports' / f"{filename}_report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
    
    def detect_batch(self, image_dir, pattern='*.jpg'):
        """
        Detect ICs in multiple images
        
        Args:
            image_dir: Directory containing images
            pattern: File pattern (e.g., '*.jpg', '*.png')
            
        Returns:
            dict: Results for all images
        """
        image_dir = Path(image_dir)
        image_files = list(image_dir.glob(pattern))
        
        if not image_files:
            logger.warning(f"⚠ No images found in {image_dir} with pattern {pattern}")
            return {}
        
        logger.info(f"Processing {len(image_files)} images...")
        
        all_results = {}
        for img_path in image_files:
            detections = self.detect(img_path)
            all_results[img_path.name] = detections
        
        # Save summary report
        summary = {
            'total_images': len(image_files),
            'total_detections': sum(len(d) for d in all_results.values() if d),
            'results': all_results,
            'timestamp': datetime.now().isoformat()
        }
        
        summary_path = self.output_dir / 'reports' / 'batch_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"✓ Batch processing complete. Summary saved to {summary_path}")
        
        return all_results


def main():
    """Main detection function"""
    parser = argparse.ArgumentParser(description='Detect ICs using YOLOv8')
    
    parser.add_argument('--source', type=str, required=True,
                      help='Image file, directory, or video')
    parser.add_argument('--weights', type=str, default='models/best.pt',
                      help='Path to model weights')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                      help='Path to config file')
    parser.add_argument('--conf', type=float, default=None,
                      help='Confidence threshold')
    parser.add_argument('--iou', type=float, default=None,
                      help='IoU threshold')
    parser.add_argument('--output', type=str, default='results',
                      help='Output directory')
    parser.add_argument('--show', action='store_true',
                      help='Display results')
    parser.add_argument('--save', action='store_true', default=True,
                      help='Save results')
    
    args = parser.parse_args()
    
    # Initialize detector
    detector = ICDetector(model_path=args.weights, config_path=args.config)
    
    # Override config with CLI args
    if args.conf:
        detector.conf_threshold = args.conf
    if args.iou:
        detector.iou_threshold = args.iou
    if args.output:
        detector.output_dir = Path(args.output)
        detector.setup_output_dirs()
    
    # Detect
    source_path = Path(args.source)
    
    if source_path.is_file():
        # Single image
        logger.info(f"Processing single image: {source_path}")
        detections = detector.detect(source_path, save_output=args.save)
        
        if args.show and detections:
            image = cv2.imread(str(source_path))
            annotated = detector.draw_detections(image, detections)
            cv2.imshow('Detection Results', annotated)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
    elif source_path.is_dir():
        # Batch processing
        logger.info(f"Processing directory: {source_path}")
        patterns = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
        
        for pattern in patterns:
            detector.detect_batch(source_path, pattern)
    
    else:
        logger.error(f"✗ Invalid source: {source_path}")


if __name__ == '__main__':
    main()
