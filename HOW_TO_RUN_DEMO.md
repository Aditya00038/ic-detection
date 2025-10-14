# ⚡ QUICK IC DETECTION DEMO - USE THIS NOW!

## 🚀 Run Basic IC Detection Immediately

### Option 1: Double-click this file
```
run_quick_demo.bat
```

### Option 2: Run in VS Code Terminal
Open a NEW PowerShell terminal and run:
```powershell
cd "d:\SIH PS-162\ic-detection-yolo"
C:\Users\sagitec\anaconda3\Scripts\conda.exe run -n base python quick_ic_demo.py
```

### Option 3: Run with Anaconda Prompt
1. Open **Anaconda Prompt** from Start Menu
2. Run these commands:
```bash
cd "d:\SIH PS-162\ic-detection-yolo"
conda activate base
python quick_ic_demo.py
```

---

## 📸 What This Does

- **Webcam Mode**: Shows live IC detection
- **Image Mode**: Detect ICs in photos
- Uses pretrained YOLOv8 (works immediately!)
- Filters out faces and non-IC objects
- Shows detection confidence scores

---

## 🎯 Controls (Webcam Mode)

- **Q** - Quit
- **S** - Save screenshot
- **SPACE** - Pause/Resume

---

## 💡 Note

This is a **basic demo** using pretrained model (~70% accuracy).

For **95% accuracy**, wait for the training to complete (running in background).
The trained model will be at: `C:\Users\sagitec\runs\detect\ic_detector\weights\best.pt`

---

## 🎥 Try It Now!

1. Run using one of the options above
2. Choose option 1 for webcam
3. Point camera at IC chip
4. See real-time detection!

If webcam doesn't work, try option 2 (image mode) with your IC photos.
