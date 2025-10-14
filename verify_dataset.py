"""
Dataset Verifier
Checks if downloaded dataset is ready for training
"""

import os
from pathlib import Path
import yaml

def verify_dataset(data_path="data"):
    """Verify dataset structure and content"""
    
    print("\n" + "="*60)
    print("📋 DATASET VERIFICATION")
    print("="*60)
    
    data_path = Path(data_path)
    
    # Check for data.yaml
    yaml_files = list(data_path.glob("*.yaml")) + list(data_path.glob("*.yml"))
    
    if not yaml_files:
        print("\n❌ No data.yaml found!")
        print("💡 Expected location: data/data.yaml")
        return False
    
    yaml_file = yaml_files[0]
    print(f"\n✅ Found config: {yaml_file.name}")
    
    # Read yaml
    try:
        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"\n📄 Dataset Configuration:")
        print(f"   Classes: {config.get('nc', 'unknown')}")
        print(f"   Names: {config.get('names', 'unknown')}")
        
        # Check paths
        train_path = config.get('train', '')
        val_path = config.get('val', '') or config.get('valid', '')
        
        print(f"   Train path: {train_path}")
        print(f"   Val path: {val_path}")
        
    except Exception as e:
        print(f"\n❌ Error reading yaml: {e}")
        return False
    
    # Check train folder
    print(f"\n📁 Checking training data...")
    
    # Find train images folder
    train_folders = [
        data_path / "train" / "images",
        data_path / "train",
        data_path / train_path if train_path else None,
    ]
    
    train_images = None
    for folder in train_folders:
        if folder and folder.exists():
            train_images = list(folder.glob("*.jpg")) + list(folder.glob("*.png"))
            if train_images:
                print(f"   ✅ Train images: {len(train_images)} found")
                print(f"      Location: {folder}")
                break
    
    if not train_images:
        print(f"   ❌ No training images found!")
        return False
    
    # Check labels
    label_folder = folder.parent / "labels"
    if not label_folder.exists():
        label_folder = folder.with_name("labels")
    
    if label_folder.exists():
        labels = list(label_folder.glob("*.txt"))
        print(f"   ✅ Train labels: {len(labels)} found")
        
        if len(labels) < len(train_images) * 0.8:
            print(f"   ⚠️ Warning: Some images may be missing labels")
    else:
        print(f"   ❌ No labels folder found!")
        return False
    
    # Check validation folder
    print(f"\n📁 Checking validation data...")
    
    val_folders = [
        data_path / "valid" / "images",
        data_path / "val" / "images",
        data_path / "validation" / "images",
        data_path / val_path if val_path else None,
    ]
    
    val_images = None
    for folder in val_folders:
        if folder and folder.exists():
            val_images = list(folder.glob("*.jpg")) + list(folder.glob("*.png"))
            if val_images:
                print(f"   ✅ Validation images: {len(val_images)} found")
                print(f"      Location: {folder}")
                break
    
    if not val_images:
        print(f"   ⚠️ No validation images found (optional but recommended)")
    
    # Summary
    print(f"\n" + "="*60)
    print(f"📊 DATASET SUMMARY")
    print(f"="*60)
    print(f"   Training images: {len(train_images)}")
    if val_images:
        print(f"   Validation images: {len(val_images)}")
    print(f"   Total: {len(train_images) + len(val_images) if val_images else len(train_images)}")
    
    # Recommendations
    total_images = len(train_images) + (len(val_images) if val_images else 0)
    
    print(f"\n💡 Assessment:")
    if total_images < 100:
        print(f"   ⚠️ {total_images} images is quite small")
        print(f"      Minimum: 100 images")
        print(f"      Recommended: 300+ images")
    elif total_images < 300:
        print(f"   ✅ {total_images} images is okay for training")
        print(f"      For better results: 300+ recommended")
    else:
        print(f"   ✅ {total_images} images is excellent!")
        print(f"      Ready for high-quality training!")
    
    print(f"\n✅ Dataset verification complete!")
    print(f"\n📝 Next step:")
    print(f"   python train_ic_model.py")
    
    return True

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify IC dataset')
    parser.add_argument('--path', type=str, default='data',
                       help='Path to dataset folder')
    
    args = parser.parse_args()
    
    verify_dataset(args.path)
