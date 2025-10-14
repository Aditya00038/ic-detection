@echo off
REM Quick Start Script for IC Detection
REM Choose what you want to do

:menu
cls
echo.
echo ========================================
echo    IC DETECTION SYSTEM - QUICK START
echo ========================================
echo.
echo 1. Setup Environment (First time only)
echo 2. Demo: Webcam Detection
echo 3. Demo: Image Detection
echo 4. Train Model
echo 5. Detect with Trained Model
echo 6. Exit
echo.
echo ========================================
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto webcam
if "%choice%"=="3" goto image
if "%choice%"=="4" goto train
if "%choice%"=="5" goto detect
if "%choice%"=="6" goto end

echo Invalid choice! Please try again.
timeout /t 2 >nul
goto menu

:setup
cls
echo.
echo ========================================
echo    SETTING UP ENVIRONMENT
echo ========================================
echo.
powershell -ExecutionPolicy Bypass -File setup.ps1
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:webcam
cls
echo.
echo ========================================
echo    WEBCAM DETECTION DEMO
echo ========================================
echo.
echo Starting webcam detection...
echo Press 'q' to quit, 's' to save screenshot
echo.
call venv\Scripts\activate.bat
python demo.py --mode webcam
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:image
cls
echo.
echo ========================================
echo    IMAGE DETECTION DEMO
echo ========================================
echo.
set /p imgpath="Enter image path (or press Enter for test.jpg): "
if "%imgpath%"=="" set imgpath=test.jpg
echo.
echo Detecting in: %imgpath%
echo.
call venv\Scripts\activate.bat
python demo.py --mode image --source %imgpath%
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:train
cls
echo.
echo ========================================
echo    TRAIN IC DETECTION MODEL
echo ========================================
echo.
echo Make sure you have prepared your dataset!
echo Dataset should be in data/train/ and data/val/
echo.
set /p confirm="Continue with training? (y/n): "
if /i not "%confirm%"=="y" goto menu
echo.
set /p epochs="Enter number of epochs (default 100): "
if "%epochs%"=="" set epochs=100
echo.
echo Training for %epochs% epochs...
echo This may take several hours!
echo.
call venv\Scripts\activate.bat
python src/train.py --epochs %epochs%
echo.
echo Training complete!
echo Model saved to models/best.pt
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:detect
cls
echo.
echo ========================================
echo    DETECT WITH TRAINED MODEL
echo ========================================
echo.
set /p source="Enter image/video/folder path: "
echo.
echo Detecting...
echo.
call venv\Scripts\activate.bat
python src/detect.py --source %source% --weights models/best.pt
echo.
echo Detection complete!
echo Results saved to results/
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:end
cls
echo.
echo Thank you for using IC Detection System!
echo.
timeout /t 2 >nul
exit
