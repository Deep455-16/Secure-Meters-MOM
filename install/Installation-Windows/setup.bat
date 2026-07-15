@echo off
setlocal enabledelayedexpansion
title MOM Generator - First Time Setup
color 0A

:: Get the directory of this batch file (install/) and navigate to project root
set "INSTALL_DIR=%~dp0"
set "ROOT_DIR=%INSTALL_DIR%.."
cd /d "%ROOT_DIR%"

echo.
echo  ================================================================
echo   MOM GENERATOR - AUTOMATED SETUP
echo   AI-Powered Minutes of Meeting Application
echo  ================================================================
echo.
echo  This script installs EVERYTHING needed to run MOM Generator.
echo  It may take 10-20 minutes on first run (downloading AI models).
echo.
echo  DO NOT CLOSE this window until you see "SETUP COMPLETE!"
echo.
pause

:: ================================================================
:: STEP 1: Check Administrator (recommended for Ollama install)
:: ================================================================
echo.
echo  [STEP 1/6]  Checking system privileges...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [!] TIP: If installation fails, close this window and
    echo      right-click install\setup.bat then "Run as Administrator"
    echo.
    timeout /t 3 /nobreak >nul
) else (
    echo  Running with Administrator privileges.
)

:: ================================================================
:: STEP 2: Check / Install Python
:: ================================================================
echo.
echo  [STEP 2/6]  Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Python not found. Attempting automatic install via winget...
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo.
        echo  ================================================================
        echo   [ACTION REQUIRED] Could not auto-install Python.
        echo.
        echo   Please download and install Python 3.11 manually:
        echo   https://www.python.org/downloads/
        echo.
        echo   IMPORTANT: During install, CHECK "Add Python to PATH"
        echo   Then close this window and run setup.bat again.
        echo  ================================================================
        pause
        exit /b 1
    )
    echo  Python installed successfully!
) else (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  Found: %%v
)

:: ================================================================
:: STEP 3: Upgrade pip and Install Python Packages
:: ================================================================
echo.
echo  [STEP 3/6]  Installing Python packages...
echo  (This downloads AI libraries - may take 5-10 minutes)
echo.

set HF_HUB_DISABLE_SYMLINKS=1
set HF_HUB_DISABLE_SYMLINKS_WARNING=1

python -m pip install --upgrade pip --quiet
python -m pip install -r "%INSTALL_DIR%requirements.txt"
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Failed to install Python packages.
    echo  Check your internet connection and try again.
    pause
    exit /b 1
)
echo.
echo  All Python packages installed!

:: ================================================================
:: STEP 4: Check / Install Ollama (Local AI Engine)
:: ================================================================
echo.
echo  [STEP 4/6]  Checking Ollama (Local AI engine)...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Ollama not found. Attempting automatic install...
    winget install Ollama.Ollama --silent --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo.
        echo  Trying direct download from ollama.com...
        powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%TEMP%\OllamaSetup.exe'; Start-Process '%TEMP%\OllamaSetup.exe' -Wait"
        if %errorlevel% neq 0 (
            echo.
            echo  ================================================================
            echo   [ACTION REQUIRED] Could not auto-install Ollama.
            echo.
            echo   Please download and install Ollama manually:
            echo   https://ollama.com/download
            echo.
            echo   After installing Ollama, run setup.bat again.
            echo  ================================================================
            pause
            exit /b 1
        )
    )
    echo  Ollama installed successfully!
    timeout /t 3 /nobreak >nul
) else (
    for /f "tokens=*" %%v in ('ollama --version 2^>^&1') do echo  Found: %%v
)

:: ================================================================
:: STEP 5: Pull AI Models via Ollama
:: ================================================================
echo.
echo  [STEP 5/6]  Downloading AI models...
echo.
echo  Starting Ollama service...
start /B "" ollama serve >nul 2>&1
timeout /t 4 /nobreak >nul

:wait_ollama
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 2 /nobreak >nul
    goto wait_ollama
)
echo  Ollama service is ready.
echo.

echo  Downloading qwen2.5:1.5b  (Chunking model  - ~1.0 GB)...
ollama pull qwen2.5:1.5b
if %errorlevel% neq 0 echo  [WARNING] qwen2.5:1.5b download failed - will retry on first launch.

echo.
echo  Downloading qwen2.5:7b  (Refinement model - ~4.7 GB)...
ollama pull qwen2.5:7b
if %errorlevel% neq 0 echo  [WARNING] qwen2.5:7b download failed - will retry on first launch.

echo.
echo  AI models ready!

:: ================================================================
:: STEP 6: Create .env config in project root
:: ================================================================
echo.
echo  [STEP 6/6]  Creating configuration...
(
    echo # MOM Generator Environment Config - auto-generated by setup.bat
    echo HF_HUB_DISABLE_SYMLINKS=1
    echo HF_HUB_DISABLE_SYMLINKS_WARNING=1
    echo OLLAMA_URL=http://127.0.0.1:11434
) > "%ROOT_DIR%\.env"
echo  Configuration file created.

:: ================================================================
:: SETUP COMPLETE
:: ================================================================
echo.
echo  ================================================================
echo   SETUP COMPLETE!
echo  ================================================================
echo.
echo   Everything is installed and ready to use!
echo.
echo   HOW TO USE THE APP:
echo     1. Double-click  START_APP.bat  (in the main folder)
echo     2. Your browser will open automatically
echo     3. Use the app at http://127.0.0.1:5001
echo.
echo   You only need to run setup.bat ONCE.
echo   For all future launches, just use START_APP.bat
echo.

:: Auto-start the server now
echo  Starting MOM Generator server...
echo.
set HF_HUB_DISABLE_SYMLINKS=1
set HF_HUB_DISABLE_SYMLINKS_WARNING=1
start "" "http://127.0.0.1:5001"
python "%ROOT_DIR%\mom_api_server.py"

pause
