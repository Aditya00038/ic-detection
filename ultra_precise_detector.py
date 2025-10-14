"""
ULTRA-PRECISE IC DETECTION v2.0
Maximum accuracy for IC chip detection
Uses advanced CV algorithms and multiple validation layers
"""

import cv2
from ultralytics import YOLO
import numpy as np

class UltraPreciseICDetector:
    def __init__(self):
        print("🚀 Loading Ultra-Precise IC Detection System...")
        self.model = YOLO('yolov8s.pt')
        print("✅ Model loaded!")
        
        # Strict IC parameters
        self.min_size = 60
        self.max_size = 450
        
    def detect_ic_package_type(self, roi):
        """Identify IC package type based on shape and features"""
        h, w = roi.shape[:2]
        aspect_ratio = w / h
        
        if 0.9 < aspect_ratio < 1.1:
            return "QFP/QFN (Square IC)"
        elif 1.5 < aspect_ratio < 3.5:
            return "DIP/SOIC (Rectangular IC)"
        elif aspect_ratio < 0.9:
            return "Vertical IC Package"
        else:
            return "IC Chip"
    
    def advanced_pin_detection(self, gray):
        """Advanced algorithm to detect IC pins/legs"""
        h, w = gray.shape
        
        # Multi-scale edge detection
        edges1 = cv2.Canny(gray, 30, 90)
        edges2 = cv2.Canny(gray, 50, 150)
        edges = cv2.bitwise_or(edges1, edges2)
        
        # Morphological operations to connect pin segments
        kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
        kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))
        
        edges_h = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_h)
        edges_v = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_v)
        
        # Detect horizontal pins (most common in DIP ICs)
        lines_h = cv2.HoughLinesP(edges_h, 1, np.pi/180, threshold=10,
                                   minLineLength=int(w * 0.12),
                                   maxLineGap=3)
        
        # Detect vertical pins (QFP packages)
        lines_v = cv2.HoughLinesP(edges_v, 1, np.pi/180, threshold=10,
                                   minLineLength=int(h * 0.12),
                                   maxLineGap=3)
        
        h_pins = 0
        v_pins = 0
        
        if lines_h is not None:
            for line in lines_h:
                x1, y1, x2, y2 = line[0]
                angle = abs(np.arctan2(y2-y1, x2-x1) * 180 / np.pi)
                if angle < 20 or angle > 160:  # Horizontal
                    h_pins += 1
        
        if lines_v is not None:
            for line in lines_v:
                x1, y1, x2, y2 = line[0]
                angle = abs(np.arctan2(y2-y1, x2-x1) * 180 / np.pi)
                if 70 < angle < 110:  # Vertical
                    v_pins += 1
        
        total_pins = h_pins + v_pins
        has_pins = total_pins >= 4
        
        return has_pins, total_pins, h_pins, v_pins
    
    def check_ic_body_structure(self, gray):
        """Verify IC body has correct rectangular structure"""
        # Adaptive thresholding for better contrast
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 11, 2)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return False, 0, 0
        
        # Get largest contour (IC body)
        largest = max(contours, key=cv2.contourArea)
        
        # Fit rectangle
        rect = cv2.minAreaRect(largest)
        box = cv2.boxPoints(rect)
        
        # Calculate rectangularity
        rect_area = rect[1][0] * rect[1][1]
        contour_area = cv2.contourArea(largest)
        
        if rect_area > 0:
            rectangularity = contour_area / rect_area
        else:
            rectangularity = 0
        
        # Check corners
        epsilon = 0.02 * cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, epsilon, True)
        corner_count = len(approx)
        
        # IC bodies have 4-6 corners (rectangular with possibly rounded corners)
        is_rectangular = (rectangularity > 0.75 and 4 <= corner_count <= 8)
        
        return is_rectangular, rectangularity, corner_count
    
    def analyze_surface_texture(self, roi):
        """Analyze IC surface for characteristic texture patterns"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Check for uniform, non-organic texture
        # ICs have printed text and uniform surface
        
        # Standard deviation of pixel intensities
        std_dev = np.std(gray)
        
        # Local Binary Pattern-like analysis
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_score = laplacian.var()
        
        # Gradient magnitude
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_mag = np.sqrt(sobelx**2 + sobely**2)
        edge_strength = np.mean(gradient_mag)
        
        # IC characteristics:
        # - Moderate texture variance (printed text)
        # - Sharp edges (rectangular body)
        # - Not too smooth (like skin) or too chaotic
        
        has_ic_texture = (
            40 < std_dev < 80 and
            100 < texture_score < 1000 and
            20 < edge_strength < 80
        )
        
        return has_ic_texture, std_dev, texture_score, edge_strength
    
    def reject_organic_objects(self, roi):
        """Advanced rejection of faces, hands, and organic objects"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # 1. Detect circular features (eyes, nostrils, etc.)
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, dp=1.5, minDist=min(w, h)//4,
            param1=50, param2=30, minRadius=5, maxRadius=min(w, h)//3
        )
        
        if circles is not None and len(circles[0]) >= 2:
            return True, "Multiple circular features (face/eyes)"
        
        # 2. Check skin-like color in HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Skin color range in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 170, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        skin_ratio = np.count_nonzero(skin_mask) / skin_mask.size
        
        if skin_ratio > 0.3:
            return True, f"Skin-like color detected ({skin_ratio*100:.1f}%)"
        
        # 3. Check brightness (faces are usually brighter than ICs)
        mean_brightness = np.mean(gray)
        if mean_brightness > 160:
            return True, f"Too bright ({mean_brightness:.0f}) - likely face/skin"
        
        # 4. Check for smooth gradients (organic vs geometric)
        # ICs have sharp transitions, faces have smooth gradients
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        
        if edge_density < 0.06:
            return True, f"Too smooth ({edge_density:.3f}) - not IC-like"
        
        return False, "Passed organic rejection"
    
    def comprehensive_ic_analysis(self, roi):
        """Complete multi-layer IC analysis"""
        if roi.size == 0 or roi.shape[0] < 30 or roi.shape[1] < 30:
            return False, "ROI too small", {}
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        features = {}
        score = 0
        max_score = 12
        reasons = []
        
        # LAYER 1: Reject organic objects first (CRITICAL)
        is_organic, organic_reason = self.reject_organic_objects(roi)
        if is_organic:
            return False, organic_reason, features
        features['organic_check'] = "✓ Passed"
        score += 2
        
        # LAYER 2: Pin detection (ESSENTIAL for ICs)
        has_pins, total_pins, h_pins, v_pins = self.advanced_pin_detection(gray)
        features['pins'] = f"{total_pins} ({h_pins}H+{v_pins}V)"
        if has_pins:
            score += 3
            reasons.append("Pins detected")
        else:
            reasons.append("No pins found")
        
        # LAYER 3: Body structure (CRITICAL)
        is_rect, rectangularity, corners = self.check_ic_body_structure(gray)
        features['rectangularity'] = f"{rectangularity:.2f}"
        features['corners'] = corners
        if is_rect:
            score += 2
            reasons.append("Rectangular body")
        else:
            reasons.append("Not rectangular")
        
        # LAYER 4: Surface texture analysis
        has_ic_texture, std_dev, texture_var, edge_str = self.analyze_surface_texture(roi)
        features['texture'] = f"{texture_var:.0f}"
        features['std_dev'] = f"{std_dev:.1f}"
        if has_ic_texture:
            score += 2
            reasons.append("IC-like texture")
        
        # LAYER 5: Color saturation (ICs are typically low saturation)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        saturation = hsv[:,:,1]
        mean_sat = np.mean(saturation)
        features['saturation'] = f"{mean_sat:.0f}"
        if mean_sat < 100:  # Low saturation (black/metallic)
            score += 1
            reasons.append("Low saturation")
        
        # LAYER 6: Edge characteristics
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        features['edge_density'] = f"{edge_density:.3f}"
        if 0.10 < edge_density < 0.40:
            score += 1
            reasons.append("Good edge density")
        
        # LAYER 7: Aspect ratio check
        aspect = w / h
        features['aspect'] = f"{aspect:.2f}"
        if 0.4 < aspect < 4.0:
            score += 1
            reasons.append("Valid aspect ratio")
        
        # Calculate confidence
        confidence = (score / max_score) * 100
        features['score'] = f"{score}/{max_score}"
        features['confidence'] = f"{confidence:.1f}%"
        features['reasons'] = ", ".join(reasons[:3])
        
        # IC Package type
        if score >= 7:
            package_type = self.detect_ic_package_type(gray)
            features['package'] = package_type
        
        # DECISION: Need at least 7/12 points (58%)
        if score >= 7:
            return True, f"IC DETECTED ({confidence:.0f}%)", features
        else:
            return False, f"Not IC ({confidence:.0f}%) - {reasons[0] if reasons else 'insufficient features'}", features
    
    def is_ic_chip(self, box, frame):
        """Main IC detection entry point"""
        x1, y1, x2, y2 = map(int, box[:4])
        
        width = x2 - x1
        height = y2 - y1
        
        # Size validation
        if width < self.min_size or height < self.min_size:
            return False, f"Too small ({width}x{height})", {}
        
        if width > self.max_size or height > self.max_size:
            return False, f"Too large ({width}x{height})", {}
        
        # Extreme aspect ratio rejection
        aspect = max(width, height) / min(width, height)
        if aspect > 6.0:
            return False, f"Too elongated ({aspect:.1f}:1)", {}
        
        # Extract ROI with small padding
        pad = 3
        y1_pad = max(0, y1-pad)
        y2_pad = min(frame.shape[0], y2+pad)
        x1_pad = max(0, x1-pad)
        x2_pad = min(frame.shape[1], x2+pad)
        
        roi = frame[y1_pad:y2_pad, x1_pad:x2_pad]
        
        return self.comprehensive_ic_analysis(roi)
    
    def draw_professional_overlay(self, frame, box, details, ic_num):
        """Professional detection overlay with full details"""
        x1, y1, x2, y2 = map(int, box[:4])
        
        # Main detection box - thick green
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        # Corner markers - cyan
        corner_len = 25
        thickness = 3
        color = (0, 255, 255)
        
        cv2.line(frame, (x1, y1), (x1+corner_len, y1), color, thickness)
        cv2.line(frame, (x1, y1), (x1, y1+corner_len), color, thickness)
        cv2.line(frame, (x2, y1), (x2-corner_len, y1), color, thickness)
        cv2.line(frame, (x2, y1), (x2, y1+corner_len), color, thickness)
        cv2.line(frame, (x1, y2), (x1+corner_len, y2), color, thickness)
        cv2.line(frame, (x1, y2), (x1, y2-corner_len), color, thickness)
        cv2.line(frame, (x2, y2), (x2-corner_len, y2), color, thickness)
        cv2.line(frame, (x2, y2), (x2, y2-corner_len), color, thickness)
        
        # IC number badge
        badge_x = x1 - 30
        badge_y = y1 - 30
        cv2.circle(frame, (badge_x, badge_y), 22, (0, 255, 0), -1)
        cv2.circle(frame, (badge_x, badge_y), 22, (255, 255, 255), 2)
        cv2.putText(frame, str(ic_num), (badge_x-10, badge_y+8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        
        # Info panel
        info_y = y1 - 40
        line_height = 22
        
        # Package type
        if 'package' in details:
            cv2.putText(frame, details['package'], (x1, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
            info_y -= line_height
        
        # Confidence + Score
        if 'confidence' in details:
            label = f"{details['confidence']} | {details.get('score', '')}"
            cv2.putText(frame, label, (x1, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            info_y -= line_height
        
        # Pins
        if 'pins' in details:
            cv2.putText(frame, f"Pins: {details['pins']}", (x1, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 2)
    
    def detect_webcam(self):
        """Real-time ultra-precise detection"""
        print("\n" + "="*70)
        print("🎥 ULTRA-PRECISE IC DETECTION - WEBCAM MODE")
        print("="*70)
        print("📸 Controls:")
        print("   Q - Quit")
        print("   S - Save screenshot")
        print("   SPACE - Pause/Resume")
        print("   D - Debug mode")
        print("   I - Show info panel")
        print("="*70)
        print("\n💡 OPTIMAL SETUP:")
        print("   • IC flat to camera (parallel)")
        print("   • Distance: 15-25cm")
        print("   • Good overhead lighting")
        print("   • Plain background")
        print("   • IC fills 25-40% of frame")
        print("="*70 + "\n")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open webcam!")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        
        paused = False
        show_debug = False
        show_info = True
        frame_count = 0
        
        print("🎥 Webcam started!")
        
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                display_frame = frame.copy()
                
                # Run detection
                results = self.model(frame, verbose=False, conf=0.15)
                
                ic_detections = []
                rejections = []
                
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        is_ic, reason, details = self.is_ic_chip(box.xyxy[0], frame)
                        
                        if is_ic:
                            ic_detections.append((box, details))
                        elif show_debug:
                            rejections.append((reason, details))
                
                # Draw detections
                for idx, (box, details) in enumerate(ic_detections, 1):
                    self.draw_professional_overlay(display_frame, box.xyxy[0], details, idx)
                
                # Status panel
                status_h = 140 if show_info else 80
                status_bg = np.zeros((status_h, display_frame.shape[1], 3), dtype=np.uint8)
                status_bg[:] = (25, 25, 25)
                
                if len(ic_detections) > 0:
                    status_text = f"✅ {len(ic_detections)} IC CHIP(S) DETECTED"
                    color = (0, 255, 0)
                    
                    if show_info and ic_detections:
                        details = ic_detections[0][1]
                        info_lines = [
                            f"Package: {details.get('package', 'Unknown')}",
                            f"Confidence: {details.get('confidence', 'N/A')} | Pins: {details.get('pins', 'N/A')}",
                            f"Quality: {details.get('rectangularity', 'N/A')} rect | {details.get('edge_density', 'N/A')} edges"
                        ]
                        
                        y_off = 75
                        for line in info_lines:
                            cv2.putText(status_bg, line, (20, y_off),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)
                            y_off += 22
                else:
                    status_text = "⚠️ NO IC DETECTED"
                    color = (0, 165, 255)
                    if show_info:
                        cv2.putText(status_bg, "Position IC flat, 15-25cm from camera", (20, 75),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
                
                cv2.putText(status_bg, status_text, (20, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 2)
                
                # Controls indicator
                controls = f"D:Debug[{'ON' if show_debug else 'OFF'}] | I:Info[{'ON' if show_info else 'OFF'}]"
                cv2.putText(status_bg, controls, (display_frame.shape[1]-320, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)
                
                display_frame = np.vstack([status_bg, display_frame])
                
                # Console debug
                if show_debug and frame_count % 30 == 0:
                    if rejections:
                        print(f"\n🔍 Frame {frame_count} - Rejections:")
                        for reason, details in rejections[:2]:
                            print(f"   ❌ {reason}")
                            if details:
                                print(f"      {details}")
            
            cv2.imshow('Ultra-Precise IC Detection', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"ic_ultra_{frame_count}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"📸 Saved: {filename}")
            elif key == ord(' '):
                paused = not paused
                print("⏸️  PAUSED" if paused else "▶️  RESUMED")
            elif key == ord('d'):
                show_debug = not show_debug
                print("🔍 Debug:", "ON" if show_debug else "OFF")
            elif key == ord('i'):
                show_info = not show_info
                print("ℹ️  Info panel:", "ON" if show_info else "OFF")
        
        cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Ultra-precise detection closed")


def main():
    print("\n" + "="*70)
    print("⚡ ULTRA-PRECISE IC DETECTION SYSTEM v2.0")
    print("="*70)
    print("Advanced Features:")
    print("  ✅ 7-layer analysis system (12 validation points)")
    print("  ✅ Advanced pin detection (H+V lines)")
    print("  ✅ Multi-layer organic rejection (face/skin/hand)")
    print("  ✅ IC package identification (DIP/QFP/SOIC)")
    print("  ✅ Surface texture analysis")
    print("  ✅ Adaptive thresholding")
    print("  ✅ Professional visualization")
    print("="*70 + "\n")
    
    detector = UltraPreciseICDetector()
    detector.detect_webcam()


if __name__ == "__main__":
    main()
