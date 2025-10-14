"""
Real-time IC Chip Detection with Webcam
Specialized for electronic IC chips with text recognition
"""

import cv2
import numpy as np
from ultralytics import YOLO
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

try:
    import pytesseract
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False
    print("⚠ pytesseract not installed. Text recognition will be limited.")


class ICWebcamDetector:
    """Real-time IC chip detection with webcam"""
    
    # IC manufacturer patterns (simplified)
    IC_PREFIXES = {
        'TI': 'TEXAS INSTRUMENTS',
        'LM': 'TEXAS INSTRUMENTS',
        'TL': 'TEXAS INSTRUMENTS',
        'TPS': 'TEXAS INSTRUMENTS',
        'AD': 'ANALOG DEVICES',
        'MAX': 'MAXIM',
        'LT': 'LINEAR TECH',
        'PIC': 'MICROCHIP',
        'AT': 'ATMEL/MICROCHIP',
        'STM': 'STM',
        'LPC': 'NXP',
        'IR': 'INFINEON',
        'MC': 'ONSEMI'
    }
    
    def __init__(self, camera_id=0, model_path='yolov8s.pt', confidence=0.3):
        """
        Initialize webcam IC detector
        
        Args:
            camera_id: Webcam ID (usually 0)
            model_path: Path to YOLO model
            confidence: Detection confidence threshold
        """
        print("🔧 Initializing IC Chip Webcam Detector...")
        
        # Load YOLO model
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.camera_id = camera_id
        
        # Detection settings
        self.show_confidence = True
        self.filter_ic_only = True
        self.frame_count = 0
        self.fps = 0
        
        # OCR status
        if OCR_AVAILABLE:
            try:
                pytesseract.get_tesseract_version()
                self.ocr_available = True
                print("✓ Tesseract OCR available")
            except:
                self.ocr_available = False
                print("⚠ Tesseract not properly configured")
        else:
            self.ocr_available = False
    
    def is_ic_shape(self, width, height, roi=None):
        """Check if detection has IC-like rectangular shape - STRICT filtering"""
        # ICs must be a reasonable size (not too small, not too large)
        if width < 50 or height < 50:  # Too small
            return False
        
        if width > 400 or height > 400:  # Too large (probably not an IC)
            return False
        
        aspect_ratio = width / height
        
        # ICs are typically rectangular with specific ratios
        # Most ICs are either square-ish (1:1) or moderately rectangular (up to 2:1 or 1:2)
        # Reject very elongated objects
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:
            return False
        
        # Additional check: ICs should have reasonable area
        area = width * height
        if area < 2500 or area > 160000:  # Filter by area (50x50 to 400x400)
            return False
        
        # If we have the ROI, check if it looks rectangular with edges
        if roi is not None and roi.size > 0:
            try:
                # Convert to grayscale
                if len(roi.shape) == 3:
                    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                else:
                    gray = roi
                
                # Edge detection
                edges = cv2.Canny(gray, 50, 150)
                
                # Count edge pixels
                edge_pixel_count = np.count_nonzero(edges)
                total_pixels = gray.shape[0] * gray.shape[1]
                edge_ratio = edge_pixel_count / total_pixels
                
                # ICs should have clear rectangular edges (but not too many edges)
                # Too many edges = complex object (not a simple IC chip)
                if edge_ratio < 0.02 or edge_ratio > 0.3:
                    return False
                
                # Check for rectangular contours
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if len(contours) > 0:
                    # Find the largest contour
                    largest_contour = max(contours, key=cv2.contourArea)
                    
                    # Approximate the contour to a polygon
                    epsilon = 0.04 * cv2.arcLength(largest_contour, True)
                    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
                    
                    # ICs should have 4 corners (rectangular)
                    # Allow 4-8 points (some ICs might have slightly irregular edges)
                    if len(approx) < 4 or len(approx) > 8:
                        return False
            except:
                pass  # If edge detection fails, rely on other checks
        
        return True
    
    def simple_ocr(self, roi):
        """Simple OCR for IC text (basic version without Tesseract)"""
        if self.ocr_available:
            try:
                # Preprocess
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, None, fx=2, fy=2)
                _, binary = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # OCR
                text = pytesseract.image_to_string(binary, config='--psm 6')
                return text.strip().upper()
            except:
                pass
        return ""
    
    def identify_ic(self, text):
        """Identify IC from text"""
        if not text:
            return None, None
        
        # Check known prefixes
        for prefix, manufacturer in self.IC_PREFIXES.items():
            if prefix in text:
                # Try to extract part number
                words = text.split()
                for word in words:
                    if prefix in word and len(word) > 2:
                        return manufacturer, word
        
        # Generic detection
        if len(text) > 3:
            return "UNKNOWN IC", text[:15]
        
        return None, None
    
    def draw_detection(self, image, box, label, confidence, color=(0, 255, 0)):
        """Draw detection box and label"""
        x1, y1, x2, y2 = map(int, box)
        
        # Draw box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
        
        # Prepare text
        if self.show_confidence:
            text = f"{label} ({confidence:.2f})"
        else:
            text = label
        
        # Calculate text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Draw background
        cv2.rectangle(image, 
                     (x1, y1 - text_height - 10),
                     (x1 + text_width + 10, y1),
                     color, -1)
        
        # Draw text
        cv2.putText(image, text, (x1 + 5, y1 - 5),
                   font, font_scale, (255, 255, 255), thickness)
    
    def draw_no_ic_warning(self, image):
        """Draw warning when no IC is detected"""
        height, width = image.shape[:2]
        
        # Semi-transparent overlay
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (width, 100), (0, 0, 255), -1)
        cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)
        
        # Warning text
        warning = "NO IC DETECTED!"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 3
        
        (text_width, text_height), _ = cv2.getTextSize(warning, font, font_scale, thickness)
        x = (width - text_width) // 2
        y = 60
        
        cv2.putText(image, warning, (x, y), font, font_scale, (0, 0, 255), thickness)
        
        # Error message
        error_msg = "IC is not present"
        cv2.putText(image, error_msg, (x - 50, y + 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    def process_frame(self, frame):
        """Process single frame"""
        # Run detection
        results = self.model(frame, conf=self.confidence, verbose=False)[0]
        
        ic_count = 0
        annotated = frame.copy()
        
        # Process detections
        if results.boxes is not None and len(results.boxes) > 0:
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                
                # Extract region first
                x1_int = max(0, int(x1))
                y1_int = max(0, int(y1))
                x2_int = min(frame.shape[1], int(x2))
                y2_int = min(frame.shape[0], int(y2))
                roi = frame[y1_int:y2_int, x1_int:x2_int]
                
                # Check IC shape with ROI for edge detection
                width, height = x2 - x1, y2 - y1
                if self.filter_ic_only and not self.is_ic_shape(width, height, roi):
                    continue
                
                # Try OCR
                text = self.simple_ocr(roi)
                manufacturer, part_number = self.identify_ic(text)
                
                # Create label
                if manufacturer:
                    label = f"{manufacturer}"
                    if part_number:
                        label = f"{manufacturer}: {part_number}"
                    color = (0, 255, 0)  # Green for identified
                else:
                    label = "IC CHIP"
                    color = (255, 165, 0)  # Orange for unidentified
                
                # Draw detection
                self.draw_detection(annotated, [x1, y1, x2, y2], label, conf, color)
                ic_count += 1
        
        return annotated, ic_count
    
    def draw_info_panel(self, image, ic_count):
        """Draw information panel"""
        height, width = image.shape[:2]
        
        # Background for info
        cv2.rectangle(image, (10, 10), (400, 110), (0, 0, 0), -1)
        cv2.rectangle(image, (10, 10), (400, 110), (0, 255, 0), 2)
        
        # Info text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, f"IC Chips Detected: {ic_count}", (20, 40),
                   font, 0.7, (0, 255, 0), 2)
        cv2.putText(image, f"FPS: {self.fps:.1f}", (20, 70),
                   font, 0.6, (255, 255, 255), 1)
        cv2.putText(image, f"Confidence: {self.confidence}", (20, 95),
                   font, 0.6, (255, 255, 255), 1)
    
    def run(self):
        """Run webcam detection"""
        print(f"\n📹 Opening camera {self.camera_id}...")
        cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("\n✅ IC Chip Detection Started!")
        print("\n⌨️  Keyboard Controls:")
        print("  'q' - Quit")
        print("  's' - Save screenshot")
        print("  'c' - Toggle confidence display")
        print("  'f' - Toggle IC filter")
        print(f"\n📊 OCR Status: {'✓ Enabled' if self.ocr_available else '✗ Disabled'}")
        print("\n🔍 Point camera at IC chips to detect and identify them!\n")
        
        # FPS calculation
        import time
        prev_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Error reading frame")
                break
            
            # Process frame
            result_frame, ic_count = self.process_frame(frame)
            
            # Calculate FPS
            curr_time = time.time()
            self.fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            
            # Draw info panel
            self.draw_info_panel(result_frame, ic_count)
            
            # Show warning if no IC detected
            if ic_count == 0:
                self.draw_no_ic_warning(result_frame)
            
            # Display
            cv2.imshow('IC Chip Detection - Webcam', result_frame)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n👋 Exiting...")
                break
            elif key == ord('s'):
                filename = f"ic_screenshot_{self.frame_count}.jpg"
                cv2.imwrite(filename, result_frame)
                print(f"📸 Screenshot saved: {filename}")
            elif key == ord('c'):
                self.show_confidence = not self.show_confidence
                print(f"Confidence display: {'ON' if self.show_confidence else 'OFF'}")
            elif key == ord('f'):
                self.filter_ic_only = not self.filter_ic_only
                print(f"IC filter: {'ON' if self.filter_ic_only else 'OFF'}")
            
            self.frame_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
        print("✓ Camera closed")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IC Chip Webcam Detection')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID (default: 0)')
    parser.add_argument('--model', type=str, default='yolov8s.pt', help='YOLO model')
    parser.add_argument('--conf', type=float, default=0.5, help='Confidence threshold (default: 0.5 for strict filtering)')
    
    args = parser.parse_args()
    
    # Run detector
    detector = ICWebcamDetector(
        camera_id=args.camera,
        model_path=args.model,
        confidence=args.conf
    )
    
    detector.run()


if __name__ == '__main__':
    main()
