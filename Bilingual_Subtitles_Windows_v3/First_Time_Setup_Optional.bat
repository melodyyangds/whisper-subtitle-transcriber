@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0transcribe.ps1" -SetupOnly
if errorlevel 1 echo There was an error. Read the message above.
echo.
pause
