"""
BALANCED IC DETECTOR - Easy Detection, Smart Rejection
Simple but effective IC detection
"""

import cv2
from ultralytics import YOLO
import numpy as np

class BalancedICDetector:
    def __init__(self):
        print("🚀 Loading Balanced IC Detection System...")
        self.model = YOLO('yolov8n.pt')  # Faster nano model
        print("✅ Model loaded!")
        
    def simple_ic_check(self, roi):
        """Simple but effective IC detection"""
        if roi.size == 0:
            return False, "Empty ROI", 0
        
        h, w = roi.shape[:2]
        if h < 40 or w < 40:
            return False, "Too small", 0
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        score = 0
        
        # 1. NOT too bright (reject faces) - CRITICAL
        brightness = np.mean(gray)
        if brightness > 170:
            return False, f"Too bright ({brightness:.0f}) - likely face", score
        score += 2
        
        # 2. Has edges (ICs have pins/components)
        edges = cv2.Canny(gray, 40, 120)
        edge_density = np.count_nonzero(edges) / edges.size
        if edge_density > 0.05:  # Has some edges
            score += 2
        
        # 3. NOT too smooth (reject faces)
        if edge_density < 0.03:
            return False, "Too smooth - not IC", score
        
        # 4. Check for circular features (reject faces)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=2, minDist=30,
                                   param1=50, param2=40, minRadius=8, maxRadius=min(w,h)//3)
        if circles is not None and len(circles[0]) >= 2:
            return False, "Circular features (face)", score
        score += 1
        
        # 5. Low color saturation (ICs are dark/metallic)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        saturation = np.mean(hsv[:,:,1])
        if saturation < 100:  # Low saturation
            score += 1
        
        # 6. Look for any parallel lines (IC pins)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=10,
                                minLineLength=int(min(h,w)*0.1), maxLineGap=5)
        
        if lines is not None and len(lines) >= 3:
            score += 2  # Bonus for having lines
        
        # Need at least 4/8 points
        confidence = (score / 8) * 100
        
        if score >= 4:
            return True, f"IC ({confidence:.0f}%)", score
        else:
            return False, f"Not IC ({confidence:.0f}%)", score
    
    def is_ic(self, box, frame):
        """Main IC check"""
        x1, y1, x2, y2 = map(int, box[:4])
        
        width = x2 - x1
        height = y2 - y1
        
        # Relaxed size check
        if width < 35 or height < 35:
            return False, "Too small", 0
        
        if width > 600 or height > 600:
            return False, "Too large", 0
        
        # Relaxed aspect ratio
        aspect = max(width, height) / min(width, height)
        if aspect > 8.0:
            return False, "Too elongated", 0
        
        # Extract ROI
        roi = frame[y1:y2, x1:x2]
        
        return self.simple_ic_check(roi)
    
    def draw_detection(self, frame, box, score, ic_num):
        """Draw simple detection box"""
        x1, y1, x2, y2 = map(int, box[:4])
        
        # Green box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        # IC number
        cv2.circle(frame, (x1-20, y1-20), 18, (0, 255, 0), -1)
        cv2.putText(frame, str(ic_num), (x1-27, y1-12),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Label
        label = f"IC #{ic_num}"
        cv2.putText(frame, label, (x1, y1-30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    def detect_webcam(self):
        """Simple webcam detection"""
        print("\n" + "="*60)
        print("🎥 BALANCED IC DETECTION - WEBCAM MODE")
        print("="*60)
        print("📸 Controls:")
        print("   Q - Quit")
        print("   S - Save screenshot")
        print("   + - More sensitive (detect more)")
        print("   - - Less sensitive (detect less)")
        print("="*60)
        print("\n💡 Just point at any IC chip - it will detect!")
        print("="*60 + "\n")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open webcam!")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        frame_count = 0
        confidence_threshold = 0.2  # Start low to detect more
        
        print("🎥 Webcam started! Show IC chip...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            display_frame = frame.copy()
            
            # Run detection
            results = self.model(frame, verbose=False, conf=confidence_threshold)
            
            ic_detections = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    is_ic, reason, score = self.is_ic(box.xyxy[0], frame)
                    
                    if is_ic:
                        ic_detections.append((box, score))
            
            # Draw all ICs
            for idx, (box, score) in enumerate(ic_detections, 1):
                self.draw_detection(display_frame, box.xyxy[0], score, idx)
            
            # Simple status
            status_h = 80
            status_bg = np.zeros((status_h, display_frame.shape[1], 3), dtype=np.uint8)
            status_bg[:] = (30, 30, 30)
            
            if len(ic_detections) > 0:
                status_text = f"✅ {len(ic_detections)} IC CHIP(S) DETECTED"
                color = (0, 255, 0)
            else:
                status_text = "⚠️ NO IC - Show IC chip to camera"
                color = (0, 200, 255)
            
            cv2.putText(status_bg, status_text, (20, 45),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
            
            # Sensitivity indicator
            sens_text = f"Sensitivity: {int((1-confidence_threshold)*10)}/10"
            cv2.putText(status_bg, sens_text, (display_frame.shape[1]-280, 45),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            display_frame = np.vstack([status_bg, display_frame])
            
            cv2.imshow('Balanced IC Detection', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"ic_{frame_count}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"📸 Saved: {filename}")
            elif key == ord('+') or key == ord('='):
                confidence_threshold = max(0.05, confidence_threshold - 0.05)
                print(f"📈 More sensitive: {int((1-confidence_threshold)*10)}/10")
            elif key == ord('-') or key == ord('_'):
                confidence_threshold = min(0.5, confidence_threshold + 0.05)
                print(f"📉 Less sensitive: {int((1-confidence_threshold)*10)}/10")
        
        cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Detection closed")
    
    def detect_image(self, image_path):
        """Detect IC in image"""
        print(f"\n📷 Analyzing: {image_path}")
        
        frame = cv2.imread(image_path)
        if frame is None:
            print("❌ Cannot read image!")
            return
        
        results = self.model(frame, verbose=False, conf=0.15)
        
        ic_count = 0
        for result in results:
            boxes = result.boxes
            for box in boxes:
                is_ic, reason, score = self.is_ic(box.xyxy[0], frame)
                
                if is_ic:
                    ic_count += 1
                    self.draw_detection(frame, box.xyxy[0], score, ic_count)
                    print(f"✅ IC #{ic_count}: {reason} (score: {score}/8)")
                else:
                    print(f"❌ Rejected: {reason}")
        
        if ic_count > 0:
            print(f"\n✅ FOUND {ic_count} IC(S)!")
        else:
            print("\n⚠️ NO ICs DETECTED")
        
        cv2.imshow('IC Detection Result', frame)
        print("\nPress any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    print("\n" + "="*60)
    print("⚡ BALANCED IC DETECTION")
    print("="*60)
    print("Simple & Effective:")
    print("  ✅ Detects ICs easily (relaxed detection)")
    print("  ✅ Rejects faces (brightness + circles)")
    print("  ✅ Fast performance (nano model)")
    print("  ✅ Adjustable sensitivity (+/- keys)")
    print("="*60 + "\n")
    
    detector = BalancedICDetector()
    
    print("Choose mode:")
    print("1. Webcam (recommended)")
    print("2. Image file")
    
    choice = input("\nEnter 1 or 2: ").strip()
    
    if choice == "1":
        detector.detect_webcam()
    elif choice == "2":
        path = input("Image path: ").strip().strip('"')
        detector.detect_image(path)
    else:
        # Auto-start webcam if invalid
        print("Starting webcam...")
        detector.detect_webcam()


if __name__ == "__main__":
    main()
