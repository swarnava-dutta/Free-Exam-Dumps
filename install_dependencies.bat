@echo off
setlocal EnableExtensions
rem UTF-8 console so exam names with accented characters print instead of crashing.
chcp 65001 >nul
title ExamTopics Scraper - Install

cd /d "%~dp0"

echo.
echo ============================================================
echo   ExamTopics Scraper - Install
echo ============================================================
echo.

set "PY_CMD=py -3"
where py >nul 2>&1 || set "PY_CMD=python"

if not exist ".venv\Scripts\python.exe" (
    echo [1/2] Creating virtual environment...
    %PY_CMD% -m venv .venv
    if errorlevel 1 goto no_python
) else (
    echo [1/2] Virtual environment already exists.
)

echo [2/2] Installing requests and tqdm...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto failed

echo.
echo ============================================================
echo   Done. Next: double-click run_scraper.bat
echo ============================================================
echo.
pause
exit /b 0

:no_python
echo.
echo [ERROR] Could not create the virtual environment.
echo Install Python 3 from python.org, tick "Add python.exe to PATH",
echo then run this file again.
goto failed

:failed
echo.
echo ============================================================
echo   Install failed. Check the error above.
echo ============================================================
echo.
pause
exit /b 1
