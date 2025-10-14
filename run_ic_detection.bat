@echo off
REM IC Chip Detection Launcher
echo.
echo =======================================
echo   IC Chip Detection System
echo =======================================
echo.
echo Starting IC chip webcam detection...
echo.

REM Run with conda base environment (where ultralytics is installed)
python ic_webcam.py %*

pause
