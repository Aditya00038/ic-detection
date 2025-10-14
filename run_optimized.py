"""
AUTO-START OPTIMIZED IC DETECTOR
Better IC detection with improved accuracy
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from optimized_ic_detector import OptimizedICDetector

if __name__ == "__main__":
    print("\n" + "="*70)
    print("⚡ OPTIMIZED IC DETECTION - AUTO START")
    print("="*70)
    print("Improvements for better IC detection:")
    print("  ✅ 10-point analysis system")
    print("  ✅ Better pin line detection")
    print("  ✅ Enhanced face rejection")
    print("  ✅ Brightness & saturation filtering")
    print("="*70)
    print("\n💡 TIPS:")
    print("   • Hold IC chip flat (parallel to camera)")
    print("   • Distance: 15-25cm from camera")
    print("   • Good lighting (not too bright)")
    print("   • Plain background works best")
    print("="*70)
    print("\nStarting in 2 seconds...\n")
    
    import time
    time.sleep(2)
    
    detector = OptimizedICDetector()
    detector.detect_webcam()
