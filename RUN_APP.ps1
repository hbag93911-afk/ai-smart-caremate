# AI Smart CareMATE - Quick Start Script for PowerShell
# 
# This script will:
# 1. Check Python installation
# 2. Install/verify Streamlit
# 3. Start the app
#

Write-Host ""
Write-Host "==============================================="
Write-Host "AI Smart CareMATE - Startup Script" -ForegroundColor Cyan
Write-Host "==============================================="
Write-Host ""

# Check Python installation
Write-Host "[1] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and add it to PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check Streamlit
Write-Host "[2] Checking Streamlit..." -ForegroundColor Yellow
$streamlitCheck = python -c "import streamlit; print(streamlit.__version__)" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Streamlit not found, installing..." -ForegroundColor Yellow
    pip install streamlit
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install Streamlit" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[OK] Streamlit $streamlitCheck" -ForegroundColor Green
}
Write-Host ""

# Check other required libraries
Write-Host "[3] Checking required libraries..." -ForegroundColor Yellow
$libCheck = python -c "import cv2, mediapipe, altair" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Some libraries missing, installing..." -ForegroundColor Yellow
    pip install opencv-python-headless mediapipe altair
}
Write-Host "[OK] All libraries ready" -ForegroundColor Green
Write-Host ""

# Start the app
Write-Host "[4] Starting AI Smart CareMATE app..." -ForegroundColor Yellow
Write-Host ""
Write-Host "==============================================="
Write-Host "App starting at: http://localhost:8501" -ForegroundColor Cyan
Write-Host "==============================================="
Write-Host ""
Write-Host "Press Ctrl+C to stop the app"
Write-Host ""

python -m streamlit run app.py
