@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Drag an MP4, M4A, or MP3 file onto this .bat file.
  pause
  exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0transcribe.ps1" -MediaPath "%~f1"
set "transcribe_exit=%errorlevel%"
echo.
pause
exit /b %transcribe_exit%
