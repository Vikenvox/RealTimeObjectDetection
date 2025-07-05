@echo off
title Advanced Real-Time Object Detection
cd /d "C:\Users\morig\RealTimeObjectDetection"
echo 🚀 Starting Advanced Real-Time Object Detection System...
echo.
python advanced_app.py
if %errorlevel% neq 0 (
    echo.
    echo ⚠️ Advanced version failed, trying enhanced version...
    python enhanced_app.py
)
pause
