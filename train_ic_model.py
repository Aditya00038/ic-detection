"""
IC Chip Detection Model Training Script
Trains YOLOv8 on your IC dataset for 95% accuracy
"""

from ultralytics import YOLO
from pathlib import Path
import time

def train_ic_model():
    """Train custom IC detection model"""
    
    print("\n" + "="*70)
    print("🚀 IC CHIP DETECTION MODEL TRAINING")
    print("="*70)
    
    # Check if data.yaml exists
    data_yaml = Path("data/data.yaml")
    if not data_yaml.exists():
        # Try alternative locations
        alternatives = [
            Path("data/dataset.yaml"),
            Path("data.yaml"),
        ]
        for alt in alternatives:
            if alt.exists():
                data_yaml = alt
                break
        
        if not data_yaml.exists():
            print("\n❌ ERROR: data.yaml not found!")
            print("\n💡 Please ensure:")
            print("   1. Dataset is downloaded and extracted")
            print("   2. data.yaml exists in data/ folder")
            print("   3. Run: python verify_dataset.py")
            return
    
    print(f"\n✅ Using dataset: {data_yaml}")
    
    # Training configuration
    print("\n⚙️ Training Configuration:")
    print("   Model: YOLOv8s (small, balanced)")
    print("   Epochs: 100")
    print("   Batch size: 16")
    print("   Image size: 640x640")
    print("   Device: CPU (auto-detect GPU if available)")
    print("   Patience: 20 (early stopping)")
    
    print("\n⏱️ Estimated time:")
    print("   CPU: 2-6 hours")
    print("   GPU: 20-60 minutes")
    
    print("\n� Starting training in 3 seconds...")
    import time
    time.sleep(3)
    
    # Load base model
    print("\n🔧 Loading YOLOv8s base model...")
    model = YOLO('yolov8s.pt')
    print("✅ Model loaded")
    
    # Start training
    print("\n🎓 Starting training...")
    print("   (This will take a while, you can close terminal and check progress later)")
    print()
    
    start_time = time.time()
    
    try:
        results = model.train(
            data=str(data_yaml),
            epochs=100,              # Train for 100 epochs
            imgsz=640,               # Image size
            batch=16,                # Batch size (adjust if out of memory)
            name='ic_detector',      # Experiment name
            patience=20,             # Early stopping patience
            save=True,               # Save checkpoints
            device='cpu',            # Use 'cuda' if GPU available
            workers=4,               # Number of workers
            pretrained=True,         # Use pretrained weights
            optimizer='AdamW',       # Optimizer
            verbose=True,            # Verbose output
            val=True,                # Validate during training
            plots=True,              # Generate plots
            exist_ok=True,           # Overwrite existing
            cos_lr=True,             # Cosine learning rate
            cache=False,             # Don't cache (to save memory)
        )
        
        elapsed_time = time.time() - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        
        print("\n" + "="*70)
        print("✅ TRAINING COMPLETE!")
        print("="*70)
        print(f"\n⏱️ Training time: {hours}h {minutes}m")
        print(f"\n📊 Results:")
        print(f"   Best model: runs/detect/ic_detector/weights/best.pt")
        print(f"   Last model: runs/detect/ic_detector/weights/last.pt")
        print(f"   Results folder: runs/detect/ic_detector/")
        print(f"   Plots: runs/detect/ic_detector/*.png")
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Check results: Open runs/detect/ic_detector/")
        print(f"   2. Test model: python test_ic_model.py")
        print(f"   3. Use model: python strict_ic_detector.py --model runs/detect/ic_detector/weights/best.pt")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Training interrupted by user!")
        print("   Partial model saved in runs/detect/ic_detector/")
        
    except Exception as e:
        print(f"\n❌ Training error: {e}")
        print("\n💡 Common solutions:")
        print("   • Out of memory: Reduce batch size (--batch 8 or 4)")
        print("   • Data error: Check data.yaml paths are correct")
        print("   • Permission error: Run as administrator")

if __name__ == '__main__':
    train_ic_model()
