"""
OPTIMIZED IC DETECTION - More Accurate IC-Only Detection
Focused on real IC chip characteristics
"""

import cv2
from ultralytics import YOLO
import numpy as np

class OptimizedICDetector:
    def __init__(self):
        print("🚀 Loading Optimized IC Detection System...")
        self.model = YOLO('yolov8s.pt')
        print("✅ Model loaded!")
        
        # Optimized parameters for IC detection
        self.min_size = 50
        self.max_size = 500
        
    def analyze_ic_features(self, roi):
        """Comprehensive IC feature analysis"""
        if roi.size == 0 or roi.shape[0] < 20 or roi.shape[1] < 20:
            return False, "Invalid ROI", {}
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        features = {}
        score = 0
        max_score = 10
        
        # 1. Check if it's too bright (reject faces/skin)
        mean_brightness = np.mean(gray)
        features['brightness'] = mean_brightness
        if 40 < mean_brightness < 180:  # ICs are usually darker
            score += 2
        else:
            return False, f"Wrong brightness: {mean_brightness:.0f}", features
        
        # 2. Edge density (ICs have moderate sharp edges)
        edges = cv2.Canny(gray, 40, 120)
        edge_density = np.count_nonzero(edges) / edges.size
        features['edge_density'] = edge_density
        if 0.08 < edge_density < 0.35:
            score += 2
        elif edge_density < 0.05:
            return False, "Too smooth (not IC)", features
        
        # 3. Rectangular shape check
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w_rect, h_rect = cv2.boundingRect(largest)
            rect_area = w_rect * h_rect
            contour_area = cv2.contourArea(largest)
            
            if rect_area > 0:
                rectangularity = contour_area / rect_area
                features['rectangularity'] = rectangularity
                if rectangularity > 0.75:
                    score += 2
        
        # 4. Look for parallel lines (IC pins)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=15,
                                minLineLength=int(min(h, w) * 0.15),
                                maxLineGap=5)
        
        pin_count = 0
        if lines is not None:
            # Count parallel horizontal and vertical lines
            horizontal = 0
            vertical = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = abs(np.arctan2(y2-y1, x2-x1) * 180 / np.pi)
                if angle < 15 or angle > 165:
                    horizontal += 1
                elif 75 < angle < 105:
                    vertical += 1
            
            pin_count = max(horizontal, vertical)
            features['pin_lines'] = pin_count
            
            if pin_count >= 4:  # ICs typically have multiple parallel pins
                score += 2
        
        # 5. Color saturation (ICs are usually low saturation - black/dark)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        saturation = hsv[:,:,1]
        mean_saturation = np.mean(saturation)
        features['saturation'] = mean_saturation
        
        if mean_saturation < 90:  # Low saturation = metallic/black
            score += 1
        
        # 6. Reject circular features (faces, eyes)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                                   param1=50, param2=30, minRadius=5, maxRadius=int(min(h,w)*0.4))
        
        if circles is not None and len(circles[0]) >= 2:
            return False, "Circular features (face/round object)", features
        
        # 7. Texture analysis (ICs have uniform texture)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_variance = laplacian.var()
        features['texture_var'] = texture_variance
        
        if 50 < texture_variance < 800:
            score += 1
        
        # Decision: Need at least 6/10 points
        confidence = (score / max_score) * 100
        features['score'] = f"{score}/{max_score}"
        features['confidence'] = f"{confidence:.1f}%"
        
        if score >= 6:
            return True, f"IC detected ({confidence:.0f}%)", features
        else:
            return False, f"Not IC ({confidence:.0f}%) - score too low", features
    
    def is_ic_chip(self, box, frame):
        """Main IC detection logic"""
        x1, y1, x2, y2 = map(int, box[:4])
        
        width = x2 - x1
        height = y2 - y1
        
        # Size validation
        if width < self.min_size or height < self.min_size:
            return False, "Too small", {}
        
        if width > self.max_size or height > self.max_size:
            return False, "Too large", {}
        
        # Aspect ratio (ICs can be square to rectangular)
        aspect_ratio = max(width, height) / min(width, height)
        if aspect_ratio > 5.0:
            return False, f"Too elongated ({aspect_ratio:.1f}:1)", {}
        
        # Extract ROI with padding
        pad = 5
        y1_pad = max(0, y1-pad)
        y2_pad = min(frame.shape[0], y2+pad)
        x1_pad = max(0, x1-pad)
        x2_pad = min(frame.shape[1], x2+pad)
        
        roi = frame[y1_pad:y2_pad, x1_pad:x2_pad]
        
        return self.analyze_ic_features(roi)
    
    def draw_detection(self, frame, box, details, ic_num):
        """Draw enhanced detection visualization"""
        x1, y1, x2, y2 = map(int, box[:4])
        
        # Main green box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        # Corner markers
        corner_len = 20
        thickness = 3
        color = (0, 255, 255)  # Cyan
        
        # Top-left
        cv2.line(frame, (x1, y1), (x1+corner_len, y1), color, thickness)
        cv2.line(frame, (x1, y1), (x1, y1+corner_len), color, thickness)
        # Top-right
        cv2.line(frame, (x2, y1), (x2-corner_len, y1), color, thickness)
        cv2.line(frame, (x2, y1), (x2, y1+corner_len), color, thickness)
        # Bottom-left
        cv2.line(frame, (x1, y2), (x1+corner_len, y2), color, thickness)
        cv2.line(frame, (x1, y2), (x1, y2-corner_len), color, thickness)
        # Bottom-right
        cv2.line(frame, (x2, y2), (x2-corner_len, y2), color, thickness)
        cv2.line(frame, (x2, y2), (x2, y2-corner_len), color, thickness)
        
        # IC number badge
        badge_x = x1 - 25
        badge_y = y1 - 25
        cv2.circle(frame, (badge_x, badge_y), 20, (0, 255, 0), -1)
        cv2.circle(frame, (badge_x, badge_y), 20, (255, 255, 255), 2)
        cv2.putText(frame, str(ic_num), (badge_x-8, badge_y+8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Info labels
        info_y = y1 - 35
        
        # Confidence
        if 'confidence' in details:
            label = f"IC #{ic_num}: {details['confidence']}"
            cv2.putText(frame, label, (x1, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            info_y -= 25
        
        # Pin count if available
        if 'pin_lines' in details and details['pin_lines'] > 0:
            pin_label = f"Pins: {details['pin_lines']}"
            cv2.putText(frame, pin_label, (x1, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    def detect_webcam(self):
        """Real-time webcam IC detection"""
        print("\n" + "="*70)
        print("🎥 OPTIMIZED IC DETECTION - WEBCAM MODE")
        print("="*70)
        print("📸 Controls:")
        print("   Q - Quit")
        print("   S - Save screenshot")
        print("   SPACE - Pause/Resume")
        print("   D - Toggle debug info")
        print("="*70)
        print("\n💡 TIP: Hold IC chip flat to camera, 15-25cm distance")
        print("="*70 + "\n")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open webcam!")
            return
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        paused = False
        show_debug = False
        frame_count = 0
        detection_threshold = 0.2  # Lower threshold for initial detection
        
        print("🎥 Webcam started! Point at IC chip...")
        
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                display_frame = frame.copy()
                
                # Run detection every frame for responsiveness
                results = self.model(frame, verbose=False, conf=detection_threshold)
                
                ic_detections = []
                debug_info = []
                
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        is_ic, reason, details = self.is_ic_chip(box.xyxy[0], frame)
                        
                        if show_debug:
                            debug_info.append(f"{reason}: {details}")
                        
                        if is_ic:
                            ic_detections.append((box, details))
                
                # Draw all IC detections
                for idx, (box, details) in enumerate(ic_detections, 1):
                    self.draw_detection(display_frame, box.xyxy[0], details, idx)
                
                # Status overlay
                status_h = 120
                status_bg = np.zeros((status_h, display_frame.shape[1], 3), dtype=np.uint8)
                status_bg[:] = (30, 30, 30)
                
                if len(ic_detections) > 0:
                    status_text = f"✅ {len(ic_detections)} IC CHIP(S) DETECTED"
                    color = (0, 255, 0)
                    
                    # Show details of first IC
                    if ic_detections:
                        details = ic_detections[0][1]
                        detail_lines = [
                            f"Confidence: {details.get('confidence', 'N/A')}",
                            f"Pins: {details.get('pin_lines', 0)} | Score: {details.get('score', 'N/A')}"
                        ]
                        
                        y_offset = 70
                        for detail in detail_lines:
                            cv2.putText(status_bg, detail, (20, y_offset),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                            y_offset += 25
                else:
                    status_text = "⚠️ NO IC DETECTED"
                    color = (0, 165, 255)
                    cv2.putText(status_bg, "Hold IC chip flat to camera (15-25cm)", (20, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
                
                cv2.putText(status_bg, status_text, (20, 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
                
                # Debug info toggle indicator
                if show_debug:
                    cv2.putText(status_bg, "DEBUG: ON (D to toggle)", 
                               (display_frame.shape[1]-250, 35),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                
                display_frame = np.vstack([status_bg, display_frame])
                
                # Show debug info on console
                if show_debug and frame_count % 30 == 0 and debug_info:
                    print("\n🔍 Debug Info:")
                    for info in debug_info[:3]:  # Show first 3
                        print(f"   {info}")
            
            # Display
            cv2.imshow('Optimized IC Detection', display_frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"ic_detection_{frame_count}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"📸 Saved: {filename}")
            elif key == ord(' '):
                paused = not paused
                print("⏸️  PAUSED" if paused else "▶️  RESUMED")
            elif key == ord('d'):
                show_debug = not show_debug
                print("🔍 Debug mode:", "ON" if show_debug else "OFF")
        
        cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Detection closed")
    
    def detect_image(self, image_path):
        """Detect ICs in image with detailed analysis"""
        print(f"\n📷 Analyzing: {image_path}")
        print("="*70)
        
        frame = cv2.imread(image_path)
        if frame is None:
            print("❌ Cannot read image!")
            return
        
        results = self.model(frame, verbose=False, conf=0.15)
        
        ic_detections = []
        all_detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                is_ic, reason, details = self.is_ic_chip(box.xyxy[0], frame)
                all_detections.append((is_ic, reason, details))
                
                if is_ic:
                    ic_detections.append((box, details))
                    
                    print(f"\n✅ IC #{len(ic_detections)} FOUND:")
                    print(f"   Confidence: {details.get('confidence', 'N/A')}")
                    print(f"   Score: {details.get('score', 'N/A')}")
                    print(f"   Pin lines: {details.get('pin_lines', 0)}")
                    print(f"   Brightness: {details.get('brightness', 0):.1f}")
                    print(f"   Edge density: {details.get('edge_density', 0):.3f}")
                else:
                    print(f"\n❌ Rejected: {reason}")
                    if details:
                        print(f"   Details: {details}")
        
        # Draw detections
        for idx, (box, details) in enumerate(ic_detections, 1):
            self.draw_detection(frame, box.xyxy[0], details, idx)
        
        print("\n" + "="*70)
        if ic_detections:
            print(f"✅ TOTAL ICs FOUND: {len(ic_detections)}")
        else:
            print("⚠️ NO IC CHIPS DETECTED")
            print(f"   Analyzed {len(all_detections)} objects")
        print("="*70)
        
        # Display
        cv2.imshow('Optimized IC Detection Result', frame)
        print("\nPress any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    print("\n" + "="*70)
    print("⚡ OPTIMIZED IC DETECTION SYSTEM")
    print("="*70)
    print("Improvements:")
    print("  ✅ Better IC feature analysis (10 checks)")
    print("  ✅ Enhanced pin detection algorithm")
    print("  ✅ Improved face/skin rejection")
    print("  ✅ Real-time debug mode (D key)")
    print("  ✅ Optimized for actual IC chips")
    print("="*70 + "\n")
    
    detector = OptimizedICDetector()
    
    print("Choose mode:")
    print("1. Webcam detection (recommended)")
    print("2. Image detection")
    
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
