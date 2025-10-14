@echo off
REM Direct IC Detection - No Menu
REM Just runs immediately

cd /d "d:\SIH PS-162\ic-detection-yolo"

echo.
echo ============================================================
echo          STRICT IC-ONLY DETECTOR (No Menu)
echo ============================================================
echo.
echo Starting in 2 seconds...
echo.
timeout /t 2 /nobreak > nul

REM Activate conda and run
call conda activate base
python strict_ic_detector.py --mode webcam --conf 0.5

pause
