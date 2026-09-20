@echo off
title NEXUS Life OS - Servidor Local
cd /d "C:\Antigravity\CONEXIONES\nexus-life-os"

:: 1. Verificar si el servidor ya está activo en el puerto 8501
netstat -ano | findstr /R /C:":8501 .*LISTENING" >nul
if not errorlevel 1 (
    start http://127.0.0.1:8501
    exit /b
)

:: 2. Localizar Python
set "PYTHON_EXE=C:\Users\Victus\AppData\Local\Programs\Python\Python312\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

:: 3. Abrir el navegador tras 2 segundos de espera
start "" cmd /c "ping 127.0.0.1 -n 3 >nul && start http://127.0.0.1:8501"

:: 4. Ejecutar servidor Streamlit en modo local
"%PYTHON_EXE%" -m streamlit run src\dashboards\app.py --server.port=8501 --server.address=127.0.0.1 --server.headless=true
