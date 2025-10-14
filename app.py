"""
Flask Web App for IC Detection
Users upload images and get IC detection results
Can be deployed on Render, Railway, or Heroku
"""

from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
from ultralytics import YOLO
import base64
import io
from PIL import Image

app = Flask(__name__)

# Load YOLO model
print("Loading YOLO model...")
model = YOLO('yolov8n.pt')
print("Model loaded!")

def detect_ic_in_image(image):
    """Detect ICs in uploaded image"""
    # Convert PIL to OpenCV
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    h, w = img.shape[:2]
    
    # Run YOLO
    results = model(img, conf=0.15, verbose=False)
    
    detections = []
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            width = x2 - x1
            height = y2 - y1
            area = width * height
            
            if area < 1000 or area > 250000:
                continue
            
            aspect = width / height if height > 0 else 0
            if aspect < 0.2 or aspect > 8:
                continue
            
            # Validate IC
            roi = img[y1:y2, x1:x2]
            if roi.size == 0:
                continue
            
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray_roi)
            
            if brightness > 180:
                continue
            
            edges = cv2.Canny(gray_roi, 40, 120)
            edge_density = np.count_nonzero(edges) / edges.size
            
            if edge_density < 0.02:
                continue
            
            score = 0
            if brightness < 160:
                score += 2
            if edge_density > 0.05:
                score += 3
            
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=15, 
                                   minLineLength=8, maxLineGap=3)
            if lines is not None and len(lines) >= 6:
                score += 2
            
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv_roi[:, :, 1])
            if saturation < 80:
                score += 2
            
            circles = cv2.HoughCircles(gray_roi, cv2.HOUGH_GRADIENT, 
                                      dp=1, minDist=20, param1=50, param2=30,
                                      minRadius=5, maxRadius=50)
            if circles is not None and len(circles[0]) >= 2:
                continue
            
            if score >= 5:
                confidence = (score / 9) * 100
                
                # Draw detection
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                label = f"IC {confidence:.0f}%"
                cv2.putText(img, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                detections.append({
                    'x': x1, 'y': y1, 'width': width, 'height': height,
                    'confidence': round(confidence, 1)
                })
    
    # Convert back to PIL
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    output_image = Image.fromarray(img_rgb)
    
    return output_image, detections

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    
    # Read image
    image = Image.open(file.stream)
    
    # Detect ICs
    output_image, detections = detect_ic_in_image(image)
    
    # Convert to base64
    buffered = io.BytesIO()
    output_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({
        'success': True,
        'detections': detections,
        'image': f"data:image/jpeg;base64,{img_str}",
        'count': len(detections)
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
