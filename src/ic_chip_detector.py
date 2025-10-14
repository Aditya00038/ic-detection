"""
IC Chip Detection and Text Recognition System
Detects electronic ICs and reads chip names/part numbers using OCR
"""

import cv2
import numpy as np
from ultralytics import YOLO
import pytesseract
import re
from pathlib import Path
import json
from datetime import datetime

# Configure Tesseract path (update if needed)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ICChipDetector:
    """Detects electronic ICs and extracts chip information"""
    
    # Common IC manufacturers and their patterns
    IC_MANUFACTURERS = {
        'TEXAS INSTRUMENTS': ['TI', 'TL', 'TPS', 'LM', 'SN', 'CD', 'UC'],
        'ANALOG DEVICES': ['AD', 'ADI', 'ADP', 'ADM'],
        'MAXIM': ['MAX', 'DS'],
        'LINEAR TECHNOLOGY': ['LT', 'LTC'],
        'MICROCHIP': ['PIC', 'DSPIC', 'MCP', 'AT'],
        'ATMEL': ['AT', 'ATMEGA', 'ATTINY'],
        'STM': ['STM32', 'STM8', 'ST'],
        'NXP': ['LPC', 'MK', 'i.MX'],
        'INFINEON': ['IR', 'IRL', 'XMC'],
        'ONSEMI': ['ON', 'MC'],
        'INTEL': ['8086', '8088', 'i3', 'i5', 'i7'],
        'AMD': ['RYZEN', 'ATHLON'],
        'FAIRCHILD': ['FAN', 'FQP'],
        'VISHAY': ['SI', 'SUM'],
        'ROHM': ['BA', 'BD'],
        'TOSHIBA': ['TA', 'TB'],
        'RENESAS': ['R5F', 'RX'],
        'CYPRESS': ['CY'],
        'XILINX': ['XC'],
        'ALTERA': ['EP'],
        'BROADCOM': ['BCM'],
        'QUALCOMM': ['QCA', 'MSM'],
        'SAMSUNG': ['EXYNOS', 'K4'],
        'HYNIX': ['H5'],
        'MICRON': ['MT'],
    }
    
    def __init__(self, model_path='yolov8s.pt', confidence=0.5):
        """
        Initialize IC Chip Detector
        
        Args:
            model_path: Path to YOLO model
            confidence: Minimum confidence threshold
        """
        print("🔧 Initializing IC Chip Detector...")
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.detection_count = 0
        
        # Check if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
            self.ocr_available = True
            print("✓ Tesseract OCR available")
        except:
            self.ocr_available = False
            print("⚠ Tesseract OCR not found. Text recognition disabled.")
            print("  Install: https://github.com/UB-Mannheim/tesseract/wiki")
    
    def detect_objects(self, image):
        """
        Run YOLO detection on image
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            YOLO results object
        """
        results = self.model(image, conf=self.confidence, verbose=False)
        return results[0]
    
    def is_ic_like_object(self, box_width, box_height, aspect_ratio):
        """
        Check if detected object has IC-like dimensions
        
        ICs are typically rectangular with specific aspect ratios
        
        Args:
            box_width: Width of bounding box
            box_height: Height of bounding box
            aspect_ratio: Width/Height ratio
            
        Returns:
            bool: True if object looks like an IC
        """
        # ICs are usually rectangular
        # Common IC aspect ratios: 1:1 to 3:1 or 1:3
        if 0.3 < aspect_ratio < 3.0:
            # Minimum size check (avoid tiny detections)
            if box_width > 30 and box_height > 30:
                return True
        return False
    
    def preprocess_for_ocr(self, roi):
        """
        Preprocess image region for better OCR
        
        Args:
            roi: Region of interest (cropped IC image)
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi.copy()
        
        # Resize for better OCR (make text larger)
        scale = 3
        resized = cv2.resize(gray, None, fx=scale, fy=scale, 
                           interpolation=cv2.INTER_CUBIC)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(resized)
        
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def extract_text_from_ic(self, roi):
        """
        Extract text from IC region using OCR
        
        Args:
            roi: Region of interest (cropped IC image)
            
        Returns:
            Extracted text string
        """
        if not self.ocr_available:
            return ""
        
        try:
            # Preprocess image
            processed = self.preprocess_for_ocr(roi)
            
            # OCR with custom config
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
            text = pytesseract.image_to_string(processed, config=custom_config)
            
            # Clean up text
            text = text.strip().upper()
            text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
            
            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
    
    def identify_manufacturer(self, text):
        """
        Identify IC manufacturer from text
        
        Args:
            text: Extracted text from IC
            
        Returns:
            tuple: (manufacturer_name, part_number) or (None, None)
        """
        if not text:
            return None, None
        
        # Check against known manufacturers
        for manufacturer, prefixes in self.IC_MANUFACTURERS.items():
            for prefix in prefixes:
                # Look for exact prefix match
                pattern = r'\b' + re.escape(prefix) + r'[A-Z0-9\-]+'
                matches = re.findall(pattern, text)
                if matches:
                    part_number = matches[0]
                    return manufacturer, part_number
        
        # If no exact match, try to extract any alphanumeric part number
        part_numbers = re.findall(r'[A-Z]{2,}[0-9]{2,}', text)
        if part_numbers:
            return "UNKNOWN MANUFACTURER", part_numbers[0]
        
        return None, None
    
    def draw_ic_detection(self, image, box, ic_info, color=(0, 255, 0)):
        """
        Draw bounding box and IC information on image
        
        Args:
            image: Image to draw on
            box: Bounding box coordinates [x1, y1, x2, y2]
            ic_info: Dictionary with IC information
            color: RGB color tuple
        """
        x1, y1, x2, y2 = map(int, box)
        
        # Draw bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # Prepare text information
        manufacturer = ic_info.get('manufacturer', 'Unknown')
        part_number = ic_info.get('part_number', 'N/A')
        confidence = ic_info.get('confidence', 0)
        
        # Create info text
        if manufacturer and manufacturer != "UNKNOWN MANUFACTURER":
            info_text = f"{manufacturer}"
            part_text = f"{part_number}"
        else:
            info_text = "IC DETECTED"
            part_text = part_number if part_number and part_number != 'N/A' else ""
        
        conf_text = f"Conf: {confidence:.2f}"
        
        # Calculate text background size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        
        # Get text sizes
        (w1, h1), _ = cv2.getTextSize(info_text, font, font_scale, thickness)
        (w2, h2), _ = cv2.getTextSize(part_text, font, font_scale, thickness)
        (w3, h3), _ = cv2.getTextSize(conf_text, font, font_scale-0.1, thickness-1)
        
        max_width = max(w1, w2, w3)
        total_height = h1 + h2 + h3 + 20
        
        # Draw background rectangle
        cv2.rectangle(image, 
                     (x1, y1 - total_height - 10), 
                     (x1 + max_width + 10, y1),
                     color, -1)
        
        # Draw text
        y_offset = y1 - total_height
        cv2.putText(image, info_text, (x1 + 5, y_offset + h1), 
                   font, font_scale, (255, 255, 255), thickness)
        
        if part_text:
            cv2.putText(image, part_text, (x1 + 5, y_offset + h1 + h2 + 5), 
                       font, font_scale, (255, 255, 255), thickness)
        
        cv2.putText(image, conf_text, (x1 + 5, y_offset + h1 + h2 + h3 + 10), 
                   font, font_scale-0.1, (255, 255, 255), thickness-1)
    
    def detect_and_recognize(self, image, filter_ic_only=True):
        """
        Detect ICs and recognize text on them
        
        Args:
            image: Input image
            filter_ic_only: If True, only show IC-like objects
            
        Returns:
            tuple: (annotated_image, ic_detections_list)
        """
        # Run YOLO detection
        results = self.detect_objects(image)
        
        ic_detections = []
        annotated_image = image.copy()
        
        # Process each detection
        if results.boxes is not None and len(results.boxes) > 0:
            for i, box in enumerate(results.boxes):
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                
                # Calculate dimensions
                width = x2 - x1
                height = y2 - y1
                aspect_ratio = width / height if height > 0 else 0
                
                # Check if object looks like an IC
                if filter_ic_only:
                    if not self.is_ic_like_object(width, height, aspect_ratio):
                        continue
                
                # Extract IC region
                x1_int, y1_int = max(0, int(x1)), max(0, int(y1))
                x2_int, y2_int = min(image.shape[1], int(x2)), min(image.shape[0], int(y2))
                ic_roi = image[y1_int:y2_int, x1_int:x2_int]
                
                # Extract text from IC
                ic_text = self.extract_text_from_ic(ic_roi)
                
                # Identify manufacturer
                manufacturer, part_number = self.identify_manufacturer(ic_text)
                
                # Create IC info dictionary
                ic_info = {
                    'box': [x1, y1, x2, y2],
                    'confidence': confidence,
                    'raw_text': ic_text,
                    'manufacturer': manufacturer,
                    'part_number': part_number,
                    'width': width,
                    'height': height,
                    'aspect_ratio': aspect_ratio
                }
                
                ic_detections.append(ic_info)
                
                # Draw on image
                color = (0, 255, 0) if manufacturer else (255, 165, 0)
                self.draw_ic_detection(annotated_image, [x1, y1, x2, y2], ic_info, color)
        
        return annotated_image, ic_detections
    
    def save_results(self, image, detections, output_dir='results'):
        """
        Save detection results
        
        Args:
            image: Annotated image
            detections: List of IC detections
            output_dir: Output directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save image
        image_path = output_path / f"ic_detection_{timestamp}.jpg"
        cv2.imwrite(str(image_path), image)
        
        # Save JSON report
        report = {
            'timestamp': timestamp,
            'total_ics_detected': len(detections),
            'detections': []
        }
        
        for i, det in enumerate(detections):
            report['detections'].append({
                'id': i + 1,
                'manufacturer': det.get('manufacturer', 'Unknown'),
                'part_number': det.get('part_number', 'N/A'),
                'confidence': det.get('confidence', 0),
                'raw_text': det.get('raw_text', ''),
                'dimensions': {
                    'width': det.get('width', 0),
                    'height': det.get('height', 0),
                    'aspect_ratio': det.get('aspect_ratio', 0)
                }
            })
        
        json_path = output_path / f"ic_report_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=4)
        
        print(f"\n✓ Results saved:")
        print(f"  Image: {image_path}")
        print(f"  Report: {json_path}")
        
        return str(image_path), str(json_path)


def main():
    """Demo of IC chip detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IC Chip Detection and Recognition')
    parser.add_argument('--source', type=str, required=True, help='Image path or camera ID')
    parser.add_argument('--model', type=str, default='yolov8s.pt', help='YOLO model path')
    parser.add_argument('--conf', type=float, default=0.3, help='Confidence threshold')
    parser.add_argument('--save', action='store_true', help='Save results')
    parser.add_argument('--show-all', action='store_true', help='Show all objects, not just ICs')
    
    args = parser.parse_args()
    
    # Initialize detector
    detector = ICChipDetector(model_path=args.model, confidence=args.conf)
    
    # Check if source is camera or image
    try:
        camera_id = int(args.source)
        is_camera = True
    except:
        is_camera = False
    
    if is_camera:
        # Camera mode
        print(f"\n📹 Opening camera {camera_id}...")
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        print("\n✓ Camera opened. Press 'q' to quit, 's' to save screenshot\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect and recognize ICs
            result_image, detections = detector.detect_and_recognize(
                frame, 
                filter_ic_only=not args.show_all
            )
            
            # Add info overlay
            info_text = f"ICs Detected: {len(detections)}"
            cv2.putText(result_image, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display
            cv2.imshow('IC Chip Detection', result_image)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s') and len(detections) > 0:
                detector.save_results(result_image, detections)
                print("📸 Screenshot saved!")
        
        cap.release()
        cv2.destroyAllWindows()
    
    else:
        # Image mode
        print(f"\n📷 Processing image: {args.source}")
        image = cv2.imread(args.source)
        
        if image is None:
            print(f"❌ Error: Could not read image from {args.source}")
            return
        
        # Detect and recognize ICs
        result_image, detections = detector.detect_and_recognize(
            image,
            filter_ic_only=not args.show_all
        )
        
        # Print results
        print(f"\n✓ Detection complete!")
        print(f"📊 Total ICs detected: {len(detections)}\n")
        
        if len(detections) == 0:
            print("⚠ NO IC DETECTED IN IMAGE")
            print("❌ IC is not present")
        else:
            for i, det in enumerate(detections, 1):
                print(f"IC #{i}:")
                print(f"  Manufacturer: {det.get('manufacturer', 'Unknown')}")
                print(f"  Part Number: {det.get('part_number', 'N/A')}")
                print(f"  Confidence: {det.get('confidence', 0):.2f}")
                print(f"  Raw Text: {det.get('raw_text', 'N/A')}")
                print()
        
        # Save if requested
        if args.save:
            detector.save_results(result_image, detections)
        
        # Display
        cv2.imshow('IC Chip Detection', result_image)
        print("\nPress any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
