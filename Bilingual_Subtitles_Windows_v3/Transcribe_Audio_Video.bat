@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
    powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0transcribe.ps1" -Model small
) else (
    powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0transcribe.ps1" -MediaPath "%~f1" -Model small
)
if errorlevel 1 echo There was an error. Read the message above.
echo.
pause
