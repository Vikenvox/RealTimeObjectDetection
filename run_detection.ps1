#!/usr/bin/env pwsh

# Real-Time Object Detection Launcher
Write-Host "Real-Time Object Detection System" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# Change to project directory
Set-Location "C:\Users\morig\RealTimeObjectDetection"

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Python not found in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if camera is available
Write-Host "Checking camera availability..." -ForegroundColor Yellow
try {
    python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera status:', 'Available' if cap.isOpened() else 'Not available'); cap.release()"
} catch {
    Write-Host "Warning: Could not check camera status" -ForegroundColor Yellow
}

# Launch application
Write-Host "Launching application..." -ForegroundColor Green
python enhanced_app.py

Write-Host "Application closed." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
