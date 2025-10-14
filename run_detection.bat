@echo off
REM IC Detection - Quick Launcher Menu
title IC Chip Detection System

:menu
cls
echo.
echo ===============================================
echo     IC CHIP DETECTION SYSTEM
echo ===============================================
echo.
echo Select detection mode:
echo.
echo  1. Webcam Detection (Real-time)
echo  2. Image Detection (From file)
echo  3. Test with sample (if available)
echo  4. Help / Documentation
echo  5. Exit
echo.
echo ===============================================
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto webcam
if "%choice%"=="2" goto image
if "%choice%"=="3" goto test
if "%choice%"=="4" goto help
if "%choice%"=="5" goto exit
goto menu

:webcam
cls
echo.
echo ===============================================
echo     WEBCAM DETECTION MODE
echo ===============================================
echo.
echo Starting real-time IC chip detection...
echo.
echo Controls:
echo   'q' - Quit
echo   's' - Save screenshot
echo   'c' - Toggle confidence
echo   'f' - Toggle IC filter
echo.
python ic_webcam.py --conf 0.5
pause
goto menu

:image
cls
echo.
echo ===============================================
echo     IMAGE DETECTION MODE
echo ===============================================
echo.
set /p imagefile="Enter image filename (e.g., photo.jpg): "

if not exist "%imagefile%" (
    echo.
    echo ERROR: File not found: %imagefile%
    echo.
    echo Make sure the image is in the current directory:
    echo %cd%
    echo.
    pause
    goto menu
)

echo.
echo Processing image: %imagefile%
echo.
python detect_ic_image.py --image "%imagefile%" --conf 0.5
echo.
pause
goto menu

:test
cls
echo.
echo ===============================================
echo     TEST MODE
echo ===============================================
echo.
echo Checking for test images...
echo.

dir *.jpg *.png *.jpeg /b 2>nul | findstr /i "." >nul
if errorlevel 1 (
    echo No images found in current directory.
    echo.
    echo To test:
    echo 1. Transfer a photo from your phone
    echo 2. Save it to: %cd%
    echo 3. Run this menu again and select option 2
    echo.
) else (
    echo Found images:
    dir *.jpg *.png *.jpeg /b 2>nul
    echo.
    set /p testimg="Enter filename to test (or press Enter to cancel): "
    if not "%testimg%"=="" (
        python detect_ic_image.py --image "%testimg%" --conf 0.5
    )
)
pause
goto menu

:help
cls
echo.
echo ===============================================
echo     DOCUMENTATION
echo ===============================================
echo.
echo Quick Start Guides:
echo.
echo 1. PHONE_PHOTO_GUIDE.md    - How to use photos from phone
echo 2. IC_CHIP_DETECTION.md    - Complete documentation
echo 3. STRICT_FILTERING_ENABLED.md - Filtering details
echo 4. RUNNING_STATUS.md       - Current system status
echo.
echo Opening PHONE_PHOTO_GUIDE.md...
echo.
type PHONE_PHOTO_GUIDE.md | more
echo.
pause
goto menu

:exit
echo.
echo Thank you for using IC Chip Detection System!
echo.
exit /b

