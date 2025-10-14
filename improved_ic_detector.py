"""
IMPROVED IC Chip Detection System
Works with webcam AND phone images
Better detection for real-world conditions
"""

import cv2
import numpy as np
from ultralytics import YOLO
import argparse
from pathlib import Path
import time

class ImprovedICDetector:
    """Improved IC chip detector for webcam and images"""
    
    def __init__(self, model_path='yolov8s.pt', confidence=0.4):
        """Initialize detector with better defaults"""
        print("🔧 Loading Improved IC Chip Detector...")
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.ic_filter_enabled = True
        print(f"✓ Model loaded (confidence: {confidence})")
    
    def is_ic_chip(self, width, height, roi=None):
        """
        Improved IC detection - works better with phone images
        Less strict but still filters out obvious non-ICs
        """
        # Basic size check - more lenient for phone photos
        if width < 30 or height < 30:  # Allow smaller for distant shots
            return False
        
        if width > 600 or height > 600:  # Allow larger for close-ups
            return False
        
        # Aspect ratio - ICs are rectangular but allow more variation
        aspect_ratio = width / height
        if aspect_ratio < 0.3 or aspect_ratio > 3.5:  # More lenient
            return False
        
        # If ROI provided, check for rectangular features
        if roi is not None and roi.size > 100:
            try:
                # Convert to grayscale
                if len(roi.shape) == 3:
                    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                else:
                    gray = roi
                
                # Check for edges (ICs have clear rectangular edges)
                edges = cv2.Canny(gray, 30, 100)  # Lower thresholds for phone images
                edge_ratio = np.count_nonzero(edges) / gray.size
                
                # ICs should have some edges but not be entirely edges
                if edge_ratio < 0.01 or edge_ratio > 0.5:
                    return False
                
                # Look for rectangular shape
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if len(contours) > 0:
                    largest = max(contours, key=cv2.contourArea)
                    perimeter = cv2.arcLength(largest, True)
                    approx = cv2.approxPolyDP(largest, 0.04 * perimeter, True)
                    
                    # ICs typically have 4 corners (rectangle)
                    # Allow 4-10 points for irregular edges/lighting
                    if len(approx) < 4 or len(approx) > 10:
                        return False
                
            except Exception as e:
                # If analysis fails, allow it (phone images can be tricky)
                pass
        
        return True
    
    def enhance_image(self, image):
        """Enhance image quality for better detection (especially phone photos)"""
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def detect_from_image(self, image_path, show_result=True, save_result=True):
        """Detect ICs from image file (phone photos)"""
        print(f"\n{'='*60}")
        print(f"📸 DETECTING ICs FROM IMAGE")
        print(f"{'='*60}")
        print(f"📂 File: {Path(image_path).name}")
        
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"❌ ERROR: Could not read image!")
            return None, 0
        
        print(f"✓ Image loaded: {image.shape[1]}x{image.shape[0]} pixels")
        
        # Enhance image for better detection
        enhanced = self.enhance_image(image)
        
        print(f"🔍 Analyzing image...")
        
        # Run detection on enhanced image
        results = self.model(enhanced, conf=self.confidence, verbose=False)[0]
        
        ic_count = 0
        annotated = image.copy()
        
        if results.boxes is not None and len(results.boxes) > 0:
            print(f"📊 Found {len(results.boxes)} potential objects")
            
            for idx, box in enumerate(results.boxes):
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # Get ROI
                x1_int, y1_int = max(0, int(x1)), max(0, int(y1))
                x2_int, y2_int = min(image.shape[1], int(x2)), min(image.shape[0], int(y2))
                roi = image[y1_int:y2_int, x1_int:x2_int]
                
                # Check if this is an IC chip
                width, height = x2_int - x1_int, y2_int - y1_int
                
                if self.ic_filter_enabled and not self.is_ic_chip(width, height, roi):
                    print(f"  ⊘ Object {idx+1}: Filtered out (not IC-shaped)")
                    continue
                
                # Valid IC detected!
                ic_count += 1
                
                # Draw detection
                color = (0, 255, 0)  # Green for IC
                cv2.rectangle(annotated, (x1_int, y1_int), (x2_int, y2_int), color, 3)
                
                # Label
                label = f"IC CHIP #{ic_count} ({conf:.2f})"
                
                # Draw label background
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.8
                thickness = 2
                (tw, th), _ = cv2.getTextSize(label, font, font_scale, thickness)
                
                cv2.rectangle(annotated, (x1_int, y1_int - th - 10),
                             (x1_int + tw + 10, y1_int), color, -1)
                cv2.putText(annotated, label, (x1_int + 5, y1_int - 5),
                           font, font_scale, (255, 255, 255), thickness)
                
                print(f"  ✓ IC #{ic_count}: {width}x{height}px, confidence: {conf:.2f}")
        
        # Display results
        print(f"\n{'='*60}")
        if ic_count == 0:
            print("❌ NO IC CHIPS DETECTED!")
            print("❌ IC is not present in this image")
            print("\n💡 Tips for better detection:")
            print("  • Ensure good lighting")
            print("  • IC chip should be clearly visible")
            print("  • Get closer to the IC")
            print("  • Avoid shadows and reflections")
        else:
            print(f"✅ DETECTED {ic_count} IC CHIP(S)!")
        print(f"{'='*60}\n")
        
        # Show result
        if show_result:
            # Resize if too large
            max_display_size = 1200
            h, w = annotated.shape[:2]
            if max(h, w) > max_display_size:
                scale = max_display_size / max(h, w)
                new_w, new_h = int(w * scale), int(h * scale)
                display_img = cv2.resize(annotated, (new_w, new_h))
            else:
                display_img = annotated
            
            window_name = f"IC Detection Results - {ic_count} IC(s) found"
            cv2.imshow(window_name, display_img)
            print("📺 Press any key to close the window...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        # Save result
        if save_result:
            output_path = Path(image_path).parent / f"detected_{Path(image_path).name}"
            cv2.imwrite(str(output_path), annotated)
            print(f"💾 Saved result to: {output_path.name}")
        
        return annotated, ic_count
    
    def detect_from_webcam(self, camera_id=0):
        """Real-time IC detection from webcam"""
        print(f"\n{'='*60}")
        print(f"📹 WEBCAM IC DETECTION")
        print(f"{'='*60}")
        print(f"🎥 Opening camera {camera_id}...")
        
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"❌ ERROR: Could not open camera {camera_id}")
            return
        
        print(f"✓ Camera opened successfully")
        print(f"\n⌨️  Controls:")
        print(f"  'q' - Quit")
        print(f"  's' - Save screenshot")
        print(f"  'f' - Toggle IC filter (currently: {'ON' if self.ic_filter_enabled else 'OFF'})")
        print(f"  '+' - Increase confidence")
        print(f"  '-' - Decrease confidence")
        print(f"{'='*60}\n")
        
        frame_count = 0
        fps_start = time.time()
        fps = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Error reading frame")
                    break
                
                # Calculate FPS
                frame_count += 1
                if frame_count % 30 == 0:
                    fps = 30 / (time.time() - fps_start)
                    fps_start = time.time()
                
                # Enhance frame for better detection
                enhanced = self.enhance_image(frame)
                
                # Run detection
                results = self.model(enhanced, conf=self.confidence, verbose=False)[0]
                
                ic_count = 0
                annotated = frame.copy()
                
                # Process detections
                if results.boxes is not None:
                    for box in results.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0])
                        
                        x1_int, y1_int = max(0, int(x1)), max(0, int(y1))
                        x2_int, y2_int = min(frame.shape[1], int(x2)), min(frame.shape[0], int(y2))
                        roi = frame[y1_int:y2_int, x1_int:x2_int]
                        
                        width, height = x2_int - x1_int, y2_int - y1_int
                        
                        # Apply IC filter
                        if self.ic_filter_enabled and not self.is_ic_chip(width, height, roi):
                            continue
                        
                        ic_count += 1
                        
                        # Draw detection
                        color = (0, 255, 0)
                        cv2.rectangle(annotated, (x1_int, y1_int), (x2_int, y2_int), color, 2)
                        
                        label = f"IC #{ic_count}"
                        cv2.putText(annotated, label, (x1_int, y1_int - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Display status
                status_y = 30
                cv2.putText(annotated, f"FPS: {fps:.1f}", (10, status_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                status_y += 30
                cv2.putText(annotated, f"Confidence: {self.confidence:.2f}", (10, status_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                status_y += 30
                cv2.putText(annotated, f"IC Filter: {'ON' if self.ic_filter_enabled else 'OFF'}", 
                           (10, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Display IC count or "No IC"
                status_y += 30
                if ic_count == 0:
                    cv2.putText(annotated, "NO IC DETECTED", (10, status_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(annotated, f"ICs Found: {ic_count}", (10, status_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('IC Chip Detection - Press Q to quit', annotated)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n👋 Quitting...")
                    break
                elif key == ord('s'):
                    filename = f"ic_screenshot_{int(time.time())}.jpg"
                    cv2.imwrite(filename, annotated)
                    print(f"📸 Screenshot saved: {filename}")
                elif key == ord('f'):
                    self.ic_filter_enabled = not self.ic_filter_enabled
                    print(f"🔧 IC filter: {'ON' if self.ic_filter_enabled else 'OFF'}")
                elif key == ord('+') or key == ord('='):
                    self.confidence = min(0.9, self.confidence + 0.05)
                    print(f"📊 Confidence: {self.confidence:.2f}")
                elif key == ord('-') or key == ord('_'):
                    self.confidence = max(0.1, self.confidence - 0.05)
                    print(f"📊 Confidence: {self.confidence:.2f}")
        
        except KeyboardInterrupt:
            print("\n⚠ Interrupted by user")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("✓ Camera closed")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Improved IC Chip Detection')
    parser.add_argument('--mode', choices=['webcam', 'image'], default='webcam',
                       help='Detection mode')
    parser.add_argument('--image', type=str, help='Image file path (for image mode)')
    parser.add_argument('--conf', type=float, default=0.4,
                       help='Confidence threshold (0.0-1.0)')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera ID for webcam mode')
    
    args = parser.parse_args()
    
    # Create detector
    detector = ImprovedICDetector(confidence=args.conf)
    
    # Run appropriate mode
    if args.mode == 'webcam':
        detector.detect_from_webcam(args.camera)
    else:
        if not args.image:
            print("❌ ERROR: --image required for image mode")
            print("Example: python improved_ic_detector.py --mode image --image photo.jpg")
            return
        
        if not Path(args.image).exists():
            print(f"❌ ERROR: Image file not found: {args.image}")
            return
        
        detector.detect_from_image(args.image)


if __name__ == '__main__':
    main()
