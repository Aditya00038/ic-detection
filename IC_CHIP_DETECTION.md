# 🔬 IC Chip Detection System

**Electronic IC (Integrated Circuit) Detection with Brand/Part Number Recognition**

---

## 🎯 What This Does

This system detects **electronic IC chips** in images/video and:
- ✅ Detects only IC-shaped objects (filters out non-ICs)
- ✅ Shows "**IC is not present**" error if no IC detected
- ✅ Reads text on IC chips (brand names, part numbers)
- ✅ Identifies IC manufacturers (Texas Instruments, Analog Devices, etc.)
- ✅ Shows IC name and company/brand name

---

## 🚀 Quick Start

### Option 1: Basic Detection (No OCR)
```powershell
# Works immediately - detects IC shapes only
python ic_webcam.py
```

### Option 2: With Text Recognition (OCR)
```powershell
# Step 1: Install Tesseract OCR
# Download: https://github.com/UB-Mannheim/tesseract/wiki
# Install to: C:\Program Files\Tesseract-OCR

# Step 2: Install Python OCR package
pip install pytesseract

# Step 3: Run with OCR
python ic_webcam.py
```

---

## 📋 Features

### ✅ IC Detection Features
- **Shape Filtering**: Only detects rectangular IC-shaped objects
- **Aspect Ratio Check**: Filters objects with IC-like dimensions (1:1 to 3:1 ratio)
- **Minimum Size**: Ignores objects smaller than 40x40 pixels
- **No IC Warning**: Shows "IC is not present" when no IC detected

### ✅ Brand Recognition (with OCR)
Recognizes 25+ IC manufacturers including:
- **Texas Instruments** (TI, LM, TL, TPS, SN, CD)
- **Analog Devices** (AD, ADP, ADM)
- **Maxim** (MAX, DS)
- **Linear Technology** (LT, LTC)
- **Microchip** (PIC, MCP, AT)
- **Atmel** (ATMEGA, ATTINY)
- **STM** (STM32, STM8)
- **NXP** (LPC, i.MX)
- **Infineon** (IR, IRL)
- **And 15+ more...**

### ✅ Visual Feedback
- **Green Box**: IC identified with manufacturer
- **Orange Box**: IC detected but manufacturer unknown
- **Red Warning**: "NO IC DETECTED! IC is not present"
- **Info Panel**: Shows IC count, FPS, confidence

---

## 🎮 Keyboard Controls

- **'q'** - Quit
- **'s'** - Save screenshot
- **'c'** - Toggle confidence display
- **'f'** - Toggle IC-only filter (show all objects vs IC only)

---

## 📷 Usage Examples

### Webcam Detection
```powershell
# Default camera (ID 0)
python ic_webcam.py

# External camera (ID 1)
python ic_webcam.py --camera 1

# Lower confidence for more detections
python ic_webcam.py --conf 0.2

# Higher confidence for fewer false positives
python ic_webcam.py --conf 0.5
```

### Image Detection
```powershell
# Single image
python src/ic_chip_detector.py --source ic_board.jpg --save

# Show all objects (not just ICs)
python src/ic_chip_detector.py --source ic_board.jpg --show-all
```

---

## 🔧 How It Works

### 1. **IC Shape Detection**
```python
# Checks if detected object has IC-like shape
- Width and Height > 40 pixels
- Aspect Ratio between 0.3 and 3.5
- Rectangular shape
```

### 2. **Text Extraction (OCR)**
```python
# Preprocessing for better OCR
- Convert to grayscale
- Upscale 3x for clarity
- Denoise
- Adaptive thresholding
- Morphological cleaning
```

### 3. **Manufacturer Identification**
```python
# Pattern matching against known IC prefixes
if "LM" in text:
    manufacturer = "TEXAS INSTRUMENTS"
    part_number = "LM358" (example)
```

### 4. **Visual Output**
```python
# Color-coded display
Green = IC identified with manufacturer
Orange = IC detected, manufacturer unknown
Red = No IC present (error state)
```

---

## 📊 Detection Modes

### Mode 1: IC-Only (Default)
- Filters detections to only IC-shaped objects
- Shows "IC is not present" if no IC found
- Recommended for IC-specific applications

### Mode 2: All Objects
- Shows all detected objects
- Useful for debugging
- Press 'f' to toggle during runtime

---

## 🎯 Best Results

### For IC Detection
✅ **DO:**
- Place IC on contrasting background
- Use good lighting (bright, even)
- Keep IC centered in frame
- Hold camera steady
- Use higher resolution camera

❌ **DON'T:**
- Use cluttered backgrounds
- Extreme angles (keep perpendicular)
- Poor lighting or shadows
- Very small ICs (<1cm)
- Blurry images

### For Text Recognition (OCR)
✅ **DO:**
- Get close to IC (text should be large)
- Ensure text is sharp and in focus
- Use bright, even lighting
- Keep IC flat (not tilted)
- Clean IC surface

❌ **DON'T:**
- Too far away (text too small)
- Reflective surfaces (glare)
- Dirty or damaged IC
- Motion blur
- Extreme viewing angles

---

## 🔍 Troubleshooting

### Issue: No IC Detected (but IC is present)
**Solutions:**
1. Adjust confidence: `--conf 0.2` (lower)
2. Check lighting (use brighter light)
3. Get closer to IC
4. Ensure IC is rectangular and visible
5. Toggle filter: Press 'f' to see all objects

### Issue: Text Not Recognized
**Solutions:**
1. Install Tesseract OCR (see setup instructions)
2. Get closer to IC (make text larger)
3. Improve lighting
4. Clean IC surface
5. Ensure text is in focus

### Issue: Wrong Manufacturer Detected
**Solutions:**
1. Better lighting for clearer text
2. Get closer for larger text
3. Clean IC surface
4. Hold camera steady (avoid blur)
5. Check if IC prefix is in supported list

### Issue: Too Many False Positives
**Solutions:**
1. Increase confidence: `--conf 0.5`
2. Ensure IC-only filter is ON (press 'f')
3. Use cleaner background
4. Better lighting

---

## 📁 Output Files

### Screenshot
```
ic_screenshot_0.jpg
ic_screenshot_1.jpg
...
```

### Detection Report (when using src/ic_chip_detector.py)
```json
{
    "timestamp": "20251013_224530",
    "total_ics_detected": 3,
    "detections": [
        {
            "id": 1,
            "manufacturer": "TEXAS INSTRUMENTS",
            "part_number": "LM358",
            "confidence": 0.87,
            "raw_text": "LM358N",
            "dimensions": {
                "width": 120,
                "height": 85,
                "aspect_ratio": 1.41
            }
        }
    ]
}
```

---

## 🎓 Supported IC Manufacturers

| Manufacturer | Common Prefixes | Examples |
|--------------|----------------|----------|
| **Texas Instruments** | TI, LM, TL, TPS, SN | LM358, TL074, TPS54620 |
| **Analog Devices** | AD, ADP, ADM | AD620, ADP3303, ADM3202 |
| **Maxim** | MAX, DS | MAX232, DS1307 |
| **Linear Tech** | LT, LTC | LT1086, LTC3780 |
| **Microchip** | PIC, MCP, AT | PIC16F877, MCP23017 |
| **Atmel** | ATMEGA, ATTINY, AT | ATMEGA328P, ATTINY85 |
| **STM** | STM32, STM8, ST | STM32F103, STM8S003 |
| **NXP** | LPC, MK, i.MX | LPC1768, MK20DX256 |
| **Infineon** | IR, IRL, XMC | IRFZ44N, IRL540N |
| **OnSemi** | ON, MC | MC34063, LM2904 |
| **Intel** | 8086, i3, i5, i7 | 8086, Core i7 |
| **AMD** | RYZEN, ATHLON | Ryzen 5 3600 |

...and 13+ more manufacturers!

---

## 🔧 Advanced Configuration

### Custom IC Patterns
Edit `src/ic_chip_detector.py` to add custom manufacturers:

```python
IC_MANUFACTURERS = {
    'YOUR_COMPANY': ['PREFIX1', 'PREFIX2'],
}
```

### OCR Settings
Adjust OCR preprocessing in `preprocess_for_ocr()`:
- Scale factor (default: 3x)
- Denoising strength
- Threshold parameters

### Detection Thresholds
Adjust in code:
```python
# Minimum IC size
if box_width > 30 and box_height > 30:

# Aspect ratio range
if 0.3 < aspect_ratio < 3.0:
```

---

## 📚 Files

### Main Scripts
- **`ic_webcam.py`** ⭐ - Real-time webcam detection (START HERE!)
- **`src/ic_chip_detector.py`** - Image/batch detection with detailed reports

### Configuration
- **`requirements_ocr.txt`** - OCR dependencies
- **`IC_CHIP_DETECTION.md`** - This documentation

---

## 💡 Pro Tips

### 🎯 For Electronics Enthusiasts
1. Keep a white paper background under circuit boards
2. Use a desk lamp for consistent lighting
3. Use macro lens or close-up mode for small ICs
4. Clean ICs with isopropyl alcohol before imaging

### 🔬 For PCB Inspection
1. Process image first, then zoom in on specific ICs
2. Save detection reports for inventory tracking
3. Use batch processing for multiple boards
4. Combine with multimeter readings for testing

### 📷 For Best OCR Results
1. Camera resolution: 1080p minimum
2. Distance: 10-20cm from IC
3. Lighting: 5000K+ color temperature (daylight)
4. Focus: Manual focus on IC text

---

## 🆘 Getting Help

### Quick Checks
```powershell
# Test if YOLO is working
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt'); print('OK')"

# Test if Tesseract is installed
tesseract --version

# Test if pytesseract is working
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

### Resources
- **YOLOv8 Docs**: https://docs.ultralytics.com/
- **Tesseract OCR**: https://github.com/tesseract-ocr/tesseract
- **pytesseract**: https://pypi.org/project/pytesseract/

---

## ✅ Quick Setup Checklist

- [ ] Basic detection working: `python ic_webcam.py`
- [ ] Tesseract installed: Download from GitHub
- [ ] pytesseract installed: `pip install pytesseract`
- [ ] Text recognition working: Look for manufacturer names
- [ ] Tested with real IC chips
- [ ] Saved screenshots: Press 's' key

---

## 🎉 You're Ready!

### Start detecting ICs now:
```powershell
python ic_webcam.py
```

**Point your camera at IC chips and see the magic! 🔬**

---

**Note**: Without Tesseract OCR installed, the system will still detect IC shapes and show "IC CHIP" label, but won't identify specific manufacturers or part numbers. OCR is optional but recommended for full functionality.
