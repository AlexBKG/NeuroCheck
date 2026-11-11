@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Primero ejecuta INICIAR_WINDOWS.bat
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pytest -v
pause
