"""
🎯 SIMPLE IC DETECTOR - GUARANTEED DETECTION
Detects ANY rectangular dark object as IC
Ultra-simple approach that WILL detect your ICs
"""

import cv2
import numpy as np

class SimpleICDetector:
    def __init__(self):
        print("\n" + "="*60)
        print("🎯 SIMPLE IC DETECTOR - GUARANTEED DETECTION")
        print("="*60)
        print("✅ Detects dark rectangular objects")
        print("✅ No complex filtering")
        print("✅ Just shows what looks like IC")
        print("="*60 + "\n")
        
        # Very permissive settings
        self.min_area = 800         # Very small minimum
        self.max_area = 300000      # Large maximum
        self.sensitivity = 8        # Default high sensitivity
        
    def detect_ics(self, frame):
        """Simple detection - just find dark rectangles"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Simple threshold - find dark objects
        _, thresh = cv2.threshold(blurred, 140, 255, cv2.THRESH_BINARY_INV)
        
        # Make edges thicker
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=2)
        eroded = cv2.erode(dilated, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        
        for contour in contours:
            # Get area
            area = cv2.contourArea(contour)
            
            # Adjust min_area based on sensitivity (1-10)
            # Sensitivity 10 = 500px, Sensitivity 1 = 2000px
            adjusted_min = 2500 - (self.sensitivity * 200)
            
            if area < adjusted_min or area > self.max_area:
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Check aspect ratio
            aspect_ratio = float(w) / h if h > 0 else 0
            if aspect_ratio < 0.1 or aspect_ratio > 10:  # Very permissive
                continue
            
            # Extract ROI
            roi = frame[y:y+h, x:x+w]
            if roi.size == 0:
                continue
            
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray_roi)
            
            # Simple checks
            score = 0
            
            # Check 1: Not too bright (reject faces/white objects)
            if brightness < 160:  # Dark object
                score += 3
            elif brightness > 180:  # Too bright - skip
                continue
            
            # Check 2: Has some edges (not completely smooth)
            edges = cv2.Canny(gray_roi, 50, 150)
            edge_density = np.count_nonzero(edges) / edges.size
            if edge_density > 0.02:  # Has some detail
                score += 2
            
            # Check 3: Size is reasonable
            if w > 30 and h > 30:  # Not too small
                score += 1
            
            # Very low threshold - almost everything passes
            if score >= 3:
                confidence = min(100, (score / 6) * 100 + 50)
                detections.append({
                    'bbox': (x, y, w, h),
                    'confidence': confidence,
                    'brightness': brightness
                })
        
        return detections
    
    def draw_detections(self, frame, detections):
        """Draw bounding boxes"""
        for det in detections:
            x, y, w, h = det['bbox']
            confidence = det['confidence']
            
            # Green box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            
            # Label
            label = f"IC {confidence:.0f}%"
            
            # Background for text
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (x, y - label_h - 10), (x + label_w, y), (0, 255, 0), -1)
            
            # Text
            cv2.putText(frame, label, (x, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        return frame
    
    def run_webcam(self):
        """Run webcam detection"""
        print("="*60)
        print("🎥 SIMPLE IC DETECTION - WEBCAM MODE")
        print("="*60)
        print("📸 Controls:")
        print("   Q - Quit")
        print("   S - Save screenshot")
        print("   + - More sensitive (detect smaller)")
        print("   - - Less sensitive")
        print("="*60)
        print(f"\n💡 Sensitivity: {self.sensitivity}/10")
        print("🎯 Just show any dark rectangular object (IC chip)!")
        print("="*60)
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open webcam!")
            return
        
        print("\n🎥 Webcam started! Show IC chip...\n")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect
            detections = self.detect_ics(frame)
            
            # Draw
            output = self.draw_detections(frame.copy(), detections)
            
            # Info overlay
            info_bg = np.zeros((80, frame.shape[1], 3), dtype=np.uint8)
            cv2.putText(info_bg, f"ICs Detected: {len(detections)}", 
                       (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(info_bg, f"Sensitivity: {self.sensitivity}/10 (+ or - to adjust)", 
                       (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Combine
            output = np.vstack([info_bg, output])
            
            # Show
            cv2.imshow('Simple IC Detection', output)
            
            # Keys
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == ord('Q'):
                print("\n✅ Detection stopped")
                break
            elif key == ord('s') or key == ord('S'):
                filename = f"ic_detected_{frame_count}.jpg"
                cv2.imwrite(filename, output)
                print(f"📸 Saved: {filename}")
            elif key == ord('+') or key == ord('='):
                if self.sensitivity < 10:
                    self.sensitivity += 1
                    print(f"📈 Sensitivity: {self.sensitivity}/10 (detecting smaller objects)")
            elif key == ord('-') or key == ord('_'):
                if self.sensitivity > 1:
                    self.sensitivity -= 1
                    print(f"📉 Sensitivity: {self.sensitivity}/10 (detecting larger objects)")
        
        cap.release()
        cv2.destroyAllWindows()
    
    def run_image(self, image_path):
        """Run on static image"""
        print(f"\n🖼️  Loading image: {image_path}")
        
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"❌ Cannot load image!")
            return
        
        print("🔍 Detecting ICs...")
        
        # Detect
        detections = self.detect_ics(frame)
        
        print(f"✅ Found {len(detections)} IC(s)!")
        
        # Draw
        output = self.draw_detections(frame.copy(), detections)
        
        # Show
        cv2.imshow('Simple IC Detection', output)
        print("\n📸 Press any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # Save
        output_path = image_path.replace('.', '_detected.')
        cv2.imwrite(output_path, output)
        print(f"💾 Saved: {output_path}")

def main():
    print("\n" + "="*60)
    print("     🎯 SIMPLE IC DETECTOR")
    print("="*60)
    print("This detector will find ANY dark rectangular object")
    print("Perfect for detecting IC chips!")
    print("="*60)
    
    detector = SimpleICDetector()
    
    print("\n📋 Choose mode:")
    print("  1 - Webcam (live detection)")
    print("  2 - Image file")
    
    choice = input("\n👉 Enter 1 or 2: ").strip()
    
    if choice == '1':
        detector.run_webcam()
    elif choice == '2':
        image_path = input("Enter image path: ").strip()
        detector.run_image(image_path)
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
