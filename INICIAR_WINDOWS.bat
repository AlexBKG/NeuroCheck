@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 (echo No se pudo crear el entorno Python.& pause & exit /b 1)
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (echo Fallo la instalacion de dependencias.& pause & exit /b 1)
".venv\Scripts\python.exe" app.py
pause
