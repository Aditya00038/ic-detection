"""
IC Chip Detection from Image File
Test with photos from your phone or any image file
"""

import cv2
import numpy as np
from ultralytics import YOLO
import argparse
from pathlib import Path

class ICImageDetector:
    """Detect IC chips in static images"""
    
    def __init__(self, model_path='yolov8s.pt', confidence=0.5):
        """Initialize detector"""
        print("🔧 Loading IC Chip Detector...")
        self.model = YOLO(model_path)
        self.confidence = confidence
        print(f"✓ Model loaded with confidence threshold: {confidence}")
    
    def is_ic_shape(self, width, height, roi=None):
        """Check if detection has IC-like rectangular shape - STRICT filtering"""
        # ICs must be a reasonable size (not too small, not too large)
        if width < 50 or height < 50:  # Too small
            return False
        
        if width > 400 or height > 400:  # Too large (probably not an IC)
            return False
        
        aspect_ratio = width / height
        
        # ICs are typically rectangular with specific ratios
        # Most ICs are either square-ish (1:1) or moderately rectangular (up to 2:1 or 1:2)
        # Reject very elongated objects
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:
            return False
        
        # Additional check: ICs should have reasonable area
        area = width * height
        if area < 2500 or area > 160000:  # Filter by area (50x50 to 400x400)
            return False
        
        # If we have the ROI, check if it looks rectangular with edges
        if roi is not None and roi.size > 0:
            try:
                # Convert to grayscale
                if len(roi.shape) == 3:
                    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                else:
                    gray = roi
                
                # Edge detection
                edges = cv2.Canny(gray, 50, 150)
                
                # Count edge pixels
                edge_pixel_count = np.count_nonzero(edges)
                total_pixels = gray.shape[0] * gray.shape[1]
                edge_ratio = edge_pixel_count / total_pixels
                
                # ICs should have clear rectangular edges (but not too many edges)
                if edge_ratio < 0.02 or edge_ratio > 0.3:
                    return False
                
                # Check for rectangular contours
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if len(contours) > 0:
                    # Find the largest contour
                    largest_contour = max(contours, key=cv2.contourArea)
                    
                    # Approximate the contour to a polygon
                    epsilon = 0.04 * cv2.arcLength(largest_contour, True)
                    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
                    
                    # ICs should have 4 corners (rectangular)
                    if len(approx) < 4 or len(approx) > 8:
                        return False
            except:
                pass  # If edge detection fails, rely on other checks
        
        return True
    
    def detect_ics(self, image_path):
        """Detect ICs in image"""
        print(f"\n📸 Loading image: {image_path}")
        
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"❌ Error: Could not read image from {image_path}")
            return None, []
        
        print(f"✓ Image loaded: {image.shape[1]}x{image.shape[0]} pixels")
        print(f"🔍 Detecting IC chips...")
        
        # Run detection
        results = self.model(image, conf=self.confidence, verbose=False)[0]
        
        ic_count = 0
        annotated = image.copy()
        detections = []
        
        # Process detections
        if results.boxes is not None and len(results.boxes) > 0:
            print(f"📊 Found {len(results.boxes)} potential objects")
            
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                
                # Extract region first
                x1_int = max(0, int(x1))
                y1_int = max(0, int(y1))
                x2_int = min(image.shape[1], int(x2))
                y2_int = min(image.shape[0], int(y2))
                roi = image[y1_int:y2_int, x1_int:x2_int]
                
                # Check IC shape with ROI for edge detection
                width, height = x2 - x1, y2 - y1
                if not self.is_ic_shape(width, height, roi):
                    continue
                
                # This is an IC!
                ic_count += 1
                
                # Draw detection
                color = (0, 255, 0)  # Green
                cv2.rectangle(annotated, (x1_int, y1_int), (x2_int, y2_int), color, 3)
                
                # Label
                label = f"IC CHIP #{ic_count}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7
                thickness = 2
                
                (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, thickness)
                
                # Draw background for text
                cv2.rectangle(annotated, 
                             (x1_int, y1_int - text_height - 10),
                             (x1_int + text_width + 10, y1_int),
                             color, -1)
                
                # Draw text
                cv2.putText(annotated, label, (x1_int + 5, y1_int - 5),
                           font, font_scale, (255, 255, 255), thickness)
                
                # Store detection info
                detections.append({
                    'id': ic_count,
                    'confidence': conf,
                    'box': [x1_int, y1_int, x2_int, y2_int],
                    'size': f"{int(width)}x{int(height)}"
                })
        
        return annotated, detections
    
    def display_results(self, image, detections, image_path):
        """Display detection results"""
        if len(detections) == 0:
            print("\n" + "="*50)
            print("❌ NO IC DETECTED!")
            print("❌ IC is not present in this image")
            print("="*50)
            
            # Draw warning on image
            height, width = image.shape[:2]
            overlay = image.copy()
            cv2.rectangle(overlay, (0, 0), (width, 150), (0, 0, 255), -1)
            cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image, "NO IC DETECTED!", (50, 70),
                       font, 2, (0, 0, 255), 4)
            cv2.putText(image, "IC is not present", (50, 120),
                       font, 1.2, (0, 0, 255), 3)
        else:
            print("\n" + "="*50)
            print(f"✅ DETECTED {len(detections)} IC CHIP(S)!")
            print("="*50)
            
            for det in detections:
                print(f"\nIC #{det['id']}:")
                print(f"  Size: {det['size']} pixels")
                print(f"  Confidence: {det['confidence']:.2f}")
                print(f"  Location: {det['box']}")
        
        # Save result
        output_path = Path(image_path).parent / f"detected_{Path(image_path).name}"
        cv2.imwrite(str(output_path), image)
        print(f"\n💾 Result saved to: {output_path}")
        
        # Display
        print("\n👁️  Displaying result (press any key to close)...")
        
        # Resize if too large
        max_display_size = 1200
        h, w = image.shape[:2]
        if w > max_display_size or h > max_display_size:
            scale = max_display_size / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            display_image = cv2.resize(image, (new_w, new_h))
        else:
            display_image = image
        
        cv2.imshow('IC Detection Result', display_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        description='IC Chip Detection from Image',
        epilog='Example: python detect_ic_image.py --image photo.jpg'
    )
    parser.add_argument('--image', '-i', type=str, required=True,
                       help='Path to image file (from phone or camera)')
    parser.add_argument('--model', type=str, default='yolov8s.pt',
                       help='YOLO model path')
    parser.add_argument('--conf', type=float, default=0.5,
                       help='Confidence threshold (0.1-0.9, default: 0.5)')
    
    args = parser.parse_args()
    
    # Check if image exists
    if not Path(args.image).exists():
        print(f"❌ Error: Image file not found: {args.image}")
        print("\n💡 Tips:")
        print("  1. Transfer photo from phone to computer")
        print("  2. Put image in: d:\\SIH PS-162\\ic-detection-yolo\\")
        print("  3. Run: python detect_ic_image.py --image yourphoto.jpg")
        return
    
    # Initialize detector
    detector = ICImageDetector(model_path=args.model, confidence=args.conf)
    
    # Detect ICs
    result_image, detections = detector.detect_ics(args.image)
    
    if result_image is not None:
        # Display results
        detector.display_results(result_image, detections, args.image)
    
    print("\n✅ Done!")


if __name__ == '__main__':
    main()
