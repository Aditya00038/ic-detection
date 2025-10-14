# 🎯 Best IC Detection Project using YOLOv8 + OpenCV

## ✅ What You Have Now

A **complete, production-ready IC detection system** using:
- ✅ **YOLOv8** - Latest YOLO architecture (state-of-the-art)
- ✅ **OpenCV** - Advanced image processing
- ✅ **Real-time Detection** - Webcam support
- ✅ **Batch Processing** - Process multiple images
- ✅ **Quality Metrics** - Blur, brightness, contrast analysis
- ✅ **Training Pipeline** - Complete training workflow
- ✅ **Easy Setup** - Automated setup script

## 🚀 Installation (5 Minutes)

```powershell
# 1. Navigate to project
cd "d:\SIH PS-162\ic-detection-yolo"

# 2. Run setup script
.\setup.ps1

# That's it! Setup script will:
# - Create virtual environment
# - Install all dependencies
# - Download YOLOv8 model
# - Create necessary directories
```

## 🎮 Quick Demo (No Training Needed!)

### Demo 1: Webcam (Easiest!)
```powershell
python demo.py --mode webcam
```
Press 'q' to quit, 's' to save screenshot

### Demo 2: Single Image
```powershell
# Use your own IC image
python demo.py --mode image --source path\to\your\ic.jpg
```

### Demo 3: Advanced Detection
```powershell
python src/detect.py --source test.jpg --weights yolov8s.pt --conf 0.5
```

## 📊 Train Your Custom IC Model

### Step 1: Prepare Dataset

**Option A: Use Roboflow (Recommended)**
1. Go to https://roboflow.com
2. Create account and project
3. Upload IC images (minimum 100, recommended 500+)
4. Annotate (draw boxes around ICs)
5. Export as "YOLOv8"
6. Extract to `data/` folder

**Option B: Manual Annotation**
```powershell
# Install annotation tool
pip install labelImg

# Run annotation tool
labelImg

# Annotate your images
# Save in YOLO format
```

**Dataset Structure:**
```
data/
├── train/
│   ├── images/    <- Your training images
│   └── labels/    <- YOLO format labels (.txt)
├── val/
│   ├── images/    <- Validation images
│   └── labels/    <- Validation labels
└── test/
    ├── images/    <- Test images
    └── labels/    <- Test labels
```

### Step 2: Configure Training

Edit `train_config.yaml`:
```yaml
names:
  0: Aadhaar
  1: PAN
  2: Passport
  3: DrivingLicense
  
nc: 4  # Number of IC types
```

### Step 3: Train!

```powershell
# Quick training (1-2 hours on GPU)
python src/train.py --epochs 50 --batch 16

# Full training (better accuracy)
python src/train.py --epochs 100 --batch 16

# Advanced training
python src/train.py --model yolov8m.pt --epochs 100 --batch 8 --imgsz 640
```

### Step 4: Use Your Model

```powershell
# After training, use your model
python src/detect.py --source test.jpg --weights models/best.pt
```

## 📁 Project Structure

```
ic-detection-yolo/
├── config/
│   └── config.yaml           # Detection settings
├── data/                     # Your dataset goes here
│   ├── train/images/
│   ├── train/labels/
│   ├── val/images/
│   └── val/labels/
├── models/
│   └── best.pt              # Your trained model (after training)
├── src/
│   ├── train.py             # 🎓 Training script
│   ├── detect.py            # 🔍 Detection script
│   ├── webcam.py            # 📹 Real-time webcam
│   └── utils/               # Utility functions
├── results/                 # Output files
│   ├── images/              # Detected images
│   ├── crops/               # Cropped ICs
│   └── reports/             # JSON reports
├── demo.py                  # 🎮 Quick demo
├── setup.ps1                # 🔧 Setup script
├── QUICKSTART.md            # 📚 Detailed guide
└── README.md                # This file
```

## 🎯 Usage Examples

### 1. Real-time Webcam Detection
```powershell
python src/webcam.py --conf 0.5 --show-fps
```

### 2. Single Image Detection
```powershell
python src/detect.py --source image.jpg --weights models/best.pt --conf 0.5
```

### 3. Video Processing
```powershell
python src/detect.py --source video.mp4 --weights models/best.pt --save
```

### 4. Batch Processing (Multiple Images)
```powershell
python src/detect.py --source ./data/test/ --weights models/best.pt
```

### 5. High Confidence Only
```powershell
python src/detect.py --source image.jpg --conf 0.8
```

## 🎨 Features

### ✨ Detection Features
- **Multiple IC Types**: Aadhaar, PAN, Passport, etc.
- **High Accuracy**: YOLOv8 architecture
- **Fast**: 30+ FPS on GPU
- **Confidence Scores**: Know how sure the model is
- **Bounding Boxes**: Precise IC location

### 📊 Quality Analysis
- **Blur Detection**: Is the IC image sharp?
- **Brightness**: Too dark or too bright?
- **Contrast**: Image clarity
- **Sharpness**: Edge quality
- **Overall Score**: Quality rating 0-100

### 🎥 Real-time Features
- **Webcam Support**: Live detection
- **FPS Counter**: Performance monitoring
- **Screenshot**: Save detections (press 's')
- **Adjustable Settings**: Change confidence on the fly

### 💾 Output Options
- **Annotated Images**: Images with boxes
- **Cropped ICs**: Individual IC images
- **JSON Reports**: Detailed detection data
- **Quality Metrics**: Image quality analysis

## 🔧 Configuration

Edit `config/config.yaml`:

```yaml
detection:
  confidence_threshold: 0.5    # Lower = more detections
  iou_threshold: 0.45          # Overlap threshold
  max_detections: 10           # Max ICs per image

preprocessing:
  denoise: false               # Remove noise
  sharpen: false               # Sharpen image
  contrast_enhance: false      # Boost contrast

quality_metrics:
  enabled: true                # Calculate quality
  min_blur_score: 100         # Minimum sharpness
  min_brightness: 30          # Minimum brightness
```

## 📈 Model Performance

| Model | Size | Speed (FPS) | Accuracy | Use Case |
|-------|------|-------------|----------|----------|
| YOLOv8n | 6MB | 45 | Good | Mobile, Edge devices |
| YOLOv8s | 22MB | 35 | Better | **Recommended** |
| YOLOv8m | 52MB | 25 | Great | High accuracy needed |
| YOLOv8l | 87MB | 18 | Excellent | Production systems |
| YOLOv8x | 131MB | 12 | Best | Maximum accuracy |

## 💡 Tips for Best Results

### Data Collection
✅ **DO:**
- Collect 500+ images per IC type
- Include various angles (0-30°)
- Different lighting conditions
- Various backgrounds
- Different quality levels

❌ **DON'T:**
- Use only perfect images
- Same background for all
- Only one angle
- Ignore edge cases

### Training Tips
✅ **Best Practices:**
- Start with YOLOv8s (balanced)
- Train 50-100 epochs
- Use 70-20-10 split (train-val-test)
- Enable augmentation (automatic)
- Monitor validation loss
- Save checkpoints regularly

❌ **Avoid:**
- Training on too few images
- Using same data for train and val
- Stopping too early
- Ignoring validation results

### Detection Tips
✅ **For Better Detection:**
- Good lighting
- Sharp images (not blurry)
- IC fills 20-80% of frame
- Minimal background clutter
- Confidence threshold 0.5-0.7

❌ **Will Cause Issues:**
- Very blurry images
- Extreme angles (>45°)
- Very poor lighting
- IC too small in image

## 🐛 Troubleshooting

### Problem: "CUDA not available"
**Solution:**
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Problem: Low detection accuracy
**Solutions:**
1. Collect more training data (1000+ images)
2. Train longer (100-200 epochs)
3. Use larger model (yolov8m)
4. Check dataset quality
5. Balance dataset (equal images per class)

### Problem: Too many false positives
**Solutions:**
1. Increase confidence: `--conf 0.7`
2. Add negative samples to training
3. Train longer
4. Clean dataset (remove bad annotations)

### Problem: Slow performance
**Solutions:**
1. Use smaller model: `yolov8n.pt`
2. Enable GPU: `--device 0`
3. Reduce image size: `--imgsz 416`
4. Process every Nth frame in video

### Problem: Can't find ICs in image
**Solutions:**
1. Lower confidence: `--conf 0.3`
2. Check image quality
3. Ensure IC is visible and clear
4. Try different lighting
5. Check if model is trained for that IC type

## 📚 Next Steps

### 1. **Test Current Setup**
```powershell
python demo.py --mode webcam
```

### 2. **Collect Dataset**
- Use Roboflow or LabelImg
- Minimum 100 images per IC type
- Aim for 500-1000 total images

### 3. **Train Model**
```powershell
python src/train.py --epochs 100
```

### 4. **Test & Iterate**
```powershell
python src/detect.py --source test.jpg --weights models/best.pt
```

### 5. **Deploy**
- Export to ONNX for production
- Create FastAPI service
- Integrate with your app

## 🆘 Need Help?

1. **Read QUICKSTART.md** - Detailed guide
2. **Check config files** - Ensure correct settings
3. **Verify dataset structure** - Correct format
4. **Check error messages** - Usually helpful
5. **YOLOv8 Docs** - https://docs.ultralytics.com/

## 📞 Support Resources

- **YOLOv8 Documentation**: https://docs.ultralytics.com/
- **Roboflow Tutorials**: https://roboflow.com/tutorials
- **OpenCV Docs**: https://docs.opencv.org/
- **Computer Vision Basics**: https://pyimagesearch.com/

## 🎓 Learning Resources

### Beginner
- YOLOv8 Tutorial: https://docs.ultralytics.com/quickstart/
- Dataset Annotation: https://roboflow.com/annotate

### Intermediate
- Object Detection Guide: https://blog.roboflow.com/
- OpenCV Tutorial: https://docs.opencv.org/master/d9/df8/tutorial_root.html

### Advanced
- Model Optimization: https://docs.ultralytics.com/modes/export/
- Custom Augmentation: https://albumentations.ai/

## 📝 License

MIT License - Free for personal and commercial use

## 🎉 You're Ready!

Run this command to start:
```powershell
python demo.py --mode webcam
```

**Happy detecting! 🚀**
