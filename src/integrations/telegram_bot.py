import os
import re
import json
import urllib.parse
from datetime import datetime, date
from typing import Dict, Any, Optional

from src.engine.scheduler import DynamicScheduler
from src.ai.video_analyzer import analyze_url
from src.database.cloud_sync import export_db_to_json

class TelegramNEXUSAssistant:
    """
    Asistente Central de Telegram para NEXUS Life OS:
    - Procesa lenguaje natural (texto o transcripciones de voz).
    - Detecta intenciones: Imprevistos de horario, captura de enlaces, finanzas, hábitos y consultas.
    - Ejecuta el recálculo dinámico con menor fricción y actualiza la base de datos en la nube.
    """

    def __init__(self, db_path: str, gemini_key: Optional[str] = None):
        self.db_path = db_path
        self.gemini_key = gemini_key
        self.scheduler = DynamicScheduler(db_path)

    def process_message(self, text: str, user_id: Optional[str] = None) -> str:
        """Punto de entrada principal: clasifica la intención y ejecuta la acción correspondiente."""
        clean_text = text.strip()
        lower_text = clean_text.lower()

        # 1. Detección de Enlaces (Ingesta de Recursos / Videos)
        url_match = re.search(r'https?://[^\s]+', clean_text)
        if url_match:
            found_url = url_match.group(0)
            return self._handle_link_ingest(found_url, clean_text)

        # 2. Detección de Imprevistos / Ajuste de Itinerario
        if any(w in lower_text for w in ["imprevisto", "surgio", "surgió", "ocupado", "actividad", "retraso", "tengo que salir", "cambio de horario", "recalcular"]):
            return self._handle_imprevisto_message(clean_text)

        # 3. Detección de Finanzas (Gastos / Ingresos)
        if any(w in lower_text for w in ["gasté", "gaste", "gasto", "compré", "compre", "pagué", "pague", "ingreso", "cobré", "cobre", "bs", "usd", "$"]):
            return self._handle_finance_message(clean_text)

        # 4. Detección de Hábitos y Energía (Check-in diario)
        if any(w in lower_text for w in ["dormí", "dormi", "sueño", "energia", "energía", "ánimo", "animo", "deep work"]):
            return self._handle_habits_message(clean_text)

        # 5. Consulta de Itinerario / Horario de Hoy
        if any(w in lower_text for w in ["itinerario", "horario", "plan de hoy", "qué tengo hoy", "que tengo hoy", "/hoy", "/itinerario"]):
            return self._handle_schedule_query()

        # 6. Fallback General / Asistente Socrático
        return self._handle_conversational_fallback(clean_text)

    def _handle_imprevisto_message(self, text: str) -> str:
        """Extrae duración, descripción y hora de inicio de un mensaje de imprevisto y recalcula el itinerario."""
        lower = text.lower()

        # Extraer duración en minutos
        duration_min = 60 # valor por defecto: 1 hora
        
        # Buscar patrones como "2 horas", "1.5 horas", "90 minutos", "45 min"
        min_match = re.search(r'(\d+)\s*(?:minutos|min|m\b)', lower)
        hour_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:horas|hora|h\b)', lower)

        if min_match:
            duration_min = int(min_match.group(1))
        elif hour_match:
            duration_min = int(float(hour_match.group(1)) * 60)

        # Extraer hora de inicio si se especificó (ej: "a las 15:30", "a las 4pm", "a las 16:00")
        start_time = None
        time_match = re.search(r'(?:a las|desde las|alas)?\s*(\d{1,2}):(\d{2})', lower)
        if time_match:
            h = int(time_match.group(1))
            m = int(time_match.group(2))
            start_time = f"{h:02d}:{m:02d}"
        else:
            time_h_match = re.search(r'(?:a las|desde las)\s*(\d{1,2})\s*(?:pm|am)?', lower)
            if time_h_match:
                h = int(time_h_match.group(1))
                if "pm" in lower and h < 12:
                    h += 12
                start_time = f"{h:02d}:00"

        # Extraer descripción limpia
        desc = text
        for p in ["surgió un imprevisto:", "surgió un imprevisto", "surgio un imprevisto", "surgió una actividad:", "surgió una actividad", "tengo"]:
            if p in lower:
                desc = text[lower.find(p) + len(p):].strip(" :,.")
                break
        if not desc or len(desc) < 3:
            desc = "Actividad Imprevista"

        # Ejecutar recálculo
        result = self.scheduler.handle_imprevisto(
            description=desc,
            duration_minutes=duration_min,
            start_time=start_time
        )
        return result['report']

    def _handle_link_ingest(self, url: str, full_text: str) -> str:
        """Procesa un enlace o video recibido por Telegram y devuelve la síntesis socrática de NEXUS v3."""
        # Extraer pregunta opcional si el usuario escribió algo más aparte del link
        user_q = full_text.replace(url, "").strip(" :,\n")
        
        ai_data = analyze_url(url, custom_prompt=user_q or None, gemini_api_key=self.gemini_key)
        
        # Guardar en SQLite
        import sqlite3
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cur = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        cur.execute("""
        INSERT INTO resources (
            url, direct_url, direct_url_clean, post_url, canonical_key, canonical_name,
            title, summary, ai_what_it_does, ai_how_it_helps, employability_index,
            employability_details, has_certification, recruiter_weight, bolivia_eligible,
            category, date_added, source, author, status, user_custom_analysis, found_by_ai
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Telegram Ingest', ?, 'Guardado', ?, 1)
        """, (
            ai_data["url"], ai_data["direct_url"], ai_data["direct_url_clean"],
            ai_data["post_url"], ai_data["canonical_key"], ai_data["canonical_name"],
            ai_data["title"], ai_data["summary"], ai_data["ai_what_it_does"],
            ai_data["ai_how_it_helps"], ai_data["employability_index"],
            ai_data["employability_details"], ai_data["has_certification"],
            ai_data["recruiter_weight"], ai_data["bolivia_eligible"],
            ai_data["category"], now_str, ai_data["author"],
            ai_data.get("user_custom_analysis", "")
        ))
        conn.commit()
        conn.close()

        # Diálogo socrático de NEXUS v3
        report = (
            f"📥 **Recurso Procesado & Catalogado en Segundo Cerebro:**\n\n"
            f"🎯 **{ai_data['title']}**\n"
            f"📁 **Categoría:** {ai_data['category']} | 🔥 **Empleabilidad:** {ai_data['employability_index']}%\n"
            f"🔗 **Acceso Directo Real:** {ai_data['direct_url']}\n\n"
            f"💡 **¿Qué es?:** {ai_data['ai_what_it_does']}\n"
            f"🚀 **Aporte Práctico:** {ai_data['ai_how_it_helps']}\n"
        )
        if ai_data.get("user_custom_analysis"):
            report += f"\n💬 **Tu Consulta:** {ai_data['user_custom_analysis']}\n"

        report += (
            f"\n🧠 **Integración Socrática a tu Vida:**\n"
            f"1️⃣ ¿Qué micro-acción concreta vas a ejecutar esta semana con esto?\n"
            f"2️⃣ ¿Deseas que bloquee una sesión de estudio de 45 min en tu Google Calendar para hoy en tu buffer?"
        )
        return report

    def _handle_finance_message(self, text: str) -> str:
        """Registra gastos o ingresos directamente desde Telegram."""
        # Extraer monto
        amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:bs|usd|\$|bolivianos)?', text.lower())
        amount = float(amount_match.group(1)) if amount_match else 25.0

        is_income = any(w in text.lower() for w in ["ingreso", "cobré", "cobre", "gané", "gane"])
        t_type = "Ingreso" if is_income else "Gasto"
        cat = "Ingresos Principales / Remoto" if is_income else "Gastos Personales"

        import sqlite3
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO finance_transactions (date, type, category, amount, description)
        VALUES (?, ?, ?, ?, ?)
        """, (str(date.today()), t_type, cat, amount, text))
        
        # Calcular tasa de ahorro acumulada
        cur.execute("SELECT type, SUM(amount) FROM finance_transactions GROUP BY type")
        sums = dict(cur.fetchall())
        conn.commit()
        conn.close()

        inc = sums.get("Ingreso", 0.0)
        sav = sums.get("Ahorro / Inversión", 0.0)
        rate = (sav / max(1.0, inc)) * 100.0 if inc > 0 else 0.0

        return (
            f"💰 **Transacción Registrada:** {t_type} de ${amount:.2f} ({text})\n"
            f"📊 **Tasa de Ahorro FIRE Actual:** {rate:.1f}% (Meta InvernovAH: > 40%)."
        )

    def _handle_habits_message(self, text: str) -> str:
        """Registra horas de sueño y energía desde un mensaje simple."""
        sleep_m = re.search(r'(\d+(?:\.\d+)?)\s*(?:horas|h)?\s*(?:de\s+sueño|dormí|dormi)', text.lower())
        energy_m = re.search(r'(?:energía|energia)\s*(?:de\s+|es\s+|:)?\s*(\d{1,2})', text.lower())

        sleep_val = float(sleep_m.group(1)) if sleep_m else 7.5
        energy_val = int(energy_m.group(1)) if energy_m else 8

        import sqlite3
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cur = conn.cursor()
        cur.execute("""
        INSERT OR REPLACE INTO daily_metrics (date, sleep_hours, energy_level, mood, productive_hours, notes)
        VALUES (?, ?, ?, ?, 4.5, ?)
        """, (str(date.today()), sleep_val, energy_val, energy_val, text))
        conn.commit()
        conn.close()

        return (
            f"⚡ **Check-in Registrado:** {sleep_val}h de sueño | Energía: {energy_val}/10.\n"
            f"📈 Gráfico de control de Shewhart actualizado en tu cockpit."
        )

    def _handle_schedule_query(self) -> str:
        """Devuelve el itinerario dinámico de hoy con el bloque actual resaltado."""
        items = self.scheduler.get_schedule()
        if not items:
            return "📅 No tienes bloques cargados para hoy. El sistema generará tu horario base matutino automáticamente."

        now = datetime.now()
        now_min = now.hour * 60 + now.minute

        lines = [f"📅 **Tu Itinerario Dinámico de Hoy ({date.today()}):**\n"]
        for item in items:
            s_min = self.scheduler._time_to_minutes(item['start_time'])
            e_min = self.scheduler._time_to_minutes(item['end_time'])
            
            is_current = s_min <= now_min < e_min
            tag = "👉 **[AHORA]** " if is_current else ""
            prio_badge = "🔥 " if item.get('priority') == 1 else ""
            lines.append(f"{tag}`{item['start_time']} - {item['end_time']}` {prio_badge}{item['title']}")

        return "\n".join(lines)

    def _handle_conversational_fallback(self, text: str) -> str:
        """Responde preguntas o solicitudes de productividad y estudio usando Gemini 3.6 Flash."""
        if not self.gemini_key:
            return (
                f"🤖 **NEXUS Assistant:** Recibí tu mensaje: *'{text}'*.\n\n"
                f"Puedes decirme cosas como:\n"
                f"• *'Surgió un imprevisto de 2 horas a las 15:00'* (recalculará tu día sin fricción).\n"
                f"• Enviar cualquier link de video o recurso (lo extraerá y clasificará).\n"
                f"• *'Gasté 45 Bs en libros'* (registrará finanzas).\n"
                f"• *'¿Cuál es mi plan de hoy?'* (te mostrará tu horario activo)."
            )

        import urllib.request
        import json

        system_instruction = (
            "Eres el Asistente y Copiloto de Inteligencia Artificial de 'NEXUS Life OS' para Mark Eduardo Terrazas Luna, "
            "estudiante de Ingeniería Industrial en la UMSA (La Paz, Bolivia), participante de GCI World Tokio 2026 y practicante de Empresa. "
            "Tu metodología se basa en Álvaro Hernández (InvernovAH): cero fricción, apalancamiento 80/20, rigor ingenieril y protección del descanso biológico. "
            "Si Mark te consulta sobre un examen, materia (Gerencia de Proyectos, Seguridad Industrial, Taller 1, Diseño Industrial, etc.) o plan de estudio, "
            "dale una guía estratégica magistral y directa para asegurar la máxima calificación (100 puntos): "
            "fórmulas clave indispensables (EVM, CPM/PERT, etc.), trampas conceptuales típicas, método de resolución paso a paso y cronograma de choque. "
            "Responde en español, con formato Markdown limpio y altamente legible en celular (viñetas, negritas, emojis estratégicos)."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_instruction}\n\nMensaje de Mark:\n{text}"}
                    ]
                }
            ]
        }

        models = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.6-flash"]
        last_error = ""

        for m in models:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.gemini_key}"
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
            except Exception as e:
                last_error = str(e)
                continue

        return f"🤖 **NEXUS Assistant:** Ocurrió un error consultando a la IA: {last_error}"

        return "🤖 No pude generar una respuesta en este momento. Inténtalo de nuevo."
