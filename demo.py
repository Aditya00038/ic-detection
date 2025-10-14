"""
Simple Demo Script for IC Detection
Quick test without needing a trained model
"""

import cv2
import numpy as np
from ultralytics import YOLO
import argparse
from pathlib import Path

def demo_image(image_path, model_name='yolov8s.pt'):
    """Demo detection on single image"""
    print(f"🎯 IC Detection Demo")
    print(f"=" * 50)
    print(f"Model: {model_name}")
    print(f"Image: {image_path}")
    print(f"=" * 50)
    
    # Load model
    print("\n📥 Loading model...")
    model = YOLO(model_name)
    print("✓ Model loaded")
    
    # Read image
    print(f"\n📸 Reading image...")
    image = cv2.imread(image_path)
    if image is None:
        print(f"✗ Could not read image: {image_path}")
        return
    
    h, w = image.shape[:2]
    print(f"✓ Image loaded: {w}x{h}")
    
    # Detect
    print(f"\n🔍 Detecting...")
    results = model.predict(source=image, conf=0.25, verbose=False)[0]
    
    # Process results
    boxes = results.boxes
    num_detections = len(boxes) if boxes is not None else 0
    
    print(f"✓ Detection complete!")
    print(f"  Found: {num_detections} object(s)")
    
    # Draw boxes
    if num_detections > 0:
        annotated = image.copy()
        
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            
            # Draw rectangle
            cv2.rectangle(annotated, (int(x1), int(y1)), (int(x2), int(y2)), 
                         (0, 255, 0), 2)
            
            # Draw label
            label = f"Object {i+1}: {conf:.2f}"
            cv2.putText(annotated, label, (int(x1), int(y1) - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            print(f"\n  Detection {i+1}:")
            print(f"    Confidence: {conf:.2%}")
            print(f"    BBox: ({int(x1)}, {int(y1)}) to ({int(x2)}, {int(y2)})")
            print(f"    Size: {int(x2-x1)}x{int(y2-y1)}")
        
        # Save result
        output_path = f"demo_result_{Path(image_path).stem}.jpg"
        cv2.imwrite(output_path, annotated)
        print(f"\n✓ Result saved: {output_path}")
        
        # Display
        print(f"\n👁 Displaying result (press any key to close)...")
        
        # Resize for display if too large
        display_img = annotated.copy()
        if max(h, w) > 1200:
            scale = 1200 / max(h, w)
            display_img = cv2.resize(display_img, None, fx=scale, fy=scale)
        
        cv2.imshow('IC Detection Demo', display_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    else:
        print("\n⚠ No objects detected")
        print("  Try:")
        print("  - Using a clearer image")
        print("  - Lowering confidence threshold: --conf 0.1")
        print("  - Training a custom model for IC detection")

def demo_webcam(model_name='yolov8s.pt', conf=0.25):
    """Demo detection on webcam"""
    print(f"🎥 Webcam IC Detection Demo")
    print(f"=" * 50)
    print(f"Model: {model_name}")
    print(f"Confidence: {conf}")
    print(f"=" * 50)
    
    # Load model
    print("\n📥 Loading model...")
    model = YOLO(model_name)
    print("✓ Model loaded")
    
    # Open webcam
    print("\n📹 Opening webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("✗ Cannot open webcam")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"✓ Webcam opened: {width}x{height}")
    print("\n🎬 Starting detection...")
    print("  Press 'q' to quit")
    print("  Press 's' to save screenshot")
    
    screenshot_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect
            results = model.predict(source=frame, conf=conf, verbose=False)[0]
            
            # Draw results
            boxes = results.boxes
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0])
                    
                    # Draw box
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), 
                                (0, 255, 0), 2)
                    
                    # Draw label
                    label = f"{confidence:.2f}"
                    cv2.putText(frame, label, (int(x1), int(y1) - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Draw info
            num_det = len(boxes) if boxes is not None else 0
            info_text = f"Detections: {num_det} | Press Q to quit, S to save"
            cv2.putText(frame, info_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display
            cv2.imshow('IC Detection Demo - Webcam', frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"screenshot_{screenshot_count:04d}.jpg"
                cv2.imwrite(filename, frame)
                print(f"✓ Screenshot saved: {filename}")
                screenshot_count += 1
    
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n✓ Webcam closed")

def main():
    parser = argparse.ArgumentParser(description='IC Detection Demo')
    parser.add_argument('--mode', type=str, default='image', 
                       choices=['image', 'webcam'],
                       help='Demo mode: image or webcam')
    parser.add_argument('--source', type=str, default='test.jpg',
                       help='Image path (for image mode)')
    parser.add_argument('--model', type=str, default='yolov8s.pt',
                       help='Model name (yolov8n/s/m/l/x.pt)')
    parser.add_argument('--conf', type=float, default=0.25,
                       help='Confidence threshold')
    
    args = parser.parse_args()
    
    if args.mode == 'image':
        if not Path(args.source).exists():
            print(f"✗ Image not found: {args.source}")
            print("\nUsage:")
            print(f"  python demo.py --mode image --source your_image.jpg")
            return
        demo_image(args.source, args.model)
    
    elif args.mode == 'webcam':
        demo_webcam(args.model, args.conf)

if __name__ == '__main__':
    main()
