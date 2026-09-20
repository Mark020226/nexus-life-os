import unittest
import sqlite3
import os
import sys

# Add src to path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from src.database.dedup_engine import analyze_against_db, format_mixed_markdown, normalize_url, detect_resources_in_text

class TestDeduplicationEngine(unittest.TestCase):
    def setUp(self):
        # Create in-memory database for testing
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        
        self.cur.execute("""
        CREATE TABLE resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            summary TEXT,
            category TEXT,
            date_added TEXT,
            source TEXT,
            author TEXT,
            status TEXT DEFAULT 'Pendiente',
            notes TEXT,
            direct_url TEXT,
            post_url TEXT,
            direct_url_clean TEXT,
            canonical_key TEXT,
            canonical_name TEXT,
            found_by_ai INTEGER DEFAULT 0,
            ai_what_it_does TEXT,
            ai_how_it_helps TEXT,
            employability_index INTEGER DEFAULT 70,
            employability_details TEXT,
            has_certification TEXT,
            recruiter_weight TEXT,
            bolivia_eligible TEXT,
            bolivia_details TEXT,
            is_duplicate INTEGER DEFAULT 0,
            duplicate_count INTEGER DEFAULT 1,
            duplicate_sources TEXT,
            date_published TEXT,
            date_saved TEXT,
            has_mixed_resources INTEGER DEFAULT 0,
            new_resources_list TEXT,
            repeated_resources_list TEXT
        )
        """)
        
        # Seed test data
        # Row 1: Harvard CS50
        self.cur.execute("""
        INSERT INTO resources (id, url, direct_url_clean, canonical_key, title, summary)
        VALUES (1, 'https://instagram.com/reel/1', 'https://cs50.harvard.edu/x/', 'harvard-cs50',
                'Harvard CS50x Curso Gratuito', 'Aprende programación desde cero con CS50')
        """)
        
        # Row 2: NVIDIA DLI
        self.cur.execute("""
        INSERT INTO resources (id, url, direct_url_clean, canonical_key, title, summary)
        VALUES (2, 'https://instagram.com/reel/2', 'https://learn.nvidia.com', 'nvidia-dli',
                'NVIDIA Deep Learning Institute', 'Certificación oficial de IA de NVIDIA')
        """)
        
        # Row 3: Direct external URL
        self.cur.execute("""
        INSERT INTO resources (id, url, direct_url_clean, canonical_key, title, summary)
        VALUES (3, 'https://github.com/anthropics/skills/tree/main/skills/mcp-builder',
                'https://github.com/anthropics/skills/tree/main/skills/mcp-builder', 'mcp-builder',
                'Anthropic MCP Builder', 'Servidores MCP locales')
        """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_single_resource_duplicate_detected(self):
        """Test that a post talking ONLY about CS50 is detected as PURE_DUPLICATE."""
        post_text = "Comenta CS50 y te mando el curso completo de Harvard CS50 para aprender a programar"
        post_url = "https://instagram.com/reel/new_cs50"
        analysis = analyze_against_db(self.cur, post_text, post_url)
        
        self.assertEqual(analysis["status"], "PURE_DUPLICATE")
        self.assertEqual(analysis["primary_id"], 1)
        self.assertIn("Harvard CS50", analysis["reason"])

    def test_multi_resource_all_repeated_detected(self):
        """Test that a post covering both CS50 and NVIDIA (both already in DB) is detected as PURE_DUPLICATE."""
        post_text = "Top 2 certificaciones que necesitas: Harvard CS50 y NVIDIA Deep Learning Institute"
        post_url = "https://instagram.com/reel/new_multi_rep"
        analysis = analyze_against_db(self.cur, post_text, post_url)
        
        self.assertEqual(analysis["status"], "PURE_DUPLICATE")
        self.assertEqual(len(analysis["new_resources"]), 0)
        self.assertEqual(len(analysis["repeated_resources"]), 2)

    def test_multi_resource_mixed_detected(self):
        """Test that a post covering CS50 (repeated) AND n8n (new) is classified as MIXED."""
        post_text = "Las 2 herramientas para estudiantes: Harvard CS50 para programar y n8n para automatizar flujos"
        post_url = "https://instagram.com/reel/new_mixed"
        analysis = analyze_against_db(self.cur, post_text, post_url)
        
        self.assertEqual(analysis["status"], "MIXED")
        self.assertEqual(len(analysis["new_resources"]), 1)
        self.assertEqual(analysis["new_resources"][0]["canonical_id"], "n8n_automation")
        self.assertEqual(len(analysis["repeated_resources"]), 1)
        self.assertEqual(analysis["repeated_resources"][0]["canonical_id"], "harvard_cs50")
        
        # Test markdown formatting
        new_md, rep_md = format_mixed_markdown(analysis["new_resources"], analysis["repeated_resources"])
        self.assertIn("n8n Workflow Automation", new_md)
        self.assertIn("🟢", new_md)
        self.assertIn("Harvard CS50", rep_md)
        self.assertIn("⚠️", rep_md)
        self.assertIn("#1", rep_md)

    def test_single_new_resource(self):
        """Test that a brand new resource is classified as NEW."""
        post_text = "Aprende modelos locales con Ollama en tu computadora"
        post_url = "https://instagram.com/reel/new_ollama"
        analysis = analyze_against_db(self.cur, post_text, post_url)
        
        self.assertEqual(analysis["status"], "NEW")
        self.assertEqual(len(analysis["new_resources"]), 1)
        self.assertEqual(len(analysis["repeated_resources"]), 0)

    def test_exact_direct_url_duplicate(self):
        """Test that submitting an identical direct URL is rejected as PURE_DUPLICATE."""
        post_text = "Nueva herramienta de agentes"
        post_url = "https://github.com/anthropics/skills/tree/main/skills/mcp-builder"
        analysis = analyze_against_db(self.cur, post_text, post_url, direct_url=post_url)
        
        self.assertEqual(analysis["status"], "PURE_DUPLICATE")
        self.assertEqual(analysis["primary_id"], 3)

    def test_url_normalization(self):
        """Test that URL normalization strips trailing slashes, fragments, and params."""
        url1 = "https://cs50.harvard.edu/x/"
        url2 = "https://cs50.harvard.edu/x"
        url3 = "https://cs50.harvard.edu/x?utm_source=instagram&ref=reel"
        self.assertEqual(normalize_url(url1), "https://cs50.harvard.edu/x")
        self.assertEqual(normalize_url(url2), "https://cs50.harvard.edu/x")

if __name__ == "__main__":
    unittest.main()
