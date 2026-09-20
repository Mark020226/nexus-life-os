import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "nexus.db")
JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "instagram_resources.json")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Knowledge Base / Resources
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        title TEXT,
        summary TEXT,
        category TEXT,
        date_added TEXT,
        source TEXT,
        status TEXT DEFAULT 'Pendiente',
        notes TEXT
    )
    """)
    
    # 2. Daily Life Metrics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_metrics (
        date TEXT PRIMARY KEY,
        sleep_hours REAL,
        energy_level INTEGER,
        mood INTEGER,
        productive_hours REAL,
        notes TEXT
    )
    """)
    
    # 3. Academic UMSA Courses
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS academic_courses (
        code TEXT PRIMARY KEY,
        name TEXT,
        semester INTEGER,
        status TEXT DEFAULT 'Pendiente',
        grade REAL,
        prereq TEXT
    )
    """)
    
    # 4. Finance Transactions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS finance_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        type TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
    """)
    
    conn.commit()
    
    # Seed UMSA courses if empty
    cursor.execute("SELECT COUNT(*) FROM academic_courses")
    if cursor.fetchone()[0] == 0:
        seed_umsa_courses(cursor)
        conn.commit()
        
    # Seed Instagram resources if empty
    cursor.execute("SELECT COUNT(*) FROM resources")
    if cursor.fetchone()[0] == 0 and os.path.exists(JSON_PATH):
        seed_instagram_resources(cursor)
        conn.commit()
        
    conn.close()

def seed_umsa_courses(cursor):
    umsa_courses = [
        # Semestre 1
        ("MAT-100", "Álgebra", 1, "Aprobada", 0, "Pre-Facultativo"),
        ("IND-122", "Contabilidad", 1, "Aprobada", 0, "Pre-Facultativo"),
        ("MEC-101", "Dibujo Técnico", 1, "Aprobada", 0, "Pre-Facultativo"),
        ("FIS-100", "Física Básica I y Lab", 1, "Aprobada", 0, "Pre-Facultativo"),
        ("MAT-101", "Cálculo I", 1, "Aprobada", 0, "Pre-Facultativo"),
        ("QMC-101", "Química General e Inorgánica y Lab", 1, "Aprobada", 0, "Pre-Facultativo"),
        # Semestre 2
        ("MAT-103", "Álgebra Lineal y Teoría Matricial", 2, "Aprobada", 0, "MAT-100"),
        ("IND-222", "Teoría Económica", 2, "Aprobada", 0, "IND-122"),
        ("IND-225", "Ciencia de los Materiales", 2, "Aprobada", 0, "MEC-101"),
        ("FIS-102", "Física Básica II y Lab", 2, "Aprobada", 0, "FIS-100"),
        ("MAT-102", "Cálculo II", 2, "Aprobada", 0, "MAT-101"),
        ("QMC-200", "Química Orgánica y Lab", 2, "Aprobada", 0, "QMC-101"),
        # Semestre 3
        ("IND-311", "Cálculo de Probabilidades", 3, "Cursando", 0, "MAT-103"),
        ("IND-312", "Informática para Ingeniería y Lab", 3, "Cursando", 0, "MAT-103, IND-222"),
        ("IND-333", "Procesos de Manufactura", 3, "Cursando", 0, "IND-225"),
        ("ELT-322", "Electrotecnia, Electrónica y Lab", 3, "Cursando", 0, "FIS-102"),
        ("MAT-207", "Ecuaciones Diferenciales", 3, "Cursando", 0, "MAT-102"),
        ("QMC-206", "Fisicoquímica y Lab", 3, "Cursando", 0, "QMC-200"),
        # Semestre 4
        ("IND-411", "Estadística Inferencial", 4, "Pendiente", 0, "IND-311"),
        ("IND-412", "Metodología de la Inv. Científica", 4, "Pendiente", 0, "IND-312"),
        ("IND-413", "Ingeniería Ambiental y Des. Sostenible", 4, "Pendiente", 0, "IND-333"),
        ("IND-414", "Construcciones e Instalaciones Ind.", 4, "Pendiente", 0, "ELT-322"),
        ("IND-445", "Administración Industrial", 4, "Pendiente", 0, "IND-333"),
        ("IND-436", "Operaciones Unitarias I y Lab", 4, "Pendiente", 0, "QMC-206, MAT-207"),
        # Semestre 5
        ("IND-521", "Econometría", 5, "Pendiente", 0, "IND-411"),
        ("IND-532", "Control Estadístico de Calidad y Lab", 5, "Pendiente", 0, "IND-411"),
        ("IND-543", "Investigación de Operaciones I", 5, "Pendiente", 0, "IND-411, MAT-103"),
        ("IND-544", "Ingeniería de Costos", 5, "Pendiente", 0, "IND-445"),
        ("IND-535", "Ingeniería de Métodos y Lab", 5, "Pendiente", 0, "IND-445"),
        ("IND-536", "Operaciones Unitarias II y Lab", 5, "Pendiente", 0, "IND-436"),
        # Semestre 6
        ("IND-621", "Marketing", 6, "Pendiente", 0, "IND-521"),
        ("IND-642", "Ingeniería de Sistemas", 6, "Pendiente", 0, "IND-543"),
        ("IND-643", "Investigación de Operaciones II", 6, "Pendiente", 0, "IND-543"),
        ("IND-624", "Ingeniería Económica", 6, "Pendiente", 0, "IND-544"),
        ("IND-635", "Manufactura Esbelta y Lab", 6, "Pendiente", 0, "IND-535"),
        ("IND-636", "Operaciones Unitarias III y Lab", 6, "Pendiente", 0, "IND-536"),
        # Semestre 7
        ("IND-721", "Ingeniería Legal", 7, "Pendiente", 0, "IND-621"),
        ("IND-742", "Ingeniería de Simulación y Lab", 7, "Pendiente", 0, "IND-642, IND-643"),
        ("IND-723", "Prep. y Eval. de Proyectos I", 7, "Pendiente", 0, "IND-624"),
        ("IND-734", "Seguridad Industrial y Salud Ocupacional", 7, "Pendiente", 0, "IND-635"),
        ("IND-735", "Diseño Industrial y Lab", 7, "Pendiente", 0, "IND-635"),
        ("IND-736", "Tecnología de Alimentos y Lab", 7, "Pendiente", 0, "IND-636"),
        # Semestre 8
        ("IND-841", "Planif. y Control de la Producción I", 8, "Pendiente", 0, "IND-735"),
        ("IND-812", "Taller de Proyecto de Grado I", 8, "Pendiente", 0, "IND-723"),
        ("IND-823", "Prep. y Eval. de Proyectos II", 8, "Pendiente", 0, "IND-723"),
        ("IND-844", "Gestión de la Calidad", 8, "Pendiente", 0, "IND-721, IND-734"),
        ("IND-835", "Automatización y Lab", 8, "Pendiente", 0, "IND-735"),
        ("IND-836", "Diseño de Procesos Industriales I", 8, "Pendiente", 0, "IND-736"),
        # Semestre 9
        ("IND-941", "Planif. y Control de la Producción II", 9, "Pendiente", 0, "IND-841"),
        ("IND-912", "Taller de Proyecto de Grado II", 9, "Pendiente", 0, "IND-812"),
        ("IND-915", "Prácticas Industriales", 9, "Pendiente", 0, "IND-835"),
        ("IND-943", "Gerencia de Proyectos", 9, "Pendiente", 0, "IND-823"),
        ("IND-944", "Logística", 9, "Pendiente", 0, "IND-844"),
        ("IND-936", "Diseño de Procesos Industriales II", 9, "Pendiente", 0, "IND-836")
    ]
    cursor.executemany("INSERT OR IGNORE INTO academic_courses VALUES (?, ?, ?, ?, ?, ?)", umsa_courses)

def seed_instagram_resources(cursor):
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    saved_items = data.get("saved_items", {})
    chat_links = data.get("chat_links", {})
    
    rows = []
    # Add saved posts
    for cat, items in saved_items.items():
        for item in items:
            url = item.get("url", "")
            caption = item.get("caption", "").strip()
            date = item.get("date", "")
            title = caption.split("\n")[0][:80] if caption else "Publicación de Instagram"
            if url:
                rows.append((url, title, caption[:500], cat, date, "Instagram Guardados", "Pendiente", ""))
                
    # Add chat links
    for cat, items in chat_links.items():
        for item in items:
            url = item.get("url", "")
            text = item.get("text", "").strip()
            date = item.get("date", "")
            account = item.get("account", "Chat")
            title = f"Recurso de @{account}: {text[:50]}" if text else f"Enlace de @{account}"
            if url:
                rows.append((url, title, text, cat, date, f"Chat con @{account}", "Pendiente", ""))
                
    cursor.executemany("""
    INSERT OR IGNORE INTO resources (url, title, summary, category, date_added, source, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

if __name__ == "__main__":
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM resources")
    res_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM academic_courses")
    courses_count = cur.fetchone()[0]
    print(f"Base de datos NEXUS inicializada correctamente.")
    print(f"Recursos en Segundo Cerebro: {res_count}")
    print(f"Materias UMSA cargadas: {courses_count}")
    conn.close()
