@echo off
REM ============================================
REM HANDYCAT SPACE - Game Launcher
REM ============================================
REM This script runs the game from any location
REM by changing to the script's directory first

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Python is not installed or not in PATH
    echo ========================================
    echo.
    echo Please install Python from: https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if thegame.py exists
if not exist "thegame.py" (
    echo.
    echo ========================================
    echo ERROR: thegame.py not found!
    echo ========================================
    echo.
    echo Make sure thegame.py is in the same folder as RUN.bat
    echo Current location: %SCRIPT_DIR%
    echo.
    pause
    exit /b 1
)

REM Check if required Python packages are installed
echo Checking required packages...
python -c "import pygame, cv2, mediapipe, numpy" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo Installing required packages...
    echo ========================================
    echo.
    python -m pip install -q pygame opencv-python mediapipe numpy
    if errorlevel 1 (
        echo.
        echo ========================================
        echo ERROR: Failed to install packages
        echo ========================================
        echo.
        pause
        exit /b 1
    )
    echo Packages installed successfully!
    echo.
)

REM Launch the game
echo ========================================
echo Starting HANDYCAT SPACE...
echo ========================================
echo.
python thegame.py

REM If game crashes, show error message
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Game crashed!
    echo ========================================
    echo.
    pause
)

endlocal
exit /b 0
