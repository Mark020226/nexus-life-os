@echo off
title NEXUS Life OS - Servidor Local
cd /d "C:\Antigravity\CONEXIONES\nexus-life-os"
echo ===================================================
echo   Iniciando NEXUS Life OS (Segundo Cerebro y Vida)
echo ===================================================
python -m streamlit run src\dashboards\app.py
pause