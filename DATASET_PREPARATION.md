# 📸 IC IMAGE DATASET PREPARATION GUIDE

## 🎯 You Have Images - Great! Here's What We'll Do:

### Step 1: Organize Your Images ✅

**Required folder structure:**
```
d:\SIH PS-162\ic-detection-yolo\data\raw\
├── ic_images\
│   ├── img001.jpg
│   ├── img002.jpg
│   ├── img003.jpg
│   └── ... (all your IC images)
```

**Action needed:**
1. Copy ALL your IC images to: `d:\SIH PS-162\ic-detection-yolo\data\raw\ic_images\`
2. Supported formats: .jpg, .jpeg, .png
3. Rename if needed (sequential names help but not required)

---

### Step 2: Label Your Images 🏷️

**We'll use Roboflow (FREE online tool):**

#### Why Roboflow?
- ✅ Free for small datasets
- ✅ Easy drag-and-drop interface
- ✅ Exports in YOLO format (ready to use)
- ✅ Auto-splits train/val/test
- ✅ No installation needed

#### Labeling Process:

**A. Create Roboflow Account**
1. Go to: https://roboflow.com/
2. Sign up (FREE account)
3. Create new project: "IC Chip Detection"
4. Project type: Object Detection
5. Annotation group: "ic_chip"

**B. Upload Images**
1. Click "Upload"
2. Select all your IC images
3. Wait for upload (shows progress)

**C. Annotate Images**
1. Click on first image
2. Press 'B' key (box tool)
3. Draw box around IC chip
4. Label: "ic_chip"
5. Press 'D' key (done)
6. Repeat for all images

**Time estimate:** 
- ~10-20 seconds per image
- 300 images = ~1-2 hours total

**D. Generate Dataset**
1. Click "Generate" → "Version"
2. Preprocessing: Resize to 640x640
3. Augmentation: (we'll do this in training)
4. Generate!

**E. Export**
1. Format: YOLOv8
2. Download ZIP file
3. Extract to: `d:\SIH PS-162\ic-detection-yolo\data\`

---

### Step 3: Verify Dataset Structure ✅

After extraction, you should have:
```
d:\SIH PS-162\ic-detection-yolo\data\
├── train\
│   ├── images\
│   │   ├── image1.jpg
│   │   └── ...
│   └── labels\
│       ├── image1.txt
│       └── ...
├── valid\
│   ├── images\
│   └── labels\
└── data.yaml
```

**data.yaml should contain:**
```yaml
train: ../train/images
val: ../valid/images

nc: 1
names: ['ic_chip']
```

---

### Step 4: Train the Model 🚀

Run the training script (I'll create this next)

**Time estimate:**
- CPU: 2-6 hours
- GPU: 20-60 minutes

**What happens:**
- Model learns what IC chips look like
- Creates checkpoints every few epochs
- Saves best model automatically
- Generates accuracy graphs

---

### Step 5: Use Your Custom Model ✅

After training, use your model:
```powershell
python strict_ic_detector.py --mode webcam --model runs/detect/train/weights/best.pt
```

**Result:** 95%+ accuracy on YOUR specific IC types!

---

## 🎓 Alternative: Use LabelImg (Offline Tool)

If you prefer offline labeling:

**Install LabelImg:**
```powershell
pip install labelImg
labelImg
```

**Usage:**
1. Open Dir: Select your IC images folder
2. Change Save Dir: Select labels folder
3. Press 'W' - Draw box around IC
4. Label: "ic_chip"
5. Press 'D' - Next image
6. Repeat

**Export format:** YOLO (.txt files)

---

## 📊 Dataset Quality Tips

### Good Dataset Characteristics:

✅ **Variety in lighting**
- Bright light, dim light, natural light
- Different times of day

✅ **Different angles**
- Top view, slight angles
- Different distances

✅ **Various IC types**
- DIP, SMD, SOIC, QFP
- Different sizes

✅ **Different backgrounds**
- Breadboards, PCBs, plain surfaces
- Various colors

✅ **Clear vs Blurry**
- Mostly clear (90%)
- Some slightly blurry (10%) - trains for real-world

### Avoid:

❌ All images same lighting
❌ All same IC type
❌ All same angle
❌ Too blurry images
❌ Images without ICs

---

## 🔢 How Many Images Do You Need?

| Count | Result | Use Case |
|-------|--------|----------|
| 100-200 | ~75-80% | Quick testing, proof of concept |
| 300-500 | ~85-90% | Good for general use |
| 500-1000 | ~90-95% | Professional level |
| 1000+ | ~95-98% | Production ready |

**Recommendation:** Start with what you have, train, test, add more if needed!

---

## 📝 Quick Checklist

Before training, verify:

- [ ] All images copied to `data/raw/ic_images/`
- [ ] Images are clear and contain ICs
- [ ] Ready to label (Roboflow account or LabelImg installed)
- [ ] Have 2-6 hours for training (can run overnight)
- [ ] Conda environment has ultralytics installed

---

## 🚀 Next Steps

**Tell me:**
1. Where are your images now? (folder path)
2. How many images? (approximate)
3. Are they labeled? (boxes drawn around ICs?)

**Then I'll:**
1. Help you organize them
2. Guide you through labeling (if needed)
3. Create the training script
4. Run training
5. Test your custom model!

---

## 💡 Pro Tips

**Labeling Tips:**
- Label consistently (always same class name)
- Include partial ICs (if IC is cut off, still label visible part)
- Tight boxes (don't include too much background)
- Label all ICs in each image (don't skip any)

**Training Tips:**
- Train overnight (takes time but worth it)
- Save checkpoints (don't lose progress)
- Monitor training (watch accuracy improve)
- Test on new images (not in training set)

---

**Ready to proceed! Please tell me:**
- Image folder location
- Number of images
- Labeled or not

Then we'll start! 🚀
