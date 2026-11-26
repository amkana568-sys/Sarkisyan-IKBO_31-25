@echo off
set "OUTPUT=%~1"
if "%OUTPUT%"=="" set "OUTPUT=result.json"
python "%~dp0src\main.py" --output "%OUTPUT%"
