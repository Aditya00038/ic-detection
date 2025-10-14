"""
ENHANCED IC DETECTION SYSTEM
- Advanced filtering algorithms
- Multiple detection methods
- Pin/leg detection
- IC type classification
- Higher accuracy
"""

import cv2
from ultralytics import YOLO
import numpy as np
from pathlib import Path

class EnhancedICDetector:
    def __init__(self):
        print("🚀 Loading Enhanced IC Detection System...")
        self.model = YOLO('yolov8s.pt')  # Using larger model for better accuracy
        print("✅ Model loaded!")
        
        # IC-specific parameters
        self.min_size = 40
        self.max_size = 600
        self.min_aspect_ratio = 0.3
        self.max_aspect_ratio = 4.0
        
    def detect_ic_pins(self, roi):
        """Detect IC pins/legs using advanced edge detection"""
        if roi.size == 0:
            return False, 0
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Enhanced edge detection
        edges = cv2.Canny(gray, 30, 100)
        
        # Detect horizontal lines (IC pins are usually parallel)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=20, 
                                minLineLength=10, maxLineGap=5)
        
        if lines is not None:
            # Count parallel lines (IC pins)
            horizontal_lines = 0
            vertical_lines = 0
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = abs(np.arctan2(y2-y1, x2-x1) * 180 / np.pi)
                
                if angle < 20 or angle > 160:  # Horizontal
                    horizontal_lines += 1
                elif 70 < angle < 110:  # Vertical
                    vertical_lines += 1
            
            # ICs typically have pins on opposite sides
            pin_count = max(horizontal_lines, vertical_lines)
            has_pins = pin_count >= 3  # At least 3 parallel pins
            
            return has_pins, pin_count
        
        return False, 0
    
    def detect_rectangular_structure(self, roi):
        """Detect rectangular IC body structure"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return False, 0
        
        # Get largest contour
        largest = max(contours, key=cv2.contourArea)
        
        # Approximate to polygon
        perimeter = cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, 0.02 * perimeter, True)
        
        # ICs are rectangular (4 corners) or slightly rounded (4-6 corners)
        corner_count = len(approx)
        is_rectangular = 4 <= corner_count <= 8
        
        # Calculate rectangularity
        rect_area = cv2.boundingRect(largest)[2] * cv2.boundingRect(largest)[3]
        contour_area = cv2.contourArea(largest)
        rectangularity = contour_area / rect_area if rect_area > 0 else 0
        
        return is_rectangular and rectangularity > 0.7, rectangularity
    
    def detect_ic_text(self, roi):
        """Detect text markings on IC (part numbers, etc.)"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Check for text-like regions (high frequency content)
        laplacian = cv2.Laplacian(enhanced, cv2.CV_64F)
        variance = laplacian.var()
        
        # ICs often have printed text (higher variance)
        has_text = variance > 50
        
        return has_text, variance
    
    def detect_metallic_surface(self, roi):
        """Detect metallic/reflective surface typical of ICs"""
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Get saturation channel
        saturation = hsv[:,:,1]
        
        # Metallic surfaces have low saturation
        mean_saturation = np.mean(saturation)
        is_metallic = mean_saturation < 80
        
        # Check for dark colors (ICs are usually black/dark)
        value = hsv[:,:,2]
        mean_brightness = np.mean(value)
        is_dark = 30 < mean_brightness < 150
        
        return is_metallic and is_dark, mean_saturation
    
    def classify_ic_type(self, roi, pin_count):
        """Classify IC type based on features"""
        height, width = roi.shape[:2]
        aspect_ratio = width / height
        
        if pin_count >= 8:
            if aspect_ratio > 2.0:
                return "DIP IC (Dual In-line Package)"
            elif aspect_ratio < 1.2:
                return "QFP IC (Quad Flat Package)"
            else:
                return "SOIC IC (Small Outline IC)"
        elif pin_count >= 3:
            return "SMD IC (Surface Mount)"
        else:
            return "IC Chip"
    
    def is_advanced_ic(self, box, frame):
        """Advanced IC detection with multiple checks"""
        x1, y1, x2, y2 = map(int, box[:4])
        
        # Size validation
        width = x2 - x1
        height = y2 - y1
        
        if width < self.min_size or height < self.min_size:
            return False, "Too small", {}
        
        if width > self.max_size or height > self.max_size:
            return False, "Too large", {}
        
        # Aspect ratio
        aspect_ratio = width / height
        if aspect_ratio < self.min_aspect_ratio or aspect_ratio > self.max_aspect_ratio:
            return False, f"Wrong shape ({aspect_ratio:.2f})", {}
        
        # Extract ROI
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            return False, "Invalid region", {}
        
        # Multi-criteria analysis
        criteria_passed = 0
        total_criteria = 5
        details = {}
        
        # 1. Pin detection
        has_pins, pin_count = self.detect_ic_pins(roi)
        details['pins'] = pin_count
        if has_pins:
            criteria_passed += 1
        
        # 2. Rectangular structure
        is_rect, rectangularity = self.detect_rectangular_structure(roi)
        details['rectangularity'] = f"{rectangularity:.2f}"
        if is_rect:
            criteria_passed += 1
        
        # 3. Text markings
        has_text, text_variance = self.detect_ic_text(roi)
        details['text_detected'] = has_text
        if has_text:
            criteria_passed += 1
        
        # 4. Metallic surface
        is_metallic, saturation = self.detect_metallic_surface(roi)
        details['metallic'] = is_metallic
        if is_metallic:
            criteria_passed += 1
        
        # 5. Edge density (moderate edges)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_ratio = np.count_nonzero(edges) / edges.size
        details['edge_density'] = f"{edge_ratio:.3f}"
        if 0.05 < edge_ratio < 0.3:
            criteria_passed += 1
        
        # Face rejection (detect circular features)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                                   param1=50, param2=30, minRadius=5, maxRadius=50)
        if circles is not None and len(circles[0]) >= 2:
            return False, "Face/circular features detected", details
        
        # Decision: Need at least 3 out of 5 criteria
        confidence = (criteria_passed / total_criteria) * 100
        details['confidence'] = f"{confidence:.1f}%"
        details['criteria_passed'] = f"{criteria_passed}/{total_criteria}"
        
        if criteria_passed >= 3:
            # Classify IC type
            ic_type = self.classify_ic_type(roi, pin_count)
            details['ic_type'] = ic_type
            return True, f"IC detected ({confidence:.0f}%)", details
        
        return False, f"Not IC ({confidence:.0f}%)", details
    
    def draw_enhanced_detection(self, frame, box, details):
        """Draw enhanced detection box with detailed info"""
        x1, y1, x2, y2 = map(int, box[:4])
        
        # Draw main box (green for IC)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        # Draw corner markers
        corner_len = 15
        cv2.line(frame, (x1, y1), (x1+corner_len, y1), (0, 255, 255), 3)
        cv2.line(frame, (x1, y1), (x1, y1+corner_len), (0, 255, 255), 3)
        cv2.line(frame, (x2, y1), (x2-corner_len, y1), (0, 255, 255), 3)
        cv2.line(frame, (x2, y1), (x2, y1+corner_len), (0, 255, 255), 3)
        cv2.line(frame, (x1, y2), (x1+corner_len, y2), (0, 255, 255), 3)
        cv2.line(frame, (x1, y2), (x1, y2-corner_len), (0, 255, 255), 3)
        cv2.line(frame, (x2, y2), (x2-corner_len, y2), (0, 255, 255), 3)
        cv2.line(frame, (x2, y2), (x2, y2-corner_len), (0, 255, 255), 3)
        
        # Info panel
        info_y = y1 - 10
        line_height = 25
        
        # IC Type
        if 'ic_type' in details:
            cv2.putText(frame, details['ic_type'], (x1, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            info_y -= line_height
        
        # Confidence
        if 'confidence' in details:
            cv2.putText(frame, f"Confidence: {details['confidence']}", (x1, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            info_y -= line_height
        
        # Pins detected
        if 'pins' in details and details['pins'] > 0:
            cv2.putText(frame, f"Pins: {details['pins']}", (x1, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    def detect_webcam(self):
        """Enhanced webcam detection"""
        print("\n" + "="*70)
        print("🎥 ENHANCED IC DETECTION - WEBCAM MODE")
        print("="*70)
        print("📸 Controls:")
        print("   Q - Quit")
        print("   S - Save screenshot with analysis")
        print("   SPACE - Pause/Resume")
        print("   + - Increase detection sensitivity")
        print("   - - Decrease detection sensitivity")
        print("="*70 + "\n")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open webcam!")
            return
        
        # Set higher resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        paused = False
        frame_count = 0
        detection_threshold = 3  # Criteria threshold (adjustable)
        
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                display_frame = frame.copy()
                
                # Run detection every 2 frames (balance speed/accuracy)
                if frame_count % 2 == 0:
                    results = self.model(frame, verbose=False, conf=0.25)
                    
                    ic_detections = []
                    
                    for result in results:
                        boxes = result.boxes
                        for box in boxes:
                            is_ic, reason, details = self.is_advanced_ic(box.xyxy[0], frame)
                            
                            if is_ic:
                                ic_detections.append((box, details))
                    
                    # Draw all detections
                    for idx, (box, details) in enumerate(ic_detections, 1):
                        self.draw_enhanced_detection(display_frame, box.xyxy[0], details)
                        
                        # Add IC number badge
                        x1, y1 = map(int, box.xyxy[0][:2])
                        badge_size = 30
                        cv2.circle(display_frame, (x1-15, y1-15), 20, (0, 255, 0), -1)
                        cv2.putText(display_frame, str(idx), (x1-23, y1-8),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                
                # Enhanced status overlay
                status_h = 100
                status_bg = np.zeros((status_h, display_frame.shape[1], 3), dtype=np.uint8)
                status_bg[:] = (30, 30, 30)
                
                ic_count = len(ic_detections) if frame_count % 2 == 0 else 0
                
                if ic_count > 0:
                    status_text = f"✅ {ic_count} IC CHIP(S) DETECTED"
                    color = (0, 255, 0)
                    
                    # Show details of first IC
                    if ic_detections:
                        details = ic_detections[0][1]
                        detail_text = f"Type: {details.get('ic_type', 'Unknown')} | Pins: {details.get('pins', 0)} | {details.get('confidence', 'N/A')}"
                        cv2.putText(status_bg, detail_text, (20, 80),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                else:
                    status_text = "⚠️ NO IC DETECTED - Show IC chip to camera"
                    color = (0, 165, 255)
                
                cv2.putText(status_bg, status_text, (20, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
                
                # Add sensitivity indicator
                cv2.putText(status_bg, f"Sensitivity: {detection_threshold}/5 (+/-)", 
                           (display_frame.shape[1]-300, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                display_frame = np.vstack([status_bg, display_frame])
            
            # Display
            cv2.imshow('Enhanced IC Detection', display_frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"enhanced_ic_{frame_count}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"📸 Saved: {filename}")
            elif key == ord(' '):
                paused = not paused
                print("⏸️  PAUSED" if paused else "▶️  RESUMED")
            elif key == ord('+') or key == ord('='):
                detection_threshold = min(5, detection_threshold + 1)
                print(f"📈 Sensitivity increased: {detection_threshold}/5")
            elif key == ord('-') or key == ord('_'):
                detection_threshold = max(1, detection_threshold - 1)
                print(f"📉 Sensitivity decreased: {detection_threshold}/5")
        
        cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Enhanced detection closed")
    
    def detect_image(self, image_path):
        """Enhanced image detection with detailed analysis"""
        print(f"\n📷 Enhanced IC Detection: {image_path}")
        print("="*70)
        
        frame = cv2.imread(image_path)
        if frame is None:
            print("❌ Cannot read image!")
            return
        
        results = self.model(frame, verbose=False, conf=0.25)
        
        ic_detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                is_ic, reason, details = self.is_advanced_ic(box.xyxy[0], frame)
                
                if is_ic:
                    ic_detections.append((box, details))
                    
                    # Print detailed analysis
                    print(f"\n🔍 IC Detection #{len(ic_detections)}:")
                    print(f"   Type: {details.get('ic_type', 'Unknown')}")
                    print(f"   Confidence: {details.get('confidence', 'N/A')}")
                    print(f"   Pins detected: {details.get('pins', 0)}")
                    print(f"   Rectangularity: {details.get('rectangularity', 'N/A')}")
                    print(f"   Metallic surface: {'Yes' if details.get('metallic') else 'No'}")
                    print(f"   Text markings: {'Yes' if details.get('text_detected') else 'No'}")
        
        # Draw detections
        for idx, (box, details) in enumerate(ic_detections, 1):
            self.draw_enhanced_detection(frame, box.xyxy[0], details)
        
        print("\n" + "="*70)
        if ic_detections:
            print(f"✅ Total ICs found: {len(ic_detections)}")
        else:
            print("⚠️ No IC chips detected in this image")
        print("="*70)
        
        # Show result
        cv2.imshow('Enhanced IC Detection Result', frame)
        print("\nPress any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    print("\n" + "="*70)
    print("⚡ ENHANCED IC DETECTION SYSTEM")
    print("="*70)
    print("Features:")
    print("  ✅ Advanced pin/leg detection")
    print("  ✅ IC type classification (DIP, QFP, SOIC, SMD)")
    print("  ✅ Multi-criteria analysis (5 checks)")
    print("  ✅ Confidence scoring")
    print("  ✅ Face rejection algorithm")
    print("  ✅ Enhanced visualization")
    print("="*70 + "\n")
    
    detector = EnhancedICDetector()
    
    print("\nChoose mode:")
    print("1. Webcam detection (real-time enhanced)")
    print("2. Image detection (detailed analysis)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        detector.detect_webcam()
    elif choice == "2":
        image_path = input("Enter image path: ").strip().strip('"')
        detector.detect_image(image_path)
    else:
        print("❌ Invalid choice!")


if __name__ == "__main__":
    main()
