import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

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

from src.engine.scheduler import DynamicScheduler

def generate_ics_content(db_path: Optional[str] = None, days_ahead: int = 14) -> str:
    """
    Genera un archivo iCalendar (.ics) RFC 5545 para suscripción directa en Google Calendar / Apple Calendar.
    Proyecta el itinerario dinámico de NEXUS Life OS para los próximos días con alarmas de 10 min.
    """
    if db_path is None:
        db_path = os.path.join(ROOT_DIR, "data", "nexus.db")
    
    scheduler = DynamicScheduler(db_path)
    today = date.today()
    
    # Header RFC 5545
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//NEXUS Life OS//InvernovAH Engineering//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:NEXUS Life OS - Mark E. Terrazas",
        "X-WR-TIMEZONE:America/La_Paz",
        "X-WR-CALDESC:Itinerario Dinámico Adaptativo (UMSA + GCI World Tokyo + Empresa + Inglés + Monetización $1,000 USDT)"
    ]
    
    # Categorías e íconos para descripción
    priority_map = {
        1: "🔥 ALTA PRIORIDAD (Inamovible)",
        2: "⚡ MEDIA (Flexible con amortiguamiento)",
        3: "🌱 BAJA / BUFFER (Ajustable ante imprevistos)"
    }

    now_stamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")

    for day_offset in range(days_ahead):
        target_date = today + timedelta(days=day_offset)
        target_date_str = target_date.strftime("%Y-%m-%d")
        
        # Obtener los bloques correspondientes para ese día
        blocks = scheduler.get_schedule(target_date_str)
        date_str = target_date.strftime("%Y%m%d")

        for idx, block in enumerate(blocks):
            s_h, s_m = map(int, block["start_time"].split(":"))
            e_h, e_m = map(int, block["end_time"].split(":"))
            
            # Formato local YYYYMMDDTHHMMSS (Google Calendar lo interpreta con la zona horaria del calendario)
            dtstart = f"{date_str}T{s_h:02d}{s_m:02d}00"
            dtend = f"{date_str}T{e_h:02d}{e_m:02d}00"
            
            uid = f"nexus-{target_date}-{idx}-{s_h}{s_m}@nexuslifeos.cloud"
            
            title = block["title"].replace(",", "\\,").replace(";", "\\;")
            desc = (
                f"Bloque: {block['title']}\\n"
                f"Prioridad: {priority_map.get(block.get('priority', 2), 'Normal')}\\n"
                f"Categoría: {block.get('category', 'General')}\\n"
                f"Metodología: Álvaro Hernández (InvernovAH) - Cero Fricción Cognitiva"
            )

            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{now_stamp}",
                f"DTSTART:{dtstart}",
                f"DTEND:{dtend}",
                f"SUMMARY:{title}",
                f"DESCRIPTION:{desc}",
                f"CATEGORIES:{block.get('category', 'NEXUS')}",
                "STATUS:CONFIRMED",
                # Alarma 10 minutos antes
                "BEGIN:VALARM",
                "TRIGGER:-PT10M",
                "ACTION:DISPLAY",
                f"DESCRIPTION:Próximo bloque en 10 min: {title}",
                "END:VALARM",
                "END:VEVENT"
            ])
            
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)

def export_calendar_ics(output_path: Optional[str] = None, db_path: Optional[str] = None) -> str:
    """Genera y guarda el archivo .ics en el disco."""
    if output_path is None:
        output_path = os.path.join(ROOT_DIR, "data", "nexus_schedule.ics")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    content = generate_ics_content(db_path)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return output_path

if __name__ == "__main__":
    out = export_calendar_ics()
    print(f"Calendario .ics exportado exitosamente en: {out}")
