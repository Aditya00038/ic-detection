@echo off
echo ======================================================================
echo STARTING IC CHIP MODEL TRAINING (with OpenMP fix)
echo ======================================================================
echo.

REM Fix OpenMP duplicate library error
set KMP_DUPLICATE_LIB_OK=TRUE

REM Navigate to project directory
cd /d "d:\SIH PS-162\ic-detection-yolo"

REM Activate conda environment
call conda activate base

REM Start training
echo Starting training... (This will take 2-6 hours on CPU)
echo.
python train_ic_model.py

echo.
echo ======================================================================
echo Training completed! Check results in runs/detect/ic_detector/
echo ======================================================================
pause
