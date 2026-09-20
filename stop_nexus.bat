@echo off
title Detener NEXUS Life OS
echo ===================================================
echo   Deteniendo servidor de NEXUS Life OS...
echo ===================================================

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$conns = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue; " ^
  "if ($conns) { " ^
  "  foreach ($c in $conns) { " ^
  "    Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue; " ^
  "    Write-Host ('Proceso finalizado con PID: ' + $c.OwningProcess); " ^
  "  } " ^
  "  Write-Host 'Servidor detenido exitosamente.'; " ^
  "} else { " ^
  "  Write-Host 'No habia ningun servidor activo en el puerto 8501.'; " ^
  "}"

echo ===================================================
ping 127.0.0.1 -n 3 >nul
