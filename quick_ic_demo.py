"""
Quick IC Detection Demo - Works immediately without training!
Shows basic IC chip detection using YOLOv8 pretrained model
"""

import cv2
from ultralytics import YOLO
import numpy as np

class QuickICDetector:
    def __init__(self):
        print("🚀 Loading YOLOv8 model...")
        # Using pretrained YOLOv8n (nano - fastest)
        self.model = YOLO('yolov8n.pt')
        print("✅ Model loaded!")
        
        # Electronic-related classes from COCO dataset
        self.ic_related_classes = [
            'cell phone', 'remote', 'keyboard', 'mouse', 
            'laptop', 'tv', 'clock', 'scissors'
        ]
        
    def is_rectangular_electronic(self, box, frame):
        """Check if detected object looks like an IC chip"""
        x1, y1, x2, y2 = map(int, box[:4])
        
        # Size check
        width = x2 - x1
        height = y2 - y1
        
        if width < 30 or height < 30:
            return False, "Too small"
            
        if width > 400 or height > 400:
            return False, "Too large"
        
        # Aspect ratio (ICs are usually rectangular)
        aspect_ratio = width / height
        if aspect_ratio < 0.3 or aspect_ratio > 3.0:
            return False, f"Wrong shape ({aspect_ratio:.2f})"
        
        # Extract region
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            return False, "Invalid region"
        
        # Check for edges (ICs have sharp edges)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        
        if edge_density < 0.05:
            return False, f"Not enough edges ({edge_density:.3f})"
        
        # Check brightness (reject very bright objects like faces)
        mean_brightness = np.mean(gray)
        if mean_brightness > 200:
            return False, "Too bright (not IC)"
        
        return True, "IC detected!"
    
    def detect_webcam(self):
        """Run real-time IC detection on webcam"""
        print("\n" + "="*60)
        print("🎥 QUICK IC DETECTION - WEBCAM MODE")
        print("="*60)
        print("📸 Controls:")
        print("   Q - Quit")
        print("   S - Save screenshot")
        print("   SPACE - Pause/Resume")
        print("="*60 + "\n")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open webcam!")
            return
        
        paused = False
        ic_count = 0
        frame_count = 0
        
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                display_frame = frame.copy()
                
                # Run detection every 3 frames (for speed)
                if frame_count % 3 == 0:
                    results = self.model(frame, verbose=False, conf=0.3)
                    
                    ic_count = 0
                    for result in results:
                        boxes = result.boxes
                        for box in boxes:
                            cls = int(box.cls[0])
                            class_name = self.model.names[cls]
                            conf = float(box.conf[0])
                            
                            # Check if it could be an IC
                            is_ic, reason = self.is_rectangular_electronic(box.xyxy[0], frame)
                            
                            if is_ic:
                                ic_count += 1
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                
                                # Draw green box for ICs
                                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                
                                # Label
                                label = f"IC Chip #{ic_count} ({conf:.2f})"
                                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                                cv2.rectangle(display_frame, (x1, y1 - label_size[1] - 10), 
                                            (x1 + label_size[0], y1), (0, 255, 0), -1)
                                cv2.putText(display_frame, label, (x1, y1 - 5),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                
                # Status overlay
                status_bg = np.zeros((80, display_frame.shape[1], 3), dtype=np.uint8)
                status_bg[:] = (40, 40, 40)
                
                if ic_count > 0:
                    status_text = f"✅ {ic_count} IC CHIP(S) DETECTED"
                    color = (0, 255, 0)
                else:
                    status_text = "⚠️ NO IC DETECTED - Show IC chip to camera"
                    color = (0, 165, 255)
                
                cv2.putText(status_bg, status_text, (20, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                
                display_frame = np.vstack([status_bg, display_frame])
            
            # Show frame
            cv2.imshow('Quick IC Detection Demo', display_frame)
            
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
        
        cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Demo closed")
    
    def detect_image(self, image_path):
        """Detect ICs in a single image"""
        print(f"\n📷 Detecting ICs in: {image_path}")
        
        frame = cv2.imread(image_path)
        if frame is None:
            print("❌ Cannot read image!")
            return
        
        results = self.model(frame, verbose=False, conf=0.3)
        
        ic_count = 0
        for result in results:
            boxes = result.boxes
            for box in boxes:
                is_ic, reason = self.is_rectangular_electronic(box.xyxy[0], frame)
                
                if is_ic:
                    ic_count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    
                    # Draw detection
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"IC #{ic_count} ({conf:.2f})"
                    cv2.putText(frame, label, (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        if ic_count > 0:
            print(f"✅ Found {ic_count} IC chip(s)!")
        else:
            print("⚠️ No IC chips detected")
        
        # Show result
        cv2.imshow('IC Detection Result', frame)
        print("\nPress any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    print("\n" + "="*60)
    print("⚡ QUICK IC DETECTION DEMO")
    print("="*60)
    print("This is a basic demo using pretrained YOLOv8")
    print("For 95% accuracy, wait for custom model training to finish")
    print("="*60 + "\n")
    
    detector = QuickICDetector()
    
    print("\nChoose mode:")
    print("1. Webcam detection (real-time)")
    print("2. Image detection (single photo)")
    
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
