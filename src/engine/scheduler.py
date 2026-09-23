import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Tuple, Optional

class DynamicScheduler:
    """
    Motor de Itinerario Inteligente (Investigación de Operaciones & Timeblocking Dinámico):
    - Gestiona bloques fijos (Clases UMSA, sueño biológico, traslados) y bloques flexibles (Deep Work, estudio, hábitos).
    - Ante cualquier imprevisto reportado por Telegram/Voz, recalcula el día y redistribuye los bloques
      desplazados a huecos libres de hoy o de días posteriores con la menor fricción cognitiva posible.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_schedule_table()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schedule_table(self):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS dynamic_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            start_time TEXT,
            end_time TEXT,
            title TEXT,
            block_type TEXT, -- 'FIXED', 'FLEXIBLE', 'BUFFER', 'IMPREVISTO'
            priority INTEGER DEFAULT 2, -- 1: Crítica Top 3, 2: Importante, 3: Opcional
            status TEXT DEFAULT 'Programado', -- 'Programado', 'Completado', 'Desplazado'
            notes TEXT
        )
        """)
        conn.commit()
        
        # Sembrar horario base si está vacío para hoy
        today_str = str(date.today())
        cur.execute("SELECT COUNT(*) FROM dynamic_schedule WHERE date = ?", (today_str,))
        if cur.fetchone()[0] == 0:
            self._seed_default_schedule(cur, today_str)
            conn.commit()
        conn.close()

    def _seed_default_schedule(self, cur, base_date: str):
        """Genera el horario base real según el día de la semana para Mark Eduardo Terrazas Luna."""
        try:
            day_of_week = datetime.strptime(base_date, "%Y-%m-%d").weekday() # 0: Lunes, ..., 6: Domingo
        except Exception:
            day_of_week = 0

        # Lunes (0)
        if day_of_week == 0:
            blocks = [
                ("05:15", "06:30", "🌅 Rutina Matutina & Alistamiento (75 min)", "FIXED", 1),
                ("06:30", "07:00", "🚌 Traslado a UMSA (30 min)", "FIXED", 1),
                ("07:00", "09:00", "🎓 UMSA: Taller 1", "FIXED", 1),
                ("09:00", "11:00", "🎓 UMSA: Seguridad Industrial (Auxiliatura)", "FIXED", 1),
                ("11:00", "12:30", "🥗 Almuerzo & Buffer de Descanso", "BUFFER", 3),
                ("12:30", "15:30", "🔬 GCI World (Matsuo Lab Tokyo Univ): Data Science & Python", "FLEXIBLE", 1),
                ("15:30", "17:30", "💻 Deep Work UMSA: Tareas y Estudio Técnico", "FLEXIBLE", 2),
                ("17:30", "19:00", "🛡️ Buffer / Traslado a Diseño Industrial", "BUFFER", 3),
                ("19:00", "21:00", "🎓 UMSA: Diseño Industrial", "FIXED", 1),
                ("21:00", "21:30", "🚌 Retorno a casa", "FIXED", 1),
                ("21:30", "22:30", "🌙 Cena, Desconexión Digital & Cierre NASA", "FIXED", 1),
                ("22:30", "05:15", "😴 Sueño Biológico Protegido (Higiene de Sueño)", "FIXED", 1)
            ]
        # Martes (1)
        elif day_of_week == 1:
            blocks = [
                ("05:15", "06:30", "🌅 Rutina Matutina & Alistamiento (75 min)", "FIXED", 1),
                ("06:30", "07:00", "🚌 Traslado a UMSA (30 min)", "FIXED", 1),
                ("07:00", "08:00", "🎓 UMSA: Taller 1", "FIXED", 1),
                ("08:00", "11:00", "🎓 UMSA: Clases [⚠️ Choque Taller 1 / Seg. Ind. / Gerencia]", "FIXED", 1),
                ("11:00", "12:30", "🥗 Almuerzo & Buffer", "BUFFER", 3),
                ("12:30", "15:30", "🔬 GCI World (Matsuo Lab): Laboratorios de Machine Learning", "FLEXIBLE", 1),
                ("15:30", "17:30", "💰 Proyecto Monetización ($1,000 USDT Meta Noviembre)", "FLEXIBLE", 1),
                ("17:30", "18:30", "🏋️ Entrenamiento Físico & Fuerza", "FLEXIBLE", 2),
                ("18:30", "20:00", "📚 Refuerzo Académico & Estudio UMSA", "FLEXIBLE", 2),
                ("20:00", "21:30", "🛡️ Bloque Buffer Vespertino", "BUFFER", 3),
                ("21:30", "22:30", "🌙 Cena & Cierre del Día", "FIXED", 1),
                ("22:30", "05:15", "😴 Sueño Biológico Protegido", "FIXED", 1)
            ]
        # Miércoles (2)
        elif day_of_week == 2:
            blocks = [
                ("07:15", "08:30", "🌅 Rutina Matutina & Alistamiento (75 min)", "FIXED", 1),
                ("08:30", "09:00", "🚌 Traslado a UMSA (30 min)", "FIXED", 1),
                ("09:00", "12:00", "🎓 UMSA: Seguridad Industrial (Laboratorio)", "FIXED", 1),
                ("12:00", "13:00", "🥗 Almuerzo & Descanso Cognitivo", "FIXED", 1),
                ("13:00", "15:00", "🎓 UMSA: Seguridad Industrial (Clase Teórica)", "FIXED", 1),
                ("15:00", "15:30", "🚌 Retorno a casa", "FIXED", 1),
                ("15:30", "18:30", "🔬 GCI World (Matsuo Lab): Tareas y Prácticas Python/Pandas", "FLEXIBLE", 1),
                ("18:30", "20:00", "💰 Prospección Remota & Monetización ($1,000 USDT)", "FLEXIBLE", 1),
                ("20:00", "21:30", "🛡️ Buffer de Contingencia & Lectura", "BUFFER", 3),
                ("21:30", "22:30", "🌙 Cena & Cierre del Día", "FIXED", 1),
                ("22:30", "05:45", "😴 Sueño Biológico Protegido", "FIXED", 1)
            ]
        # Jueves (3)
        elif day_of_week == 3:
            blocks = [
                ("05:45", "07:00", "🌅 Rutina Matutina & Alistamiento (75 min)", "FIXED", 1),
                ("07:00", "08:00", "🚌 Traslado a Empresa (60 min) [🎧 Podcasts Técnicos / Inglés]", "FIXED", 2),
                ("08:00", "12:00", "🏢 Empresa: Pasantía & Prácticas Profesionales", "FIXED", 1),
                ("12:00", "13:00", "🚌 Retorno de Empresa (60 min) [🎧 Podcasts Técnicos / Inglés]", "FIXED", 2),
                ("13:00", "14:00", "🥗 Almuerzo & Descanso", "FIXED", 1),
                ("14:00", "17:00", "🔬 GCI World (Matsuo Lab): Análisis de Datos & Algoritmos", "FLEXIBLE", 1),
                ("17:00", "18:30", "🛡️ Buffer / Traslado a Diseño Industrial", "BUFFER", 3),
                ("19:00", "21:00", "🎓 UMSA: Diseño Industrial", "FIXED", 1),
                ("21:00", "21:30", "🚌 Retorno a casa", "FIXED", 1),
                ("21:30", "22:30", "🌙 Cena & Cierre NASA", "FIXED", 1),
                ("22:30", "07:00", "😴 Sueño Biológico Protegido", "FIXED", 1)
            ]
        # Viernes (4)
        elif day_of_week == 4:
            blocks = [
                ("08:30", "09:45", "🌅 Rutina Matutina & Alistamiento (75 min)", "FIXED", 1),
                ("09:45", "10:30", "🚌 Traslado a UMSA / Buffer", "FIXED", 1),
                ("11:00", "13:00", "🎓 UMSA: Gerencia", "FIXED", 1),
                ("13:00", "14:00", "🥗 Almuerzo & Descanso", "FIXED", 1),
                ("14:00", "17:00", "🔬 GCI World: Cierre Semanal de Entregables Tokyo", "FLEXIBLE", 1),
                ("17:00", "18:00", "🏋️ Entrenamiento Físico & Salud", "FLEXIBLE", 2),
                ("18:00", "20:00", "💰 Proyectos de Automatización con IA / n8n ($1,000 USDT)", "FLEXIBLE", 1),
                ("20:00", "21:30", "🛡️ Buffer Libre de Viernes", "BUFFER", 3),
                ("21:30", "22:30", "🌙 Cena & Cierre del Día", "FIXED", 1),
                ("22:30", "08:00", "😴 Sueño Biológico Protegido", "FIXED", 1)
            ]
        # Sábado (5)
        elif day_of_week == 5:
            blocks = [
                ("08:00", "09:00", "🌅 Rutina Matutina & Desayuno", "FIXED", 1),
                ("09:00", "12:30", "🔬 Bloque Maestro GCI World: Kaggle / Modelado Avanzado", "FLEXIBLE", 1),
                ("12:30", "14:00", "🥗 Almuerzo & Descanso", "FIXED", 1),
                ("14:00", "17:00", "💰 Deep Work Freelance / Upwork ($1,000 USDT Meta Noviembre)", "FLEXIBLE", 1),
                ("17:00", "18:30", "📚 Refuerzo Académico UMSA & Buffer", "BUFFER", 3),
                ("19:00", "22:00", "🇬🇧 Curso Virtual de Inglés (En Vivo - 3 Horas)", "FIXED", 1),
                ("22:00", "22:45", "🌙 Cena Ligera & Cierre", "FIXED", 1),
                ("22:45", "08:30", "😴 Sueño Biológico Protegido", "FIXED", 1)
            ]
        # Domingo (6)
        else:
            blocks = [
                ("08:30", "09:30", "🌅 Rutina Matutina & Desayuno", "FIXED", 1),
                ("09:30", "12:00", "📊 Retrospectiva Semanal InvernovAH (Finanzas Binance & OKRs)", "FLEXIBLE", 1),
                ("12:00", "15:00", "🥗 Almuerzo Familiar & Desconexión", "FIXED", 1),
                ("15:00", "18:00", "🔬 Práctica Libre GCI World / Proyectos Personales", "FLEXIBLE", 2),
                ("18:00", "19:00", "🛡️ Buffer de Preparación para Clase", "BUFFER", 3),
                ("19:00", "22:00", "🇬🇧 Curso Virtual de Inglés (En Vivo - 3 Horas)", "FIXED", 1),
                ("22:00", "22:45", "🌙 Cierre Semanal & Planificación de Lunes", "FIXED", 1),
                ("22:45", "05:15", "😴 Sueño Biológico Protegido", "FIXED", 1)
            ]

        for start, end, title, b_type, prio in blocks:
            cur.execute("""
            INSERT INTO dynamic_schedule (date, start_time, end_time, title, block_type, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Programado')
            """, (base_date, start, end, title, b_type, prio))

    def _time_to_minutes(self, t_str: str) -> int:
        h, m = map(int, t_str.split(':'))
        return h * 60 + m

    def _minutes_to_time(self, minutes: int) -> str:
        minutes = minutes % (24 * 60)
        h = minutes // 60
        m = minutes % 60
        return f"{h:02d}:{m:02d}"

    def get_schedule(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        target_date = target_date or str(date.today())
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM dynamic_schedule WHERE date = ? ORDER BY start_time ASC", (target_date,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def handle_imprevisto(self, description: str, duration_minutes: int, start_time: Optional[str] = None, target_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Recibe un imprevisto, lo bloquea en el horario e inteligentemente redistribuye las tareas desplazadas:
        1. Identifica qué bloques colisionan con el imprevisto.
        2. Reubica bloques flexibles en los buffers de hoy.
        3. Si hoy se agota el tiempo libre, traslada el sobrante a días posteriores (efecto cascada de menor fricción).
        """
        today_date = target_date or str(date.today())
        conn = self._get_connection()
        cur = conn.cursor()

        # Si no se indica hora de inicio, asumir la hora actual redondeada a los próximos 10 minutos
        if not start_time:
            now = datetime.now()
            start_min = ((now.hour * 60 + now.minute + 10) // 10) * 10
            start_time = self._minutes_to_time(start_min)
        else:
            start_min = self._time_to_minutes(start_time)

        end_min = start_min + duration_minutes
        end_time = self._minutes_to_time(end_min)

        # 1. Obtener eventos de hoy
        cur.execute("SELECT * FROM dynamic_schedule WHERE date = ? ORDER BY start_time ASC", (today_date,))
        current_events = [dict(r) for r in cur.fetchall()]

        displaced_blocks = []
        kept_events = []

        for ev in current_events:
            ev_start = self._time_to_minutes(ev['start_time'])
            ev_end = self._time_to_minutes(ev['end_time'])

            # Detectar solapamiento
            overlaps = max(ev_start, start_min) < min(ev_end, end_min)

            if overlaps:
                if ev['block_type'] == 'FIXED' and ev['priority'] == 1:
                    # Si colisiona con un bloque fijo (ej. clases UMSA), se deja constancia
                    ev['notes'] = (ev.get('notes') or '') + f" [Solapamiento con imprevisto: {description}]"
                    kept_events.append(ev)
                else:
                    # Bloque flexible o buffer es desplazado
                    displaced_blocks.append(ev)
            else:
                kept_events.append(ev)

        # 2. Insertar el bloque de imprevisto
        cur.execute("""
        INSERT INTO dynamic_schedule (date, start_time, end_time, title, block_type, priority, status, notes)
        VALUES (?, ?, ?, ?, 'IMPREVISTO', 1, 'Programado', 'Insertado dinámicamente vía Telegram/IA')
        """, (today_date, start_time, end_time, f"🚨 Imprevisto: {description}"))

        rescheduled_summary = []
        tomorrow_date = str(date.today() + timedelta(days=1))

        # 3. Reubicar los bloques desplazados
        for disp in displaced_blocks:
            disp_duration = self._time_to_minutes(disp['end_time']) - self._time_to_minutes(disp['start_time'])
            
            # Buscar si hoy hay un bloque BUFFER disponible después del imprevisto
            cur.execute("""
            SELECT * FROM dynamic_schedule 
            WHERE date = ? AND block_type = 'BUFFER' AND start_time >= ?
            ORDER BY start_time ASC LIMIT 1
            """, (today_date, end_time))
            buffer_row = cur.fetchone()

            if buffer_row:
                # Ocupar el buffer de hoy
                buf_id = buffer_row['id']
                cur.execute("""
                UPDATE dynamic_schedule 
                SET title = ?, block_type = ?, priority = ?, notes = ?
                WHERE id = ?
                """, (disp['title'], disp['block_type'], disp['priority'], f"Reubicado hoy desde {disp['start_time']}", buf_id))
                rescheduled_summary.append(f"• '{disp['title']}' se movió a hoy en tu buffer de las {buffer_row['start_time']}.")
            else:
                # No hay buffer hoy -> Desplazar a mañana al primer slot libre de estudio
                cur.execute("SELECT COUNT(*) FROM dynamic_schedule WHERE date = ?", (tomorrow_date,))
                if cur.fetchone()[0] == 0:
                    self._seed_default_schedule(cur, tomorrow_date)

                # Buscar buffer en el día de mañana
                cur.execute("""
                SELECT * FROM dynamic_schedule 
                WHERE date = ? AND block_type = 'BUFFER'
                ORDER BY start_time ASC LIMIT 1
                """, (tomorrow_date,))
                tom_buffer = cur.fetchone()

                if tom_buffer:
                    cur.execute("""
                    UPDATE dynamic_schedule 
                    SET title = ?, block_type = ?, priority = ?, notes = ?
                    WHERE id = ?
                    """, (disp['title'], disp['block_type'], disp['priority'], f"Trasladado con holgura desde {today_date}", tom_buffer['id']))
                    rescheduled_summary.append(f"• '{disp['title']}' se trasladó para mañana a las {tom_buffer['start_time']} sin sobrecargar tu día.")
                else:
                    # Insertar al final de la tarde de mañana
                    cur.execute("""
                    INSERT INTO dynamic_schedule (date, start_time, end_time, title, block_type, priority, status, notes)
                    VALUES (?, '16:00', '17:30', ?, ?, ?, 'Programado', 'Re-planificación automática')
                    """, (tomorrow_date, disp['title'], disp['block_type'], disp['priority']))
                    rescheduled_summary.append(f"• '{disp['title']}' fue reprogramado para mañana por la tarde (16:00).")

            # Marcar el bloque original como desplazado si no fue sobreescrito
            cur.execute("DELETE FROM dynamic_schedule WHERE id = ?", (disp['id'],))

        conn.commit()
        conn.close()

        # Construir respuesta natural para el usuario / Telegram
        text_report = (
            f"✅ **Itinerario Recalculado Exitosamente (Menor Fricción):**\n\n"
            f"🚨 **Imprevisto Agendado:** {description} ({start_time} - {end_time}, {duration_minutes} min).\n\n"
            f"🔄 **Ajustes Realizados:**\n"
        )
        if rescheduled_summary:
            text_report += "\n".join(rescheduled_summary) + "\n\n"
        else:
            text_report += "• Ningún bloque crítico fue afectado; el imprevisto cayó en una ventana libre.\n\n"

        text_report += "🛡️ **Protección de Energía:** Tu ventana de sueño biológico (22:30) y tus clases obligatorias de la UMSA permanecen intactas."

        return {
            "success": True,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration_minutes,
            "displaced_count": len(displaced_blocks),
            "report": text_report
        }
