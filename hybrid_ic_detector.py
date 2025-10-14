"""
⚡ HYBRID IC DETECTOR - YOLO + EDGE DETECTION
Combines AI detection with edge-based validation
Most accurate approach for IC chips
"""

import cv2
import numpy as np
from ultralytics import YOLO

print("\n" + "="*70)
print("⚡ HYBRID IC DETECTOR - YOLO + EDGE DETECTION")
print("="*70)
print("Strategy: AI detection + Edge validation = Better accuracy")
print("="*70 + "\n")

print("🚀 Loading YOLO model...")
model = YOLO('yolov8n.pt')
print("✅ Model loaded!\n")

# Settings
sensitivity = 7
conf_threshold = 0.15  # Low YOLO confidence (we'll validate manually)

print("="*70)
print("📸 Controls:")
print("   Q - Quit")
print("   S - Save screenshot")
print("   + - More sensitive (detect more)")
print("   - - Less sensitive (stricter)")
print("="*70)
print(f"\n💡 Current Sensitivity: {sensitivity}/10")
print("🎯 Point at IC chip - hybrid detection will find it!")
print("="*70 + "\n")

print("🎥 Opening webcam...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Cannot open webcam!")
    input("Press Enter to exit...")
    exit()

print("✅ Webcam started!\n")

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    h, w = frame.shape[:2]
    
    # === STEP 1: YOLO Detection (find potential objects) ===
    results = model(frame, conf=conf_threshold, verbose=False)
    
    ic_detections = []
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            # Get coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            width = x2 - x1
            height = y2 - y1
            
            # Skip if too small or too large
            area = width * height
            if area < 1000 or area > 250000:
                continue
            
            # Skip if weird aspect ratio
            aspect = width / height if height > 0 else 0
            if aspect < 0.2 or aspect > 8:
                continue
            
            # Extract ROI
            roi = frame[y1:y2, x1:x2]
            if roi.size == 0:
                continue
            
            # === STEP 2: VALIDATE if it's actually an IC ===
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Initialize score
            score = 0
            max_score = 10
            reasons = []
            
            # Check 1: Brightness (ICs are usually dark, faces are bright)
            brightness = np.mean(gray_roi)
            if brightness < 160:  # Dark object
                score += 2
                reasons.append("dark")
            elif brightness > 180:  # Too bright - reject
                continue
            
            # Check 2: Edge density (ICs have pins, text, details)
            edges = cv2.Canny(gray_roi, 40, 120)
            edge_density = np.count_nonzero(edges) / edges.size
            
            if edge_density > 0.05:  # Good detail
                score += 3
                reasons.append("detailed")
            elif edge_density < 0.02:  # Too smooth - reject
                continue
            else:
                score += 1
            
            # Check 3: Lines detection (IC pins show as lines)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 
                                   threshold=15, minLineLength=8, maxLineGap=3)
            if lines is not None:
                num_lines = len(lines)
                if num_lines >= 6:
                    score += 2
                    reasons.append("pins")
                elif num_lines >= 3:
                    score += 1
            
            # Check 4: Color (ICs are low saturation - gray/black)
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv_roi[:, :, 1])
            
            if saturation < 80:  # Very low saturation
                score += 2
                reasons.append("metallic")
            elif saturation < 120:
                score += 1
            
            # Check 5: NO circular features (reject faces)
            circles = cv2.HoughCircles(gray_roi, cv2.HOUGH_GRADIENT, 
                                      dp=1, minDist=20, param1=50, param2=30,
                                      minRadius=5, maxRadius=50)
            if circles is not None and len(circles[0]) >= 2:
                continue  # Multiple circles = face, reject
            score += 1
            
            # Check 6: Rectangularity
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest = max(contours, key=cv2.contourArea)
                peri = cv2.arcLength(largest, True)
                approx = cv2.approxPolyDP(largest, 0.04 * peri, True)
                if len(approx) >= 4 and len(approx) <= 6:  # Rectangular-ish
                    score += 2
                    reasons.append("rectangular")
            
            # === DECISION: Adjust threshold based on sensitivity ===
            # Sensitivity 1 = 7/10 (70% strict)
            # Sensitivity 10 = 4/10 (40% permissive)
            threshold = 7 - (sensitivity * 0.3)
            
            confidence = (score / max_score) * 100
            
            if score >= threshold:
                ic_detections.append({
                    'box': (x1, y1, x2, y2),
                    'confidence': confidence,
                    'score': score,
                    'reasons': reasons
                })
    
    # === DRAW DETECTIONS ===
    output = frame.copy()
    
    for det in ic_detections:
        x1, y1, x2, y2 = det['box']
        confidence = det['confidence']
        
        # Draw thick green box
        cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        # Label with confidence only
        label = f"IC {confidence:.0f}%"
        
        # Background for label
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        cv2.rectangle(output, (x1, y1 - lh - 10), (x1 + lw + 10, y1), (0, 255, 0), -1)
        
        # Text
        cv2.putText(output, label, (x1 + 5, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # === INFO BAR ===
    info_h = 100
    info_bar = np.zeros((info_h, w, 3), dtype=np.uint8)
    
    # Detection count
    cv2.putText(info_bar, f"ICs Detected: {len(ic_detections)}", 
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    
    # Sensitivity
    cv2.putText(info_bar, f"Sensitivity: {sensitivity}/10", 
               (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Tips
    if len(ic_detections) == 0:
        cv2.putText(info_bar, "NO IC DETECTED - Press + for more sensitivity", 
                   (400, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(info_bar, "TIP: Hold IC in center, plain background, good light", 
                   (400, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    
    # Combine
    final = np.vstack([info_bar, output])
    
    # Show
    cv2.imshow('Hybrid IC Detection', final)
    
    # Keys
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q') or key == ord('Q'):
        print("\n✅ Detection stopped")
        break
    elif key == ord('s') or key == ord('S'):
        filename = f"ic_detected_{frame_count}.jpg"
        cv2.imwrite(filename, final)
        print(f"📸 Saved: {filename}")
    elif key == ord('+') or key == ord('='):
        if sensitivity < 10:
            sensitivity += 1
            print(f"📈 Sensitivity: {sensitivity}/10 - Will detect more objects")
    elif key == ord('-') or key == ord('_'):
        if sensitivity > 1:
            sensitivity -= 1
            print(f"📉 Sensitivity: {sensitivity}/10 - Stricter filtering")

cap.release()
cv2.destroyAllWindows()

print("\n" + "="*70)
print("✅ Hybrid IC Detection closed")
print("="*70)
print("\n💡 Tips for better detection:")
print("   - Use plain background (white paper)")
print("   - Good lighting")
print("   - Hold IC in center of frame")
print("   - IC should fill 20-40% of screen")
print("   - Press + to increase sensitivity if not detecting")
print("="*70 + "\n")
