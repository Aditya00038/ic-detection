@echo off
echo ======================================================================
echo QUICK IC DETECTION DEMO - Works immediately!
echo ======================================================================
echo.

cd /d "d:\SIH PS-162\ic-detection-yolo"

REM Use conda run to avoid activation issues
C:\Users\sagitec\anaconda3\Scripts\conda.exe run -n base python quick_ic_demo.py

pause
