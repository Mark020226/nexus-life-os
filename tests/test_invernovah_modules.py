import unittest
import sqlite3
import os
import tempfile
from src.ai.video_analyzer import clean_direct_url, analyze_url
from src.database.cloud_sync import export_db_to_json

class TestInvernovahModules(unittest.TestCase):
    
    def test_clean_direct_url_strips_tracking(self):
        dirty = "https://www.coursera.org/learn/algorithms-part-1?utm_source=ig&utm_medium=social&igshid=xyz123"
        clean = clean_direct_url(dirty)
        self.assertEqual(clean, "https://www.coursera.org/learn/algorithms-part-1")

    def test_video_analyzer_heuristics(self):
        res = analyze_url("https://cs50.harvard.edu/x/2024/", custom_prompt="¿Sirve para conseguir empleo tech?")
        self.assertIn("harvard", (res["title"] + res["summary"]).lower())
        self.assertGreaterEqual(res["employability_index"], 85)
        self.assertEqual(res["category"], "Cursos & Certificaciones")
        self.assertIn("personalizada", res["user_custom_analysis"].lower())

    def test_add_and_delete_resource_lifecycle(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
            
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT,
            user_custom_analysis TEXT
        )
        """)
        
        # Insert
        cur.execute("INSERT INTO resources (url, title, user_custom_analysis) VALUES (?, ?, ?)",
                    ("https://n8n.io", "n8n Workflow Automation", "Excelente para Ing. Industrial"))
        conn.commit()
        res_id = cur.lastrowid
        
        cur.execute("SELECT COUNT(*) FROM resources")
        self.assertEqual(cur.fetchone()[0], 1)
        
        # Delete
        cur.execute("DELETE FROM resources WHERE id = ?", (res_id,))
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM resources")
        self.assertEqual(cur.fetchone()[0], 0)
        conn.close()
        
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_export_db_to_json(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as jf:
            json_path = jf.name
            
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE resources (id INTEGER, title TEXT)")
        cur.execute("INSERT INTO resources VALUES (1, 'Test Tool')")
        conn.commit()
        conn.close()
        
        success = export_db_to_json(db_path, json_path)
        self.assertTrue(success)
        self.assertTrue(os.path.getsize(json_path) > 10)
        
        if os.path.exists(db_path):
            os.remove(db_path)
        if os.path.exists(json_path):
            os.remove(json_path)

    def test_dynamic_scheduler_imprevisto(self):
        from src.engine.scheduler import DynamicScheduler
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
            
        sched = DynamicScheduler(db_path)
        initial_items = sched.get_schedule()
        self.assertGreater(len(initial_items), 5)
        
        # Simular imprevisto de 90 min a las 15:30
        res = sched.handle_imprevisto("Reunión imprevista UMSA", 90, "15:30")
        self.assertTrue(res["success"])
        self.assertIn("Itinerario Recalculado", res["report"])
        
        # Verificar que el imprevisto está agendado
        updated = sched.get_schedule()
        titles = [x["title"] for x in updated]
        self.assertTrue(any("Reunión imprevista UMSA" in t for t in titles))
        
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_telegram_assistant_intents(self):
        from src.integrations.telegram_bot import TelegramNEXUSAssistant
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
            
        # Inicializar tabla de finanzas y dynamic schedule
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS finance_transactions (id INTEGER PRIMARY KEY, date TEXT, type TEXT, category TEXT, amount REAL, description TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS daily_metrics (date TEXT PRIMARY KEY, sleep_hours REAL, energy_level INTEGER, mood INTEGER, productive_hours REAL, notes TEXT)")
        conn.commit()
        conn.close()
        
        assistant = TelegramNEXUSAssistant(db_path)
        
        # 1. Finanzas
        resp_fin = assistant.process_message("Gasté 45 Bs en fotocopias de ingeniería")
        self.assertIn("Transacción Registrada", resp_fin)
        
        # 2. Hábitos
        resp_hab = assistant.process_message("Dormí 8 horas y mi energía es 9")
        self.assertIn("Check-in Registrado", resp_hab)
        
        # 3. Consulta de itinerario
        resp_sch = assistant.process_message("¿Cuál es mi itinerario de hoy?")
        self.assertIn("Tu Itinerario Dinámico", resp_sch)
        
        if os.path.exists(db_path):
            os.remove(db_path)

if __name__ == '__main__':
    unittest.main()
