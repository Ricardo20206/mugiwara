@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   LANCEMENT CHRONOBIO - STRATEGIE OPTIMISEE
echo ========================================
echo.

echo Activation environnement virtuel...
call .venv\Scripts\activate.bat

echo.
echo Lancement du jeu complet (5 joueurs)...
echo.
powershell -ExecutionPolicy Bypass -File ".\lancer_5clients.ps1"

pause
