@echo off
title MOM Generator
color 0A
setlocal enabledelayedexpansion

set HF_HUB_DISABLE_SYMLINKS=1
set HF_HUB_DISABLE_SYMLINKS_WARNING=1

echo.
echo  ================================================================
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║           MOM GENERATOR - AI Meeting Assistant           ║
echo  ╚══════════════════════════════════════════════════════════╝
echo  ================================================================
echo.

:: ----------------------------------------------------------------
:: Check Python
:: ----------------------------------------------------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found. Please run  install\setup.bat  first!
    pause
    exit /b 1
)

:: ----------------------------------------------------------------
:: Check Ollama
:: ----------------------------------------------------------------
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Ollama not found. Please run  install\setup.bat  first!
    pause
    exit /b 1
)

:: ----------------------------------------------------------------
:: AUTO-UPDATE OLLAMA (silent, no prompts)
:: ----------------------------------------------------------------
echo  Checking for Ollama updates...

:: Get current installed version
set "CURRENT_VER="
for /f "tokens=4" %%v in ('ollama --version 2^>^&1') do set "CURRENT_VER=%%v"

:: Get latest version from GitHub API using PowerShell
set "LATEST_TAG="
for /f "usebackq delims=" %%t in (`powershell -NoProfile -Command "(Invoke-RestMethod -Uri 'https://api.github.com/repos/ollama/ollama/releases/latest' -TimeoutSec 4).tag_name" 2^>nul`) do set "LATEST_TAG=%%t"

if "%LATEST_TAG%"=="" goto SkipUpdate

:: Strip the leading 'v'
set "LATEST_VER=%LATEST_TAG:v=%"

if "%CURRENT_VER%"=="%LATEST_VER%" goto UpToDate
goto DoUpdate

:UpToDate
echo  Ollama is up to date (%CURRENT_VER%).
goto SkipUpdate

:DoUpdate
echo  [UPDATE] New Ollama version available: %LATEST_VER% (Current: %CURRENT_VER%)
echo  [UPDATE] Auto-updating Ollama silently in the background! The server will start now.

:: Create a background updater script so it doesn't block startup
echo @echo off > "%TEMP%\ollama_updater.bat"
echo title Ollama Updater >> "%TEMP%\ollama_updater.bat"
echo curl -sL "https://github.com/ollama/ollama/releases/download/v%LATEST_VER%/OllamaSetup.exe" -o "%%TEMP%%\OllamaSetup.exe" >> "%TEMP%\ollama_updater.bat"
echo if exist "%%TEMP%%\OllamaSetup.exe" ( >> "%TEMP%\ollama_updater.bat"
echo     taskkill /f /im "ollama app.exe" ^>nul 2^>^&1 >> "%TEMP%\ollama_updater.bat"
echo     taskkill /f /im ollama.exe ^>nul 2^>^&1 >> "%TEMP%\ollama_updater.bat"
echo     start /wait "" "%%TEMP%%\OllamaSetup.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART >> "%TEMP%\ollama_updater.bat"
echo     del "%%TEMP%%\OllamaSetup.exe" ^>nul 2^>^&1 >> "%TEMP%\ollama_updater.bat"
echo     start /MIN "" ollama serve >> "%TEMP%\ollama_updater.bat"
echo ) >> "%TEMP%\ollama_updater.bat"
echo del "%%~f0" >> "%TEMP%\ollama_updater.bat"

:: Launch updater in background silently
start /MIN "" "%TEMP%\ollama_updater.bat"
echo.
goto SkipUpdate

:SkipUpdate
if "%LATEST_TAG%"=="" echo  [INFO] Could not check for updates (offline?). Continuing with current version.

:: ----------------------------------------------------------------
:: Start Ollama service in background silently
:: ----------------------------------------------------------------
echo  Starting Ollama AI engine...
:: Do not use /B for ollama serve as it can sometimes hook the console.
:: Start it minimized in a separate window instead.
start /MIN "" ollama serve

:: Wait for Ollama to become responsive
:WaitForOllama
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 1 /nobreak >nul
    goto WaitForOllama
)

:: ----------------------------------------------------------------
:: Launch MOM Generator server + open browser
:: ----------------------------------------------------------------
echo.
echo  Starting MOM Generator server...
echo.
echo  ================================================================
echo  ^>^>^> Open your browser at: http://127.0.0.1:5001
echo  ^>^>^> Press CTRL+C in this window to stop the server.
echo  ================================================================
echo.

:: Get absolute path of the project root
set "STARTUP_DIR=%~dp0"
set "ROOT_DIR=%STARTUP_DIR%.."
cd /d "%ROOT_DIR%"

:: Start server in this window
python mom_api_server.py

pause
