"""
Real-time IC Detection using Webcam
Author: Your Name
Description: Real-time IC detection from webcam feed using YOLOv8
"""

import cv2
import yaml
import argparse
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebcamICDetector:
    """Real-time IC Detector for Webcam"""
    
    def __init__(self, model_path='models/best.pt', config_path='config/config.yaml'):
        """
        Initialize webcam detector
        
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
        
        # Webcam settings
        self.camera_id = self.config['webcam'].get('camera_id', 0)
        self.resolution = self.config['webcam'].get('resolution', [1280, 720])
        self.target_fps = self.config['webcam'].get('fps', 30)
        self.show_fps = self.config['webcam'].get('show_fps', True)
        
        # Video capture
        self.cap = None
        
        # FPS calculation
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
    
    def load_config(self, config_path):
        """Load configuration"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except:
            return self.get_default_config()
    
    def get_default_config(self):
        """Get default configuration"""
        return {
            'detection': {
                'confidence_threshold': 0.5,
                'iou_threshold': 0.45
            },
            'webcam': {
                'camera_id': 0,
                'resolution': [1280, 720],
                'fps': 30,
                'show_fps': True
            },
            'output': {
                'box_thickness': 2,
                'box_color': [0, 255, 0],
                'text_size': 0.8,
                'text_color': [255, 255, 255]
            }
        }
    
    def load_model(self):
        """Load YOLO model"""
        try:
            model = YOLO(self.model_path)
            logger.info(f"✓ Model loaded: {self.model_path}")
            return model
        except Exception as e:
            logger.error(f"✗ Error loading model: {e}")
            raise
    
    def initialize_camera(self):
        """Initialize video capture"""
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {self.camera_id}")
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        # Get actual resolution
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        logger.info(f"✓ Camera initialized: {width}x{height} @ {self.target_fps} FPS")
        logger.info(f"  Camera ID: {self.camera_id}")
    
    def calculate_fps(self):
        """Calculate current FPS"""
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        
        if elapsed_time > 1.0:  # Update every second
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()
    
    def draw_detections(self, frame, results):
        """
        Draw bounding boxes on frame
        
        Args:
            frame: Input frame
            results: YOLO detection results
            
        Returns:
            np.ndarray: Annotated frame
        """
        boxes = results.boxes
        if boxes is None or len(boxes) == 0:
            return frame
        
        # Output config
        box_thickness = self.config['output'].get('box_thickness', 2)
        box_color = tuple(self.config['output'].get('box_color', [0, 255, 0]))
        text_size = self.config['output'].get('text_size', 0.8)
        text_color = tuple(self.config['output'].get('text_color', [255, 255, 255]))
        
        for box in boxes:
            # Extract box data
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            
            # Get class name
            class_name = results.names[cls] if hasattr(results, 'names') else f"IC"
            
            # Draw rectangle
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), 
                         box_color, box_thickness)
            
            # Create label
            label = f"{class_name}: {conf:.2f}"
            
            # Draw label background
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 
                                                   text_size, 2)
            cv2.rectangle(frame, (int(x1), int(y1) - text_h - 10), 
                         (int(x1) + text_w, int(y1)), box_color, -1)
            
            # Draw label text
            cv2.putText(frame, label, (int(x1), int(y1) - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, text_size, text_color, 2)
        
        return frame
    
    def draw_info_panel(self, frame, num_detections):
        """
        Draw information panel on frame
        
        Args:
            frame: Input frame
            num_detections: Number of detections
            
        Returns:
            np.ndarray: Frame with info panel
        """
        h, w = frame.shape[:2]
        
        # Draw semi-transparent panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Draw text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_color = (255, 255, 255)
        
        # FPS
        if self.show_fps:
            cv2.putText(frame, f"FPS: {self.fps:.1f}", (20, 40), 
                       font, 0.7, text_color, 2)
        
        # Resolution
        cv2.putText(frame, f"Resolution: {w}x{h}", (20, 70), 
                   font, 0.6, text_color, 1)
        
        # Detections
        color = (0, 255, 0) if num_detections > 0 else (128, 128, 128)
        cv2.putText(frame, f"Detections: {num_detections}", (20, 100), 
                   font, 0.6, color, 2)
        
        return frame
    
    def run(self, save_video=False, output_path='output.mp4'):
        """
        Run real-time detection
        
        Args:
            save_video: Whether to save video
            output_path: Output video path
        """
        try:
            self.initialize_camera()
            
            # Video writer
            video_writer = None
            if save_video:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(
                    output_path,
                    fourcc,
                    self.target_fps,
                    (self.resolution[0], self.resolution[1])
                )
            
            logger.info("🎥 Starting webcam detection...")
            logger.info("Press 'q' to quit, 's' to save screenshot")
            
            screenshot_count = 0
            
            while True:
                # Read frame
                ret, frame = self.cap.read()
                if not ret:
                    logger.error("Failed to read frame")
                    break
                
                # Calculate FPS
                self.calculate_fps()
                
                # Run detection
                results = self.model.predict(
                    source=frame,
                    conf=self.conf_threshold,
                    iou=self.iou_threshold,
                    verbose=False
                )[0]
                
                # Draw detections
                frame = self.draw_detections(frame, results)
                
                # Draw info panel
                num_detections = len(results.boxes) if results.boxes is not None else 0
                frame = self.draw_info_panel(frame, num_detections)
                
                # Save video frame
                if save_video and video_writer:
                    video_writer.write(frame)
                
                # Display
                cv2.imshow('IC Detection - Real-time', frame)
                
                # Handle keypresses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    logger.info("Quit requested")
                    break
                elif key == ord('s'):
                    # Save screenshot
                    screenshot_path = f'screenshot_{screenshot_count:04d}.jpg'
                    cv2.imwrite(screenshot_path, frame)
                    logger.info(f"✓ Screenshot saved: {screenshot_path}")
                    screenshot_count += 1
                elif key == ord('c'):
                    # Toggle confidence threshold
                    self.conf_threshold = 0.3 if self.conf_threshold == 0.5 else 0.5
                    logger.info(f"Confidence threshold: {self.conf_threshold}")
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        
        except Exception as e:
            logger.error(f"Error: {e}")
        
        finally:
            # Cleanup
            if self.cap:
                self.cap.release()
            if video_writer:
                video_writer.release()
            cv2.destroyAllWindows()
            logger.info("✓ Webcam detection stopped")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Real-time IC Detection from Webcam')
    
    parser.add_argument('--weights', type=str, default='models/best.pt',
                      help='Path to model weights')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                      help='Path to config file')
    parser.add_argument('--camera', type=int, default=0,
                      help='Camera ID')
    parser.add_argument('--conf', type=float, default=0.5,
                      help='Confidence threshold')
    parser.add_argument('--resolution', type=int, nargs=2, default=[1280, 720],
                      help='Camera resolution (width height)')
    parser.add_argument('--fps', type=int, default=30,
                      help='Target FPS')
    parser.add_argument('--save-video', action='store_true',
                      help='Save video output')
    parser.add_argument('--output', type=str, default='output.mp4',
                      help='Output video path')
    parser.add_argument('--show-fps', action='store_true', default=True,
                      help='Show FPS counter')
    
    args = parser.parse_args()
    
    # Initialize detector
    detector = WebcamICDetector(
        model_path=args.weights,
        config_path=args.config
    )
    
    # Override config with CLI args
    detector.camera_id = args.camera
    detector.conf_threshold = args.conf
    detector.resolution = args.resolution
    detector.target_fps = args.fps
    detector.show_fps = args.show_fps
    
    # Run detection
    detector.run(save_video=args.save_video, output_path=args.output)


if __name__ == '__main__':
    main()
