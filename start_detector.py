"""
SIMPLE IC DETECTOR LAUNCHER
Easy-to-use interface for improved IC detection
"""

import os
import sys
from pathlib import Path

def main_menu():
    """Show main menu"""
    while True:
        os.system('cls')
        print("=" * 70)
        print("          🔍 IMPROVED IC CHIP DETECTOR 🔍")
        print("=" * 70)
        print()
        print("  What would you like to do?")
        print()
        print("  1. 📹 Webcam Detection (Real-time)")
        print("  2. 📸 Detect IC from Phone Photo")
        print("  3. 📁 Browse and Select Image")
        print("  4. ❓ Help")
        print("  5. 🚪 Exit")
        print()
        print("=" * 70)
        
        choice = input("\n  Enter choice (1-5): ").strip()
        
        if choice == '1':
            webcam_mode()
        elif choice == '2':
            image_mode()
        elif choice == '3':
            browse_images()
        elif choice == '4':
            show_help()
        elif choice == '5':
            print("\n  👋 Goodbye!\n")
            sys.exit(0)
        else:
            input("\n  ❌ Invalid choice! Press Enter...")

def webcam_mode():
    """Run webcam detection"""
    os.system('cls')
    print("=" * 70)
    print("          📹 WEBCAM DETECTION MODE")
    print("=" * 70)
    print()
    print("  🎥 Starting webcam...")
    print()
    print("  ⌨️  Controls:")
    print("    'q' - Quit")
    print("    's' - Save screenshot")
    print("    'f' - Toggle IC filter")
    print("    '+' / '-' - Adjust confidence")
    print()
    print("=" * 70)
    print()
    input("  Press Enter to start webcam detection...")
    
    os.system('python improved_ic_detector.py --mode webcam --conf 0.4')
    
    input("\n  Press Enter to return to menu...")

def image_mode():
    """Detect IC from image file"""
    os.system('cls')
    print("=" * 70)
    print("          📸 IMAGE DETECTION MODE")
    print("=" * 70)
    print()
    
    # Check for images
    images = list(Path('.').glob('*.jpg')) + list(Path('.').glob('*.png')) + list(Path('.').glob('*.jpeg'))
    
    if images:
        print(f"  📁 Found {len(images)} image(s) in current folder:")
        print()
        for img in images[:5]:
            print(f"    • {img.name}")
        if len(images) > 5:
            print(f"    ... and {len(images) - 5} more")
        print()
    
    print("  📝 Enter image filename:")
    print("     (with extension: .jpg, .png, etc.)")
    print()
    
    filename = input("  Filename: ").strip()
    
    if not filename:
        input("\n  ❌ No filename entered! Press Enter...")
        return
    
    if not Path(filename).exists():
        print(f"\n  ❌ File not found: {filename}")
        print(f"\n  📂 Current directory: {Path.cwd()}")
        print(f"\n  💡 Make sure:")
        print(f"     • File is in current directory")
        print(f"     • Filename is correct (including extension)")
        print(f"     • Photo was transferred from phone")
        input("\n  Press Enter to continue...")
        return
    
    print(f"\n  🔍 Detecting ICs in: {filename}")
    print()
    
    os.system(f'python improved_ic_detector.py --mode image --image "{filename}" --conf 0.4')
    
    input("\n  Press Enter to return to menu...")

def browse_images():
    """Browse and select image"""
    os.system('cls')
    print("=" * 70)
    print("          📁 BROWSE IMAGES")
    print("=" * 70)
    print()
    
    # Find all images
    images = list(Path('.').glob('*.jpg')) + list(Path('.').glob('*.png')) + list(Path('.').glob('*.jpeg'))
    
    if not images:
        print("  ❌ No images found in current directory!")
        print()
        print("  📱 To add images:")
        print("     1. Take photo of IC chip with your phone")
        print("     2. Transfer to computer via:")
        print("        • WhatsApp Web")
        print("        • Email")
        print("        • USB cable")
        print("        • Cloud (Google Drive, OneDrive)")
        print(f"     3. Save to: {Path.cwd()}")
        print()
        input("  Press Enter to return...")
        return
    
    print(f"  ✅ Found {len(images)} image(s):")
    print()
    
    for i, img in enumerate(images, 1):
        size_kb = img.stat().st_size / 1024
        print(f"    {i}. {img.name} ({size_kb:.1f} KB)")
    
    print()
    choice = input("  Enter number to detect ICs (or 0 to cancel): ").strip()
    
    if not choice.isdigit():
        input("\n  ❌ Invalid input! Press Enter...")
        return
    
    choice_num = int(choice)
    
    if choice_num == 0:
        return
    
    if choice_num < 1 or choice_num > len(images):
        input("\n  ❌ Invalid number! Press Enter...")
        return
    
    selected = images[choice_num - 1]
    print(f"\n  🔍 Detecting ICs in: {selected.name}")
    print()
    
    os.system(f'python improved_ic_detector.py --mode image --image "{selected}" --conf 0.4')
    
    input("\n  Press Enter to return to menu...")

def show_help():
    """Show help information"""
    os.system('cls')
    print("=" * 70)
    print("          ❓ HELP & TIPS")
    print("=" * 70)
    print()
    print("  📖 WHAT IS THIS?")
    print("     This program detects IC chips (integrated circuits) from")
    print("     webcam or phone photos using AI (YOLOv8).")
    print()
    print("  🎯 WHAT DOES IT DETECT?")
    print("     ✅ Electronic IC chips (DIP, SMD, SOIC, QFP packages)")
    print("     ✅ Rectangular components with pins")
    print("     ✅ Microcontrollers, memory chips, etc.")
    print()
    print("     ❌ Does NOT detect:")
    print("        • Round components (resistors, capacitors)")
    print("        • Very small or very large objects")
    print("        • Non-rectangular shapes")
    print()
    print("  📸 TIPS FOR PHONE PHOTOS:")
    print("     • Use good lighting (natural light is best)")
    print("     • Hold camera steady")
    print("     • Get close enough to see IC clearly")
    print("     • Avoid shadows and glare")
    print("     • IC should fill at least 1/4 of frame")
    print("     • Capture text on IC if possible")
    print()
    print("  📹 TIPS FOR WEBCAM:")
    print("     • Position IC chip in front of webcam")
    print("     • Ensure good lighting")
    print("     • Hold IC steady")
    print("     • Adjust confidence if too sensitive/strict")
    print()
    print("  ⚙️ CONFIDENCE THRESHOLD:")
    print("     • Default: 0.4 (balanced)")
    print("     • Higher (0.6-0.8): Stricter, fewer false positives")
    print("     • Lower (0.2-0.3): More lenient, may detect non-ICs")
    print()
    print("  📁 FILE LOCATIONS:")
    print(f"     • Current folder: {Path.cwd()}")
    print(f"     • Screenshots saved here")
    print(f"     • Detected images saved as: detected_[filename].jpg")
    print()
    print("  🐛 TROUBLESHOOTING:")
    print("     • 'No IC detected': Try better lighting, get closer")
    print("     • 'Detecting everything': Increase confidence (+)")
    print("     • 'Not detecting IC': Decrease confidence (-)")
    print("     • 'Camera not opening': Check camera permissions")
    print()
    print("=" * 70)
    input("\n  Press Enter to return to menu...")

if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n  👋 Goodbye!\n")
        sys.exit(0)
