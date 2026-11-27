@echo off
REM AI Smart CareMATE - Quick Start Script for Windows
REM 
REM This script will:
REM 1. Check Python installation
REM 2. Install/verify Streamlit
REM 3. Start the app
REM

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo AI Smart CareMATE - Startup Script
echo ===============================================
echo.

REM Check Python installation
echo [1] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION%
echo.

REM Check Streamlit
echo [2] Checking Streamlit...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Streamlit not found, installing...
    pip install streamlit
    if errorlevel 1 (
        echo ERROR: Failed to install Streamlit
        pause
        exit /b 1
    )
) else (
    for /f "tokens=*" %%i in ('python -c "import streamlit; print(streamlit.__version__)"') do set ST_VERSION=%%i
    echo [OK] Streamlit !ST_VERSION!
)
echo.

REM Check other required libraries
echo [3] Checking required libraries...
python -c "import cv2, mediapipe, altair" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Some libraries missing, installing...
    pip install opencv-python-headless mediapipe altair
)
echo [OK] All libraries ready
echo.

REM Start the app
echo [4] Starting AI Smart CareMATE app...
echo.
echo ===============================================
echo App starting at: http://localhost:8501
echo ===============================================
echo.
echo Press Ctrl+C to stop the app
echo.

python -m streamlit run app.py
