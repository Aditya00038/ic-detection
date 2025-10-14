"""
AUTO-START ENHANCED IC DETECTION
Automatically launches webcam with enhanced detection
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from enhanced_ic_detector import EnhancedICDetector

if __name__ == "__main__":
    print("\n" + "="*70)
    print("⚡ ENHANCED IC DETECTION - AUTO WEBCAM MODE")
    print("="*70)
    print("Starting in 2 seconds...")
    print("="*70 + "\n")
    
    import time
    time.sleep(2)
    
    detector = EnhancedICDetector()
    detector.detect_webcam()
