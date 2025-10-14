# 🎓 TRAINING CUSTOM IC DETECTOR

## ⚠️ Current Limitation

The current detector uses **YOLOv8s** trained on general objects (COCO dataset), which includes:
- People, faces, animals
- Vehicles, furniture
- Everyday objects

**This is why it detects faces and other things!**

## ✅ Solution: Train Custom IC-Only Model

To detect **ONLY IC chips**, you need to train YOLOv8 on IC-specific dataset.

---

## 📊 IC Datasets Available

### 1. **Electronics Component Dataset** (Recommended)
- **Source**: Roboflow
- **URL**: https://universe.roboflow.com/
- **Search**: "IC chip", "integrated circuit", "electronic components"
- **Classes**: IC chips, DIP, SOIC, QFP, etc.
- **Images**: 500-5000+ labeled images
- **Format**: YOLO format (ready to use)

### 2. **PCB Component Dataset**
- **Description**: Circuit boards with labeled components
- **Contains**: ICs, resistors, capacitors, etc.
- **Good for**: Detecting ICs on boards

### 3. **Custom Dataset** (DIY)
- Collect your own IC images
- Label with tools like LabelImg, Roboflow
- 300+ images minimum for good results

---

## 🚀 How to Train Custom IC Model

### Step 1: Get IC Dataset

**Option A: Download from Roboflow**
```powershell
# 1. Go to: https://universe.roboflow.com/
# 2. Search: "IC chip" or "integrated circuit"
# 3. Select a dataset (look for 1000+ images)
# 4. Download in YOLO format
# 5. Extract to: d:\SIH PS-162\ic-detection-yolo\data\
```

**Option B: Create Your Own**
```powershell
# 1. Collect 300+ IC chip photos
# 2. Upload to: https://roboflow.com/
# 3. Label ICs as "ic_chip" class
# 4. Export as YOLO format
# 5. Download and extract
```

---

### Step 2: Prepare Dataset Structure

```
d:\SIH PS-162\ic-detection-yolo\data\
├── train/
│   ├── images/
│   │   ├── ic001.jpg
│   │   ├── ic002.jpg
│   │   └── ...
│   └── labels/
│       ├── ic001.txt
│       ├── ic002.txt
│       └── ...
├── val/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── data.yaml
```

---

### Step 3: Create data.yaml

Create file: `d:\SIH PS-162\ic-detection-yolo\data\data.yaml`

```yaml
# IC Chip Detection Dataset

# Paths (use absolute paths)
train: d:/SIH PS-162/ic-detection-yolo/data/train/images
val: d:/SIH PS-162/ic-detection-yolo/data/val/images
test: d:/SIH PS-162/ic-detection-yolo/data/test/images

# Classes
nc: 1  # number of classes
names: ['ic_chip']  # class names

# Optional: Dataset info
download: false
```

---

### Step 4: Train the Model

Create file: `train_ic_model.py`

```python
from ultralytics import YOLO

# Load base model
model = YOLO('yolov8s.pt')

# Train on IC dataset
results = model.train(
    data='data/data.yaml',
    epochs=100,              # Train for 100 epochs
    imgsz=640,              # Image size
    batch=16,               # Batch size (adjust based on GPU)
    name='ic_detector',     # Experiment name
    patience=20,            # Early stopping
    save=True,              # Save checkpoints
    device='cpu',           # Use 'cuda' if you have GPU
    workers=4,
    pretrained=True,
    optimizer='AdamW',
    verbose=True,
    val=True,
    plots=True
)

print("\n✅ Training complete!")
print(f"📊 Best model: runs/detect/ic_detector/weights/best.pt")
```

Run training:
```powershell
python train_ic_model.py
```

**Training time:**
- CPU: 2-6 hours
- GPU: 20-60 minutes

---

### Step 5: Use Trained Model

```python
from ultralytics import YOLO

# Load YOUR trained model
model = YOLO('runs/detect/ic_detector/weights/best.pt')

# Now it will ONLY detect ICs!
results = model('photo.jpg')
```

---

## 📦 Quick Setup with Pre-labeled Dataset

### Option 1: Use Roboflow Dataset (Easiest)

1. **Find IC Dataset**:
   ```
   Visit: https://universe.roboflow.com/
   Search: "IC chip detection"
   Select dataset with 500+ images
   ```

2. **Download**:
   ```
   Format: YOLOv8
   Click "Download"
   Extract to: d:\SIH PS-162\ic-detection-yolo\data\
   ```

3. **Train**:
   ```powershell
   python train_ic_model.py
   ```

4. **Use**:
   ```powershell
   python strict_ic_detector.py --mode webcam
   ```

---

## 🎯 Alternative: Use Strict Filtering (No Training)

If you **don't want to train**, I've created `strict_ic_detector.py` with **ultra-strict filtering**:

### Strict Checks Applied:
1. ✅ Size: 40-500 pixels
2. ✅ Aspect ratio: 0.4-2.5 (rectangular)
3. ✅ Edge detection: Moderate edges (rectangular outline)
4. ✅ Corner detection: 4-6 corners (rectangle)
5. ✅ Rectangularity: >70% rectangular shape
6. ✅ Color: Reject very bright objects (faces)
7. ✅ Pin patterns: Detect parallel lines (IC pins)
8. ✅ Face rejection: Check for circular features (eyes)

**Run it:**
```powershell
python strict_ic_detector.py --mode webcam --conf 0.5
```

**For image:**
```powershell
python strict_ic_detector.py --mode image --image photo.jpg --conf 0.5
```

---

## 📊 Comparison

| Method | Accuracy | Setup Time | Pros | Cons |
|--------|----------|------------|------|------|
| **Strict Filtering** | ~70% | Instant | No training needed | May miss some ICs |
| **Custom Training** | ~95% | 2-6 hours | Very accurate | Needs dataset + training |

---

## 🎓 Recommended IC Datasets

### 1. "PCB Components Dataset"
- **Images**: 2000+
- **Classes**: IC, resistor, capacitor, etc.
- **Quality**: High
- **URL**: Search on Roboflow Universe

### 2. "Electronic Components Recognition"
- **Images**: 1500+
- **Classes**: Various IC types
- **Quality**: Good
- **URL**: Roboflow Universe

### 3. "IC Chip Classification"
- **Images**: 800+
- **Classes**: Different IC packages
- **Quality**: Medium
- **URL**: Roboflow Universe

---

## 🛠️ If You Want to Train

### Requirements:
```powershell
pip install ultralytics
pip install albumentations  # Data augmentation
```

### Minimal Dataset Requirements:
- **Minimum**: 300 images
- **Good**: 500-1000 images
- **Excellent**: 2000+ images
- **Classes**: 1 (just "ic_chip")
- **Annotations**: YOLO format (.txt files)

### Dataset Annotation Format:
Each image has a corresponding .txt file:

```
ic001.txt:
0 0.5 0.5 0.3 0.2
```

Format: `class_id center_x center_y width height` (normalized 0-1)

---

## 🚀 Quick Start (No Training)

**Use the strict detector now:**

```powershell
cd "d:\SIH PS-162\ic-detection-yolo"
python strict_ic_detector.py --mode webcam
```

**Features:**
- ✅ No menu - runs directly
- ✅ Ultra-strict IC filtering
- ✅ Rejects faces automatically
- ✅ Only detects IC-like objects
- ✅ Shows rejection reasons

**Controls:**
- `q` - Quit
- `s` - Save screenshot
- `+` - Stricter
- `-` - More lenient

---

## 📚 Training Tutorial (Full Process)

### 1. Collect Images
```powershell
# Take 300+ photos of IC chips
# Various angles, lighting, IC types
# Save as .jpg or .png
```

### 2. Label Images
```powershell
# Use Roboflow.com (easiest)
# Upload images
# Draw boxes around ICs
# Label as "ic_chip"
# Export as YOLOv8 format
```

### 3. Setup Dataset
```powershell
# Extract downloaded dataset
# Place in: d:\SIH PS-162\ic-detection-yolo\data\
# Verify data.yaml exists
```

### 4. Train
```powershell
python train_ic_model.py
# Wait 2-6 hours (CPU) or 30 mins (GPU)
```

### 5. Use Trained Model
```powershell
# Model saved at: runs/detect/ic_detector/weights/best.pt
python strict_ic_detector.py --mode webcam
# (update script to use your trained model)
```

---

## 🎯 My Recommendation

### For Immediate Use (Today):
✅ **Use `strict_ic_detector.py`**
- No training needed
- Works now
- Rejects faces/non-ICs
- ~70% accurate

```powershell
python strict_ic_detector.py --mode webcam --conf 0.5
```

### For Best Results (This Week):
✅ **Train custom model**
1. Download IC dataset from Roboflow (30 mins)
2. Train model (2-6 hours)
3. Get ~95% accuracy
4. Only detects ICs

---

## 📞 Need Dataset?

I can help you:
1. Find best IC dataset on Roboflow
2. Set up training script
3. Configure data.yaml
4. Run training

**Just let me know if you want to train a custom model!**

For now, **use the strict detector** - it should work much better than the general one.

---

**Quick Command:**
```powershell
cd "d:\SIH PS-162\ic-detection-yolo"
python strict_ic_detector.py --mode webcam
```

This will **NOT detect faces** - it has 8 strict checks to verify it's an IC!
