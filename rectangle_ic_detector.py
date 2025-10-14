"""
🔲 RECTANGLE-BASED IC DETECTION
Focuses on detecting rectangular shapes first, then validates as IC
Simple & Effective approach
"""

import cv2
import numpy as np
from ultralytics import YOLO

class RectangleICDetector:
    def __init__(self):
        print("\n" + "="*60)
        print("🔲 RECTANGLE-BASED IC DETECTION")
        print("="*60)
        print("Strategy:")
        print("  1️⃣  Find ALL rectangles in frame")
        print("  2️⃣  Check if rectangle looks like IC")
        print("  3️⃣  Show only IC rectangles")
        print("="*60)
        
        print("\n🚀 Loading YOLO model...")
        self.model = YOLO('yolov8n.pt')
        print("✅ Model loaded!\n")
        
        # Detection parameters
        self.conf_threshold = 0.25  # Medium confidence
        self.min_area = 1500        # Min rectangle area (smaller = more detection)
        self.max_area = 200000      # Max rectangle area
        
        # Sensitivity (1-10 scale, default 7)
        self.sensitivity = 7
        
    def find_rectangles(self, frame):
        """Find all rectangular contours in frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while keeping edges
        blurred = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Use Canny edge detection
        edges = cv2.Canny(blurred, 30, 150)
        
        # Dilate edges to close gaps
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangles = []
        for contour in contours:
            # Get area
            area = cv2.contourArea(contour)
            if area < self.min_area or area > self.max_area:
                continue
            
            # Approximate contour to polygon
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
            
            # Check if it's a rectangle (4 corners)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                
                # Check aspect ratio (width:height should be reasonable for IC)
                aspect_ratio = float(w) / h if h > 0 else 0
                if 0.2 < aspect_ratio < 5.0:  # Not too thin or too wide
                    rectangles.append({
                        'contour': approx,
                        'bbox': (x, y, w, h),
                        'area': area,
                        'aspect_ratio': aspect_ratio
                    })
        
        return rectangles
    
    def is_ic_rectangle(self, frame, rect_info):
        """Check if rectangle looks like an IC chip"""
        x, y, w, h = rect_info['bbox']
        
        # Extract ROI
        roi = frame[y:y+h, x:x+w]
        if roi.size == 0:
            return False, 0
        
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        score = 0
        max_score = 10
        
        # Check 1: NOT too bright (faces are bright)
        brightness = np.mean(gray_roi)
        if brightness > 170:
            return False, 0
        if brightness < 140:  # Dark objects like ICs
            score += 2
        
        # Check 2: Has texture/edges (ICs have pins, text, components)
        edges = cv2.Canny(gray_roi, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        if edge_density > 0.05:  # Has detail
            score += 2
        if edge_density < 0.02:  # Too smooth (not IC)
            return False, 0
        
        # Check 3: Check for parallel lines (IC pins)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=20, minLineLength=10, maxLineGap=5)
        if lines is not None:
            num_lines = len(lines)
            if num_lines >= 4:  # Multiple lines = pins
                score += 2
            elif num_lines >= 2:
                score += 1
        
        # Check 4: Color check - ICs are usually dark/gray/black
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        saturation = np.mean(hsv_roi[:, :, 1])
        value = np.mean(hsv_roi[:, :, 2])
        
        if saturation < 100 and value < 180:  # Low saturation, not too bright
            score += 2
        
        # Check 5: NOT circular (faces/eyes are circular)
        circles = cv2.HoughCircles(gray_roi, cv2.HOUGH_GRADIENT, dp=1, 
                                   minDist=20, param1=50, param2=30, 
                                   minRadius=5, maxRadius=50)
        if circles is not None and len(circles[0]) >= 2:
            return False, 0  # Multiple circles = face
        score += 2  # No circles = good
        
        # Calculate confidence based on sensitivity
        confidence = (score / max_score) * 100
        
        # Adjust threshold based on sensitivity (1-10 scale)
        # Sensitivity 1 = 70% threshold (strict)
        # Sensitivity 10 = 40% threshold (permissive)
        threshold = 70 - (self.sensitivity * 3)
        
        return confidence >= threshold, confidence
    
    def detect_rectangles(self, frame):
        """Main detection function"""
        # Step 1: Find all rectangles
        rectangles = self.find_rectangles(frame)
        
        # Step 2: Filter rectangles that look like ICs
        ic_detections = []
        for rect in rectangles:
            is_ic, confidence = self.is_ic_rectangle(frame, rect)
            if is_ic:
                ic_detections.append({
                    'rect': rect,
                    'confidence': confidence
                })
        
        return ic_detections
    
    def draw_detections(self, frame, detections):
        """Draw detected IC rectangles on frame"""
        for detection in detections:
            rect = detection['rect']
            confidence = detection['confidence']
            x, y, w, h = rect['bbox']
            
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Draw label
            label = f"IC {confidence:.1f}%"
            label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            
            # Background for label
            cv2.rectangle(frame, (x, y - label_size[1] - 10), 
                         (x + label_size[0], y), (0, 255, 0), -1)
            
            # Text
            cv2.putText(frame, label, (x, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        return frame
    
    def run_webcam(self):
        """Run detection on webcam"""
        print("="*60)
        print("🎥 RECTANGLE IC DETECTION - WEBCAM MODE")
        print("="*60)
        print("📸 Controls:")
        print("   Q - Quit")
        print("   S - Save screenshot")
        print("   + - More sensitive (detect more)")
        print("   - - Less sensitive (detect less)")
        print("="*60)
        print(f"\n💡 Sensitivity: {self.sensitivity}/10")
        print("🎯 Point at any IC chip - it will find rectangles!")
        print("="*60)
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Cannot open webcam!")
            return
        
        print("\n🎥 Webcam started!\n")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Error: Cannot read frame!")
                break
            
            frame_count += 1
            
            # Detect every frame for smooth experience
            detections = self.detect_rectangles(frame)
            
            # Draw detections
            output_frame = self.draw_detections(frame.copy(), detections)
            
            # Add status info
            cv2.putText(output_frame, f"Rectangles Found: {len(detections)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(output_frame, f"Sensitivity: {self.sensitivity}/10", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('Rectangle IC Detection', output_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == ord('Q'):
                print("\n✅ Detection closed")
                break
            elif key == ord('s') or key == ord('S'):
                filename = f"ic_detection_{frame_count}.jpg"
                cv2.imwrite(filename, output_frame)
                print(f"📸 Screenshot saved: {filename}")
            elif key == ord('+') or key == ord('='):
                if self.sensitivity < 10:
                    self.sensitivity += 1
                    print(f"📈 Sensitivity increased: {self.sensitivity}/10")
            elif key == ord('-') or key == ord('_'):
                if self.sensitivity > 1:
                    self.sensitivity -= 1
                    print(f"📉 Sensitivity decreased: {self.sensitivity}/10")
        
        cap.release()
        cv2.destroyAllWindows()
    
    def run_image(self, image_path):
        """Run detection on static image"""
        print("="*60)
        print("🖼️  RECTANGLE IC DETECTION - IMAGE MODE")
        print("="*60)
        
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"❌ Error: Cannot load image: {image_path}")
            return
        
        print(f"✅ Image loaded: {image_path}")
        print("🔍 Detecting rectangles...")
        
        # Detect
        detections = self.detect_rectangles(frame)
        
        print(f"✅ Found {len(detections)} IC rectangles!")
        
        # Draw detections
        output_frame = self.draw_detections(frame.copy(), detections)
        
        # Show result
        cv2.imshow('Rectangle IC Detection', output_frame)
        print("\n📸 Press any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # Save result
        output_path = image_path.replace('.', '_detected.')
        cv2.imwrite(output_path, output_frame)
        print(f"💾 Result saved: {output_path}")

def main():
    detector = RectangleICDetector()
    
    print("\nChoose mode:")
    print("1. Webcam (recommended)")
    print("2. Image file")
    
    choice = input("\nEnter 1 or 2: ").strip()
    
    if choice == '1':
        detector.run_webcam()
    elif choice == '2':
        image_path = input("Enter image path: ").strip()
        detector.run_image(image_path)
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
