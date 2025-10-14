"""
STRICT IC-ONLY DETECTOR
Only detects electronic IC chips, nothing else
No menu, just runs directly
"""

import cv2
import numpy as np
from ultralytics import YOLO
import argparse
import sys
from pathlib import Path

class StrictICDetector:
    """Ultra-strict IC-only detection"""
    
    def __init__(self, model_path='yolov8s.pt', confidence=0.5):
        print("🔧 Loading Strict IC-Only Detector...")
        self.model = YOLO(model_path)
        self.confidence = confidence
        print(f"✓ Model loaded (confidence: {confidence})")
    
    def is_electronic_ic(self, roi, width, height):
        """
        ULTRA-STRICT IC verification
        Must pass ALL checks to be considered an IC
        """
        # Size checks - ICs have specific size range
        if width < 40 or height < 40:
            return False, "Too small"
        if width > 500 or height > 500:
            return False, "Too large"
        
        # Aspect ratio - ICs are rectangular
        aspect_ratio = width / height
        if aspect_ratio < 0.4 or aspect_ratio > 2.5:
            return False, "Wrong aspect ratio"
        
        # Area check
        area = width * height
        if area < 1600 or area > 250000:
            return False, "Wrong area"
        
        if roi is None or roi.size == 0:
            return False, "No ROI"
        
        try:
            # Convert to grayscale
            if len(roi.shape) == 3:
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            else:
                gray = roi
            
            # 1. EDGE DETECTION - ICs have clear rectangular edges
            edges = cv2.Canny(gray, 50, 150)
            edge_ratio = np.count_nonzero(edges) / gray.size
            
            # ICs should have moderate edge density (rectangular outline)
            if edge_ratio < 0.03 or edge_ratio > 0.25:
                return False, f"Edge ratio: {edge_ratio:.3f}"
            
            # 2. CONTOUR ANALYSIS - ICs are rectangular
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) == 0:
                return False, "No contours"
            
            # Find largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            contour_area = cv2.contourArea(largest_contour)
            
            # Contour should cover significant portion of ROI
            if contour_area < (area * 0.3):
                return False, "Contour too small"
            
            # 3. CORNER DETECTION - ICs have 4 corners (rectangle)
            perimeter = cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, 0.04 * perimeter, True)
            
            # Must have 4-6 corners (rectangular shape)
            if len(approx) < 4 or len(approx) > 6:
                return False, f"Corners: {len(approx)}"
            
            # 4. RECTANGULARITY - Check if shape is rectangular
            x, y, w, h = cv2.boundingRect(largest_contour)
            rect_area = w * h
            extent = contour_area / rect_area if rect_area > 0 else 0
            
            # ICs are very rectangular (extent close to 1.0)
            if extent < 0.7:
                return False, f"Rectangularity: {extent:.2f}"
            
            # 5. COLOR/TEXTURE CHECK - ICs are typically dark/black
            mean_color = np.mean(gray)
            std_color = np.std(gray)
            
            # ICs typically have uniform dark color
            # Reject very bright objects (like faces, white objects)
            if mean_color > 180:
                return False, f"Too bright: {mean_color:.0f}"
            
            # ICs have some texture variation (pins, text)
            if std_color < 10:
                return False, f"No texture: {std_color:.0f}"
            
            # 6. CHECK FOR PIN PATTERNS (advanced)
            # ICs often have parallel lines (pins)
            # Use Hough Line Transform to detect parallel lines
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 30, minLineLength=10, maxLineGap=5)
            
            if lines is None or len(lines) < 4:
                return False, "No pin patterns"
            
            # 7. REJECT FACES - Check for circular features (eyes)
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                      param1=50, param2=30, minRadius=5, maxRadius=30)
            
            if circles is not None and len(circles[0]) >= 2:
                return False, "Face/circular features detected"
            
            # ALL CHECKS PASSED - This is likely an IC!
            return True, "IC verified"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def detect_webcam(self, camera_id=0):
        """Webcam detection with strict IC-only filtering"""
        print(f"\n{'='*60}")
        print(f"📹 STRICT IC-ONLY WEBCAM DETECTION")
        print(f"{'='*60}")
        print(f"🎥 Opening camera {camera_id}...")
        
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print(f"❌ ERROR: Could not open camera {camera_id}")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print(f"✓ Camera opened")
        print(f"\n⌨️  Controls:")
        print(f"  'q' - Quit")
        print(f"  's' - Save screenshot")
        print(f"  '+' - Increase confidence")
        print(f"  '-' - Decrease confidence")
        print(f"{'='*60}\n")
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Run detection every frame
                results = self.model(frame, conf=self.confidence, verbose=False)[0]
                
                ic_count = 0
                annotated = frame.copy()
                debug_info = []
                
                if results.boxes is not None:
                    for idx, box in enumerate(results.boxes):
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0])
                        
                        x1_int, y1_int = max(0, int(x1)), max(0, int(y1))
                        x2_int, y2_int = min(frame.shape[1], int(x2)), min(frame.shape[0], int(y2))
                        
                        width, height = x2_int - x1_int, y2_int - y1_int
                        roi = frame[y1_int:y2_int, x1_int:x2_int]
                        
                        # STRICT IC CHECK
                        is_ic, reason = self.is_electronic_ic(roi, width, height)
                        
                        if is_ic:
                            ic_count += 1
                            # Draw GREEN box for IC
                            cv2.rectangle(annotated, (x1_int, y1_int), (x2_int, y2_int), (0, 255, 0), 3)
                            label = f"IC CHIP #{ic_count}"
                            cv2.putText(annotated, label, (x1_int, y1_int - 10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            debug_info.append(f"✓ IC #{ic_count}: {width}x{height}px")
                        else:
                            # Draw RED X for rejected objects
                            if frame_count % 10 == 0:  # Show rejection reason occasionally
                                cv2.rectangle(annotated, (x1_int, y1_int), (x2_int, y2_int), (0, 0, 255), 1)
                                cv2.putText(annotated, f"X {reason}", (x1_int, y1_int - 10),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                
                # Display status
                status_y = 30
                cv2.putText(annotated, f"Confidence: {self.confidence:.2f}", (10, status_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                status_y += 30
                if ic_count == 0:
                    cv2.putText(annotated, "NO IC DETECTED - IC NOT PRESENT", (10, status_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(annotated, f"IC CHIPS FOUND: {ic_count}", (10, status_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('IC-ONLY Detection (Strict Mode) - Press Q to quit', annotated)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    filename = f"ic_strict_{ic_count}_chips.jpg"
                    cv2.imwrite(filename, annotated)
                    print(f"📸 Saved: {filename}")
                elif key == ord('+'):
                    self.confidence = min(0.9, self.confidence + 0.05)
                    print(f"📊 Confidence: {self.confidence:.2f}")
                elif key == ord('-'):
                    self.confidence = max(0.1, self.confidence - 0.05)
                    print(f"📊 Confidence: {self.confidence:.2f}")
        
        except KeyboardInterrupt:
            print("\n⚠ Stopped by user")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("✓ Camera closed")
    
    def detect_image(self, image_path):
        """Image detection with strict IC-only filtering"""
        print(f"\n{'='*60}")
        print(f"📸 STRICT IC-ONLY IMAGE DETECTION")
        print(f"{'='*60}")
        print(f"📂 File: {Path(image_path).name}")
        
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"❌ ERROR: Could not read image!")
            return
        
        print(f"✓ Image loaded: {image.shape[1]}x{image.shape[0]} pixels")
        print(f"🔍 Analyzing (strict IC-only mode)...")
        
        results = self.model(image, conf=self.confidence, verbose=False)[0]
        
        ic_count = 0
        annotated = image.copy()
        
        if results.boxes is not None:
            print(f"\n📊 Found {len(results.boxes)} potential objects")
            print(f"🔬 Applying strict IC verification...\n")
            
            for idx, box in enumerate(results.boxes):
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                
                x1_int, y1_int = max(0, int(x1)), max(0, int(y1))
                x2_int, y2_int = min(image.shape[1], int(x2)), min(image.shape[0], int(y2))
                
                width, height = x2_int - x1_int, y2_int - y1_int
                roi = image[y1_int:y2_int, x1_int:x2_int]
                
                # STRICT IC CHECK
                is_ic, reason = self.is_electronic_ic(roi, width, height)
                
                if is_ic:
                    ic_count += 1
                    cv2.rectangle(annotated, (x1_int, y1_int), (x2_int, y2_int), (0, 255, 0), 3)
                    label = f"IC CHIP #{ic_count} ({conf:.2f})"
                    cv2.putText(annotated, label, (x1_int, y1_int - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    print(f"  ✓ IC #{ic_count}: {width}x{height}px, conf: {conf:.2f}")
                else:
                    print(f"  ✗ Object {idx+1}: Rejected - {reason}")
        
        print(f"\n{'='*60}")
        if ic_count == 0:
            print("❌ NO IC CHIPS DETECTED!")
            print("❌ IC is not present in this image")
        else:
            print(f"✅ DETECTED {ic_count} IC CHIP(S)!")
        print(f"{'='*60}\n")
        
        # Show and save
        cv2.imshow('IC Detection Results - Press any key to close', annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        output_path = Path(image_path).parent / f"ic_detected_{Path(image_path).name}"
        cv2.imwrite(str(output_path), annotated)
        print(f"💾 Saved: {output_path.name}")


def main():
    parser = argparse.ArgumentParser(description='Strict IC-Only Detection')
    parser.add_argument('--mode', choices=['webcam', 'image'], default='webcam')
    parser.add_argument('--image', type=str, help='Image file path')
    parser.add_argument('--conf', type=float, default=0.5)
    parser.add_argument('--camera', type=int, default=0)
    
    args = parser.parse_args()
    
    detector = StrictICDetector(confidence=args.conf)
    
    if args.mode == 'webcam':
        detector.detect_webcam(args.camera)
    else:
        if not args.image:
            print("❌ ERROR: --image required for image mode")
            sys.exit(1)
        if not Path(args.image).exists():
            print(f"❌ ERROR: Image not found: {args.image}")
            sys.exit(1)
        detector.detect_image(args.image)


if __name__ == '__main__':
    main()
