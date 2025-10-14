# 🚀 Quick Start Guide - IC Detection System

## Installation (Step-by-Step)

### 1. Clone/Download the Project
```bash
cd d:\SIH PS-162\ic-detection-yolo
```

### 2. Create Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**Note**: If you have NVIDIA GPU:
```powershell
# Install PyTorch with CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 4. Download YOLOv8 Model (Auto-downloads on first run)
```powershell
# The model will auto-download when you run detection
# Or manually download:
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"
```

## 🎯 Quick Test (Without Training)

### Test 1: Single Image Detection
```powershell
# Download a sample IC image or use your own
# Place it in the project folder as test.jpg

python src/detect.py --source test.jpg --weights yolov8s.pt --conf 0.3
```

### Test 2: Webcam Detection
```powershell
python src/webcam.py --weights yolov8s.pt --conf 0.4
```

### Test 3: Batch Processing
```powershell
# Create a test folder with multiple IC images
mkdir data\test
# Add images to data\test\

python src/detect.py --source data\test --weights yolov8s.pt
```

## 📊 Training Your Own Model

### Step 1: Prepare Dataset

#### Option A: Use Roboflow (Recommended)
1. Go to [Roboflow](https://roboflow.com)
2. Create a project
3. Upload IC images (100+ minimum, 1000+ recommended)
4. Annotate images (draw boxes around ICs)
5. Export in **YOLOv8 format**
6. Download and extract to `data/` folder

#### Option B: Manual Annotation
1. Install LabelImg:
   ```powershell
   pip install labelImg
   labelImg
   ```
2. Annotate images
3. Save in YOLO format
4. Organize:
   ```
   data/
   ├── train/
   │   ├── images/
   │   └── labels/
   ├── val/
   │   ├── images/
   │   └── labels/
   └── test/
       ├── images/
       └── labels/
   ```

### Step 2: Update Training Config
Edit `train_config.yaml`:
```yaml
path: ./data
train: train/images
val: val/images

names:
  0: IC
  1: Aadhaar
  2: PAN
  # Add your IC types

nc: 3  # Number of classes
```

### Step 3: Train Model
```powershell
# Quick training (50 epochs)
python src/train.py --epochs 50 --batch 16

# Full training (100 epochs)
python src/train.py --epochs 100 --batch 16 --imgsz 640

# With validation
python src/train.py --epochs 100 --validate
```

### Step 4: Use Trained Model
```powershell
# After training, best model is saved to models/best.pt
python src/detect.py --source test.jpg --weights models/best.pt
```

## 🎨 Usage Examples

### Example 1: High Confidence Detection
```powershell
python src/detect.py --source image.jpg --conf 0.7 --weights models/best.pt
```

### Example 2: Video Processing
```powershell
python src/detect.py --source video.mp4 --weights models/best.pt --save
```

### Example 3: Webcam with Custom Settings
```powershell
python src/webcam.py --conf 0.5 --resolution 1920 1080 --fps 30
```

### Example 4: Batch Processing Directory
```powershell
python src/detect.py --source ./data/test/ --weights models/best.pt --output results/
```

## 📝 Configuration

### Adjust Detection Settings
Edit `config/config.yaml`:

```yaml
detection:
  confidence_threshold: 0.5  # Lower = more detections
  iou_threshold: 0.45
  max_detections: 10

preprocessing:
  denoise: true  # Enable denoising
  sharpen: true  # Enable sharpening
  
quality_metrics:
  enabled: true  # Calculate quality metrics
```

### Model Selection
- **yolov8n.pt** - Fastest, smallest (6MB), FPS: 45
- **yolov8s.pt** - Balanced (22MB), FPS: 35 ⭐ **Recommended**
- **yolov8m.pt** - More accurate (52MB), FPS: 25
- **yolov8l.pt** - Very accurate (87MB), FPS: 18
- **yolov8x.pt** - Best accuracy (131MB), FPS: 12

## 🔧 Troubleshooting

### Issue 1: "CUDA not available"
**Solution**: Install CUDA-enabled PyTorch
```powershell
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Issue 2: Low accuracy
**Solutions**:
- Collect more training images (1000+)
- Use data augmentation
- Train for more epochs (100-300)
- Try larger model (yolov8m or yolov8l)
- Increase image size: `--imgsz 1280`

### Issue 3: Slow detection
**Solutions**:
- Use smaller model (yolov8n)
- Enable GPU: `--device 0`
- Reduce image size: `--imgsz 416`
- Use half-precision: Add `half=True` in code

### Issue 4: Too many false positives
**Solutions**:
- Increase confidence threshold: `--conf 0.7`
- Add more negative samples to training
- Train longer
- Use NMS threshold: `--iou 0.3`

## 📈 Performance Tips

### 1. GPU Acceleration
```powershell
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Use GPU
python src/detect.py --source test.jpg --device 0
```

### 2. Optimize for Speed
```yaml
# config.yaml
detection:
  device: "cuda"
  half_precision: true  # FP16 (2x faster)
  input_size: 416  # Smaller input (faster)
```

### 3. Optimize for Accuracy
```yaml
detection:
  input_size: 1280  # Larger input
  confidence_threshold: 0.3  # Lower threshold
  max_detections: 50  # More detections
```

## 🎯 Next Steps

1. **Collect Dataset**: 
   - Minimum: 100 images per IC type
   - Recommended: 1000+ images
   - Include variations: lighting, angles, backgrounds

2. **Train Model**:
   - Start with 50 epochs
   - Monitor validation loss
   - If overfitting, add augmentation
   - If underfitting, train longer

3. **Test & Iterate**:
   - Test on new images
   - Identify failure cases
   - Add more training data for failures
   - Retrain

4. **Deploy**:
   - Export to ONNX for production
   - Create API service (FastAPI)
   - Integrate with your application

## 📚 Resources

- **YOLOv8 Docs**: https://docs.ultralytics.com/
- **Roboflow Tutorial**: https://roboflow.com/train
- **Dataset Best Practices**: https://blog.roboflow.com/
- **OpenCV Docs**: https://docs.opencv.org/

## 💡 Tips for Best Results

1. **Quality over Quantity**: 100 well-annotated images > 1000 poor ones
2. **Diverse Data**: Include various lighting, angles, backgrounds
3. **Augmentation**: Use built-in augmentation (YOLOv8 does this automatically)
4. **Validation**: Always validate on separate test set
5. **Iterative**: Train → Test → Collect more data → Retrain

## 🆘 Support

If you encounter issues:
1. Check error message carefully
2. Verify dataset structure
3. Check config files
4. Try default settings first
5. Read YOLOv8 documentation

---

**Ready to start? Run:**
```powershell
python src/webcam.py --weights yolov8s.pt
```

Press 'q' to quit, 's' to save screenshot!
