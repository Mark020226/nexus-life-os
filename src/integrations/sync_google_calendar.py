import os
import sys
import json
from datetime import datetime, date, timedelta
from typing import Optional

def get_project_root():
    if "NEXUS_ROOT" in os.environ and os.path.exists(os.environ["NEXUS_ROOT"]):
        return os.path.abspath(os.environ["NEXUS_ROOT"])
    cur = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    for _ in range(5):
        if os.path.exists(os.path.join(cur, "requirements.txt")) and (
            os.path.exists(os.path.join(cur, "src")) or os.path.exists(os.path.join(cur, "data"))
        ):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return cur

ROOT_DIR = get_project_root()
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.engine.scheduler import DynamicScheduler

CREDENTIALS_PATH = os.path.expanduser("~/.google_workspace_mcp/credentials/mark23terrazas30@gmail.com.json")
TIMEZONE = "America/La_Paz"

def get_calendar_service():
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(f"No se encontró el archivo de credenciales en {CREDENTIALS_PATH}")
    
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    
    with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    creds = Credentials.from_authorized_user_info(data)
    service = build("calendar", "v3", credentials=creds)
    return service

def sync_schedule_to_primary_calendar(days_ahead: int = 7, db_path: Optional[str] = None):
    """
    Sincroniza el horario dinámico de NEXUS Life OS directamente en el Calendario Principal de Mark.
    - Crea o actualiza cada bloque con su alarma de 10 min.
    - Usa códigos de color para distinguir clases UMSA, GCI World Tokyo, Empresa, Inglés y descanso.
    - Evita duplicar eventos existentes mediante el identificador [NEXUS-LIFE-OS].
    """
    if db_path is None:
        db_path = os.path.join(ROOT_DIR, "data", "nexus.db")
        
    scheduler = DynamicScheduler(db_path)
    service = get_calendar_service()
    today = date.today()
    
    print(f"=== INICIANDO SINCRONIZACIÓN CON GOOGLE CALENDAR (mark23terrazas30@gmail.com) ===")
    print(f"Zona Horaria: {TIMEZONE} | Días a proyectar: {days_ahead}")

    # Mapeo de colores de Google Calendar:
    # 9: Blueberry (Azul), 10: Basil (Verde), 11: Tomato (Rojo), 8: Graphite (Gris), 5: Banana (Amarillo), 6: Tangerine (Naranja)
    def get_color_id(title: str, block_type: str) -> str:
        t_low = title.lower()
        if "umsa" in t_low or "clase" in t_low or "taller" in t_low or "seguridad" in t_low or "gerencia" in t_low or "diseño" in t_low:
            return "9" # Blueberry (Académico UMSA)
        if "gci world" in t_low:
            return "3" # Grape / Púrpura (GCI World Tokio)
        if "empresa" in t_low:
            return "6" # Tangerine (Empresa)
        if "inglés" in t_low or "ingles" in t_low:
            return "7" # Peacock (Inglés en vivo)
        if "monetización" in t_low or "freelance" in t_low or "1,000 usdt" in t_low or "n8n" in t_low:
            return "10" # Basil (Verde - Ingresos/Finanzas)
        if "sueño" in t_low or "rutina" in t_low:
            return "8" # Graphite (Descanso/Rutina)
        if "imprevisto" in t_low:
            return "11" # Tomato (Alerta / Imprevisto)
        if block_type == "BUFFER":
            return "5" # Banana (Buffer)
        return "1"

    total_created = 0
    total_existing = 0

    for day_offset in range(days_ahead):
        target_date = today + timedelta(days=day_offset)
        target_date_str = str(target_date)
        blocks = scheduler.get_schedule(target_date_str)
        
        # Obtener eventos existentes de ese día en Google Calendar con tag [NEXUS-LIFE-OS]
        time_min = f"{target_date_str}T00:00:00-04:00"
        time_max = f"{target_date_str}T23:59:59-04:00"
        
        events_result = service.events().list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        existing_nexus_events = {}
        for ev in events_result.get("items", []):
            desc = ev.get("description", "")
            if "[NEXUS-LIFE-OS]" in desc or ev.get("summary", "").startswith(("🎓", "🔬", "🏢", "🇬🇧", "💰", "🌅", "😴", "🛡️", "🚨")):
                existing_nexus_events[ev.get("summary")] = ev.get("id")

        print(f"\n📅 Procesando {target_date_str} ({len(blocks)} bloques planificados)...")

        for b in blocks:
            title = b["title"]
            s_time = b["start_time"]
            e_time = b["end_time"]
            b_type = b.get("block_type", "FLEXIBLE")
            prio = b.get("priority", 2)
            
            # Construir start / end RFC3339
            start_rfc = f"{target_date_str}T{s_time}:00"
            end_rfc = f"{target_date_str}T{e_time}:00"
            
            # Manejar trasnoche si termina pasada la medianoche
            if e_time < s_time:
                next_day = str(target_date + timedelta(days=1))
                end_rfc = f"{next_day}T{e_time}:00"

            prio_label = "🔥 Alta Prioridad (Inamovible)" if prio == 1 else ("⚡ Flexible" if prio == 2 else "🛡️ Buffer / Amortiguador")
            
            description_text = (
                f"Bloque de NEXUS Life OS\n\n"
                f"🎯 Prioridad: {prio_label}\n"
                f"📁 Tipo: {b_type}\n"
                f"💡 Metodología: Álvaro Hernández (InvernovAH) - Cero Fricción Cognitiva\n"
                f"[NEXUS-LIFE-OS]"
            )
            
            color_id = get_color_id(title, b_type)
            
            event_body = {
                "summary": title,
                "description": description_text,
                "start": {
                    "dateTime": f"{start_rfc}-04:00",
                    "timeZone": TIMEZONE
                },
                "end": {
                    "dateTime": f"{end_rfc}-04:00",
                    "timeZone": TIMEZONE
                },
                "colorId": color_id,
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": 10}
                    ]
                }
            }

            if title in existing_nexus_events:
                # Actualizar evento existente
                ev_id = existing_nexus_events[title]
                service.events().update(calendarId="primary", eventId=ev_id, body=event_body).execute()
                total_existing += 1
            else:
                # Crear nuevo evento
                service.events().insert(calendarId="primary", body=event_body).execute()
                total_created += 1

    print(f"\n✅ Sincronización completada exitosamente:")
    print(f"   • Eventos nuevos creados: {total_created}")
    print(f"   • Eventos existentes verificados/actualizados: {total_existing}")
    print(f"   • Todos los eventos cuentan con notificación emergente 10 minutos antes.")

if __name__ == "__main__":
    sync_schedule_to_primary_calendar(days_ahead=7)
