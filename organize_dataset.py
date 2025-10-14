"""
IC Dataset Organizer
Helps prepare your IC images for training
"""

import os
import shutil
from pathlib import Path
import cv2

def check_images(source_folder):
    """Check images in folder and provide statistics"""
    
    print("\n" + "="*60)
    print("📊 IC IMAGE DATASET CHECKER")
    print("="*60)
    
    if not Path(source_folder).exists():
        print(f"\n❌ Folder not found: {source_folder}")
        print(f"\n💡 Please provide the correct path to your IC images")
        return
    
    # Supported formats
    formats = ['.jpg', '.jpeg', '.png', '.bmp']
    
    # Find all images
    images = []
    for fmt in formats:
        images.extend(list(Path(source_folder).rglob(f'*{fmt}')))
        images.extend(list(Path(source_folder).rglob(f'*{fmt.upper()}')))
    
    if not images:
        print(f"\n❌ No images found in: {source_folder}")
        print(f"\n💡 Supported formats: {', '.join(formats)}")
        return
    
    print(f"\n✅ Found {len(images)} images")
    print(f"📂 Source: {source_folder}")
    
    # Check image properties
    print(f"\n🔍 Analyzing images...")
    
    valid_count = 0
    invalid_count = 0
    sizes = []
    
    for img_path in images:
        try:
            img = cv2.imread(str(img_path))
            if img is not None:
                valid_count += 1
                h, w = img.shape[:2]
                sizes.append((w, h))
            else:
                invalid_count += 1
                print(f"  ⚠️ Cannot read: {img_path.name}")
        except Exception as e:
            invalid_count += 1
            print(f"  ❌ Error reading: {img_path.name}")
    
    print(f"\n📊 Statistics:")
    print(f"  Valid images: {valid_count}")
    print(f"  Invalid/corrupt: {invalid_count}")
    
    if sizes:
        widths = [s[0] for s in sizes]
        heights = [s[1] for s in sizes]
        print(f"\n📐 Image sizes:")
        print(f"  Width range: {min(widths)} - {max(widths)} px")
        print(f"  Height range: {min(heights)} - {max(heights)} px")
        print(f"  Average: {sum(widths)//len(widths)}x{sum(heights)//len(heights)} px")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    if valid_count < 100:
        print(f"  ⚠️ {valid_count} images is quite small")
        print(f"     Minimum: 100 images")
        print(f"     Recommended: 300+ images")
        print(f"     Need {100 - valid_count} more for minimum")
    elif valid_count < 300:
        print(f"  ✅ {valid_count} images is okay for training")
        print(f"     For better results: 300+ images recommended")
    else:
        print(f"  ✅ {valid_count} images is great for training!")
    
    return images

def organize_images(source_folder, dest_folder="data/raw/ic_images"):
    """Copy images to organized folder"""
    
    print(f"\n" + "="*60)
    print(f"📁 ORGANIZING IMAGES")
    print(f"="*60)
    
    # Create destination
    dest_path = Path(dest_folder)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Find images
    formats = ['.jpg', '.jpeg', '.png', '.bmp']
    images = []
    for fmt in formats:
        images.extend(list(Path(source_folder).rglob(f'*{fmt}')))
        images.extend(list(Path(source_folder).rglob(f'*{fmt.upper()}')))
    
    if not images:
        print(f"❌ No images found")
        return
    
    print(f"\n📋 Copying {len(images)} images...")
    print(f"   From: {source_folder}")
    print(f"   To:   {dest_folder}")
    print()
    
    copied = 0
    skipped = 0
    
    for i, img_path in enumerate(images, 1):
        try:
            # Create sequential name
            new_name = f"ic_{i:04d}{img_path.suffix.lower()}"
            dest_file = dest_path / new_name
            
            # Check if image is valid
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"  ⚠️ Skip (invalid): {img_path.name}")
                skipped += 1
                continue
            
            # Copy
            shutil.copy2(img_path, dest_file)
            copied += 1
            
            if i % 50 == 0:
                print(f"  ✓ Copied {i}/{len(images)} images...")
        
        except Exception as e:
            print(f"  ❌ Error copying {img_path.name}: {e}")
            skipped += 1
    
    print(f"\n✅ Done!")
    print(f"   Copied: {copied} images")
    print(f"   Skipped: {skipped} images")
    print(f"   Location: {dest_path.absolute()}")
    
    return copied

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IC Dataset Organizer')
    parser.add_argument('--check', type=str, help='Check images in folder')
    parser.add_argument('--organize', type=str, help='Organize images from folder')
    parser.add_argument('--dest', type=str, default='data/raw/ic_images',
                       help='Destination folder')
    
    args = parser.parse_args()
    
    if args.check:
        images = check_images(args.check)
        
        if images and len(images) > 0:
            print(f"\n" + "="*60)
            print(f"✅ Images are ready!")
            print(f"="*60)
            print(f"\n📝 Next steps:")
            print(f"   1. Organize: python organize_dataset.py --organize \"{args.check}\"")
            print(f"   2. Label images using Roboflow or LabelImg")
            print(f"   3. Train model: python train_ic_model.py")
    
    elif args.organize:
        copied = organize_images(args.organize, args.dest)
        
        if copied and copied > 0:
            print(f"\n" + "="*60)
            print(f"✅ Images organized!")
            print(f"="*60)
            print(f"\n📝 Next steps:")
            print(f"   1. Label images:")
            print(f"      • Roboflow: https://roboflow.com/")
            print(f"      • LabelImg: pip install labelImg; labelImg")
            print(f"   2. After labeling, run: python train_ic_model.py")
    
    else:
        print("="*60)
        print("IC DATASET ORGANIZER")
        print("="*60)
        print()
        print("Usage:")
        print()
        print("  Check images:")
        print("    python organize_dataset.py --check \"D:\\Your\\IC\\Images\\Folder\"")
        print()
        print("  Organize images:")
        print("    python organize_dataset.py --organize \"D:\\Your\\IC\\Images\\Folder\"")
        print()
        print("  Organize to custom location:")
        print("    python organize_dataset.py --organize \"D:\\IC\\Images\" --dest \"custom/folder\"")
        print()
        print("Examples:")
        print("  python organize_dataset.py --check \"D:\\Photos\\IC_Chips\"")
        print("  python organize_dataset.py --organize \"D:\\Photos\\IC_Chips\"")

if __name__ == '__main__':
    main()
