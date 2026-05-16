@echo off
title Sistema de Ficha Técnica
color 0A

echo.
echo ========================================
echo   SISTEMA DE FICHA TECNICA
echo   Sinara Bordignon Assessoria
echo ========================================
echo.
echo Iniciando sistema...
echo.

cd /d "%~dp0"

python -m streamlit run app.py

pause
