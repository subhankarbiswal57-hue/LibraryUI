@echo off
title Library Management System
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo An error occurred running the application.
    pause
)
