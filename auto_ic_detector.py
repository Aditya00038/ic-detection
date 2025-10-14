"""
🚀 AUTO IC DETECTOR - NO MENU, INSTANT START
Just run and point at IC chip!
"""

import cv2
import numpy as np

print("\n" + "="*70)
print("🚀 AUTO IC DETECTOR - STARTING WEBCAM...")
print("="*70)
print("✅ Detects dark rectangular objects (IC chips)")
print("✅ Very permissive - will detect easily!")
print("="*70)
print("\n📸 Controls:")
print("   Q - Quit")
print("   + - More sensitive (detect smaller ICs)")
print("   - - Less sensitive (detect larger ICs only)")
print("="*70 + "\n")

# Settings
sensitivity = 8  # High sensitivity (1-10)
min_area = 500   # Very small minimum
max_area = 300000

print("🎥 Opening webcam...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ ERROR: Cannot open webcam!")
    print("💡 Make sure:")
    print("   - Webcam is connected")
    print("   - No other app is using it")
    input("\nPress Enter to exit...")
    exit()

print("✅ Webcam started!")
print("\n🎯 Point at any IC chip and it will detect it!")
print("="*70 + "\n")

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Cannot read frame!")
        break
    
    frame_count += 1
    
    # === SIMPLE DETECTION ===
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Find dark objects
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Thicken edges
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    ic_count = 0
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Adjust for sensitivity
        adjusted_min = 2500 - (sensitivity * 200)
        
        if area < adjusted_min or area > max_area:
            continue
        
        # Get box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Check aspect ratio
        aspect = float(w) / h if h > 0 else 0
        if aspect < 0.1 or aspect > 10:
            continue
        
        # Check if too small
        if w < 20 or h < 20:
            continue
        
        # Get ROI
        roi = frame[y:y+h, x:x+w]
        if roi.size == 0:
            continue
        
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray_roi)
        
        # Skip if too bright (face/white object)
        if brightness > 180:
            continue
        
        # Check if has some edges
        edges = cv2.Canny(gray_roi, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        
        # Need at least some edges
        if edge_density < 0.01:
            continue
        
        # DETECTED! Draw it
        ic_count += 1
        
        # Draw green box
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        
        # Calculate confidence
        confidence = 60 + min(40, int(edge_density * 400))
        
        # Label
        label = f"IC {confidence}%"
        
        # Text background
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        cv2.rectangle(frame, (x, y - lh - 10), (x + lw, y), (0, 255, 0), -1)
        
        # Text
        cv2.putText(frame, label, (x, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # === DRAW INFO ===
    # Top bar
    info_h = 90
    info_bar = np.zeros((info_h, frame.shape[1], 3), dtype=np.uint8)
    
    # IC count
    cv2.putText(info_bar, f"ICs Detected: {ic_count}", 
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    # Sensitivity
    cv2.putText(info_bar, f"Sensitivity: {sensitivity}/10", 
               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Tips
    if ic_count == 0:
        cv2.putText(info_bar, "TIP: Press + to detect smaller objects", 
                   (400, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(info_bar, "TIP: Move IC closer to camera", 
                   (400, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # Combine
    output = np.vstack([info_bar, frame])
    
    # Show
    cv2.imshow('IC Detection', output)
    
    # Handle keys
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q') or key == ord('Q'):
        print("\n✅ Detection stopped by user")
        break
    elif key == ord('+') or key == ord('='):
        if sensitivity < 10:
            sensitivity += 1
            print(f"📈 Sensitivity increased: {sensitivity}/10 (will detect smaller ICs)")
    elif key == ord('-') or key == ord('_'):
        if sensitivity > 1:
            sensitivity -= 1
            print(f"📉 Sensitivity decreased: {sensitivity}/10 (larger ICs only)")
    elif key == ord('s') or key == ord('S'):
        filename = f"ic_screenshot_{frame_count}.jpg"
        cv2.imwrite(filename, output)
        print(f"📸 Screenshot saved: {filename}")

cap.release()
cv2.destroyAllWindows()

print("\n" + "="*70)
print("✅ IC Detection closed")
print("="*70)
