@echo off
cd /d "%~dp0"
pyside6-uic src/gui/interface.ui -o src/gui/interface.py
start "" pythonw src/main.py