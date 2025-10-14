"""
IC Detection - Interactive Launcher
Easy-to-use menu for IC chip detection
"""

import os
import sys
from pathlib import Path

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Display main menu"""
    clear_screen()
    print("=" * 60)
    print("           IC CHIP DETECTION SYSTEM")
    print("=" * 60)
    print()
    print("Select detection mode:")
    print()
    print("  1. 📹 Webcam Detection (Real-time)")
    print("  2. 📸 Image Detection (From file)")
    print("  3. 📁 List available images")
    print("  4. ℹ️  Help & Documentation")
    print("  5. 🚪 Exit")
    print()
    print("=" * 60)
    print()

def webcam_detection():
    """Run webcam detection"""
    clear_screen()
    print("=" * 60)
    print("           WEBCAM DETECTION MODE")
    print("=" * 60)
    print()
    print("🎥 Starting real-time IC chip detection...")
    print()
    print("⌨️  Controls:")
    print("  'q' - Quit")
    print("  's' - Save screenshot")
    print("  'c' - Toggle confidence display")
    print("  'f' - Toggle IC-only filter")
    print()
    print("=" * 60)
    print()
    
    # Check if conda base is active
    os.system('python ic_webcam.py --conf 0.5')
    
    input("\nPress Enter to return to menu...")

def image_detection():
    """Run image detection"""
    clear_screen()
    print("=" * 60)
    print("           IMAGE DETECTION MODE")
    print("=" * 60)
    print()
    
    # List available images
    image_files = list(Path('.').glob('*.jpg')) + list(Path('.').glob('*.png')) + list(Path('.').glob('*.jpeg'))
    
    if image_files:
        print("📁 Available images:")
        for i, img in enumerate(image_files, 1):
            print(f"  {i}. {img.name}")
        print()
    
    image_path = input("Enter image filename (or full path): ").strip()
    
    if not image_path:
        print("\n❌ No filename provided!")
        input("Press Enter to return to menu...")
        return
    
    if not Path(image_path).exists():
        print(f"\n❌ Error: File not found: {image_path}")
        print(f"\n💡 Make sure the image is in: {Path.cwd()}")
        input("\nPress Enter to return to menu...")
        return
    
    print(f"\n🔍 Processing image: {image_path}")
    print()
    
    os.system(f'python detect_ic_image.py --image "{image_path}" --conf 0.5')
    
    input("\nPress Enter to return to menu...")

def list_images():
    """List all images in directory"""
    clear_screen()
    print("=" * 60)
    print("           AVAILABLE IMAGES")
    print("=" * 60)
    print()
    
    image_files = list(Path('.').glob('*.jpg')) + list(Path('.').glob('*.png')) + list(Path('.').glob('*.jpeg'))
    
    if not image_files:
        print("❌ No images found in current directory!")
        print()
        print("📱 To add images:")
        print("  1. Transfer photo from your phone")
        print("  2. Save to: " + str(Path.cwd()))
        print("  3. Run this menu again and select option 2")
        print()
        print("📚 See PHONE_PHOTO_GUIDE.md for detailed instructions")
    else:
        print(f"✅ Found {len(image_files)} image(s):")
        print()
        for i, img in enumerate(image_files, 1):
            size = img.stat().st_size / 1024  # KB
            print(f"  {i}. {img.name} ({size:.1f} KB)")
        print()
        
        choice = input("\nEnter number to detect ICs (or Enter to cancel): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(image_files):
            selected = image_files[int(choice) - 1]
            print(f"\n🔍 Processing: {selected.name}")
            os.system(f'python detect_ic_image.py --image "{selected}" --conf 0.5')
    
    input("\nPress Enter to return to menu...")

def show_help():
    """Show documentation"""
    clear_screen()
    print("=" * 60)
    print("           HELP & DOCUMENTATION")
    print("=" * 60)
    print()
    print("📚 Available documentation files:")
    print()
    print("  1. PHONE_PHOTO_GUIDE.md       - Use photos from phone")
    print("  2. IC_CHIP_DETECTION.md       - Complete guide")
    print("  3. STRICT_FILTERING_ENABLED.md - Filter details")
    print("  4. RUNNING_STATUS.md          - System status")
    print("  5. START_HERE.md              - Project overview")
    print()
    print("=" * 60)
    print()
    print("🚀 Quick Start:")
    print()
    print("For Webcam:")
    print("  1. Select option 1 from main menu")
    print("  2. Point camera at IC chips")
    print("  3. Press 'q' to quit")
    print()
    print("For Phone Photos:")
    print("  1. Transfer photo to this folder")
    print("  2. Select option 2 from main menu")
    print("  3. Enter filename")
    print("  4. View results!")
    print()
    print("=" * 60)
    print()
    print("📋 What Gets Detected:")
    print()
    print("  ✅ Electronic IC chips (rectangular)")
    print("  ✅ DIP packages, SMD chips, SOIC, QFP")
    print("  ✅ Size: 50-400 pixels")
    print("  ✅ Aspect ratio: 0.5-2.0 (IC-typical)")
    print()
    print("  ❌ Round components (resistors, capacitors)")
    print("  ❌ Very small or very large objects")
    print("  ❌ Non-rectangular shapes")
    print()
    
    input("Press Enter to return to menu...")

def main():
    """Main program loop"""
    while True:
        show_menu()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            webcam_detection()
        elif choice == '2':
            image_detection()
        elif choice == '3':
            list_images()
        elif choice == '4':
            show_help()
        elif choice == '5':
            clear_screen()
            print("\n👋 Thank you for using IC Chip Detection System!\n")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice! Please enter 1-5")
            input("Press Enter to continue...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("\n👋 Goodbye!\n")
        sys.exit(0)
