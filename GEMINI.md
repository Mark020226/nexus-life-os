# Reglas del Proyecto NEXUS Life OS

## Servidor Local de Streamlit
- El servidor de **NEXUS Life OS** funciona de forma **autónoma y automática** directamente en el sistema operativo (Windows Startup / servicio local) en el puerto `8501` (`http://127.0.0.1:8501`).
- **REGLA CRÍTICA PARA AGENTES:** **NUNCA** ejecutes `streamlit run` o `python -m streamlit run` como proceso demonio en segundo plano (`IsDaemon: true`) dentro de ningún chat.
- Los chats de Antigravity deben permanecer siempre libres de tareas continuas en segundo plano.
- Para validar cambios realizados en el código o en los dashboards:
  1. Ejecuta pruebas unitarias (`pytest` o `unittest`).
  2. Para comprobar el servidor web, realiza únicamente una petición puntual (`Invoke-WebRequest` o `curl`) a `http://127.0.0.1:8501` y termina de inmediato.
  3. No levantes nuevos procesos ni demonios permanentes; el servidor ya está activo en el sistema operativo y el usuario puede simplemente actualizar su navegador (`F5`).
