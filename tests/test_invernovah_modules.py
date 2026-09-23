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

if __name__ == '__main__':
    unittest.main()
