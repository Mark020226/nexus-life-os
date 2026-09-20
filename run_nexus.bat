@echo off
title NEXUS Life OS - Servidor Local
cd /d "C:\Antigravity\CONEXIONES\nexus-life-os"

echo ===================================================
echo   Iniciando NEXUS Life OS (Segundo Cerebro y Vida)
echo ===================================================

set "PYTHON_EXE=C:\Users\Victus\AppData\Local\Programs\Python\Python312\python.exe"

if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

:: Abrir navegador local en 2 segundos
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8501"

:: Ejecutar servidor Streamlit exclusivamente local (sin alertas de Firewall)
"%PYTHON_EXE%" -m streamlit run src\dashboards\app.py --server.port=8501 --server.address=127.0.0.1

pause
