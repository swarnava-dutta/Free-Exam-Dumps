@echo off
setlocal EnableExtensions
rem UTF-8 console so exam names with accented characters print instead of crashing.
chcp 65001 >nul
title ExamTopics Scraper

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    echo [WARN] .venv not found. Run install_dependencies.bat first.
    echo Trying system Python instead...
    echo.
    python main.py
)

echo.
pause
