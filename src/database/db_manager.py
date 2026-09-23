import sqlite3
import os
import json

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
DB_PATH = os.path.join(ROOT_DIR, "data", "nexus.db")
JSON_PATH = os.path.join(ROOT_DIR, "data", "instagram_resources.json")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Knowledge Base / Resources (Full Typed Schema)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resources (
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
        repeated_resources_list TEXT,
        user_custom_analysis TEXT
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
    
    # 5. NASA Daily Pre-Flight Tasks (InvernovAH 5-Step System)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nasa_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        step_number INTEGER,
        task_description TEXT,
        is_critical INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0,
        time_estimate_min INTEGER DEFAULT 30
    )
    """)
    
    # 6. Lotus Blossom Matrix (Matsumura 8x8 System)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lotus_blossom (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pillar_id INTEGER,
        pillar_name TEXT,
        micro_task_num INTEGER,
        action_title TEXT,
        status TEXT DEFAULT 'Pendiente',
        impact_weight INTEGER DEFAULT 1
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

    # Seed Lotus Blossom if empty
    cursor.execute("SELECT COUNT(*) FROM lotus_blossom")
    if cursor.fetchone()[0] == 0:
        seed_lotus_blossom(cursor)
        conn.commit()

    # Seed Sample Metrics if empty
    cursor.execute("SELECT COUNT(*) FROM daily_metrics")
    if cursor.fetchone()[0] == 0:
        seed_daily_metrics(cursor)
        conn.commit()

    # Seed Sample Finance Transactions if empty
    cursor.execute("SELECT COUNT(*) FROM finance_transactions")
    if cursor.fetchone()[0] == 0:
        seed_finance_transactions(cursor)
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

def seed_lotus_blossom(cursor):
    """Inicializa la Matriz Flor de Loto (Matsumura 8x8) para Mark Hazard."""
    matrix = [
        # Pilar 1: Excelencia UMSA
        (1, "1. Excelencia UMSA (Ing. Industrial)", 1, "Aprobar IND-311 (Probabilidad) con nota > 75", "En Progreso", 2),
        (1, "1. Excelencia UMSA (Ing. Industrial)", 2, "Dominar IND-312 (Informática para Ingeniería)", "En Progreso", 2),
        (1, "1. Excelencia UMSA (Ing. Industrial)", 3, "Superar IND-333 (Procesos de Manufactura)", "En Progreso", 2),
        (1, "1. Excelencia UMSA (Ing. Industrial)", 4, "Mantener promedio ponderado acumulado > 70", "En Progreso", 1),
        (1, "1. Excelencia UMSA (Ing. Industrial)", 5, "Adelantar temario de 4to semestre (Estadística Inferencial)", "Pendiente", 1),
        (1, "1. Excelencia UMSA (Ing. Industrial)", 6, "Conectar proyectos de taller con casos reales de manufactura", "Pendiente", 1),
        (1, "1. Excelencia UMSA (Ing. Industrial)", 7, "Establecer grupo de estudio de alto rendimiento", "Completada", 1),
        (1, "1. Excelencia UMSA (Ing. Industrial)", 8, "Planificar perfil de grado / Trabajo Dirigido", "Pendiente", 2),

        # Pilar 2: Programación & Data Science
        (2, "2. Programación & Data Science", 1, "Dominar Python intermedio-avanzado y funciones puras", "En Progreso", 2),
        (2, "2. Programación & Data Science", 2, "Manipulación de datos profesional con Pandas y NumPy", "En Progreso", 2),
        (2, "2. Programación & Data Science", 3, "SQL analítico (joins, queries agregadas, subconsultas)", "En Progreso", 2),
        (2, "2. Programación & Data Science", 4, "Dashboards ejecutivos interactivos con Plotly & Streamlit", "Completada", 2),
        (2, "2. Programación & Data Science", 5, "Análisis exploratorio de datos (EDA) en datasets industriales", "Pendiente", 1),
        (2, "2. Programación & Data Science", 6, "Flujo de trabajo Git/GitHub profesional y ramas", "Completada", 1),
        (2, "2. Programación & Data Science", 7, "Publicar 3 proyectos de portafolio con código reproducible", "En Progreso", 2),
        (2, "2. Programación & Data Science", 8, "Culminar curso certificado CS50 / Google Data Analytics", "En Progreso", 2),

        # Pilar 3: Automatización & Inteligencia Artificial
        (3, "3. Automatización & IA Aplicada", 1, "Automatización de flujos de trabajo con n8n", "En Progreso", 2),
        (3, "3. Automatización & IA Aplicada", 2, "Consumo e integración de APIs REST y webhooks con Python", "Completada", 2),
        (3, "3. Automatización & IA Aplicada", 3, "Prompt Engineering estructurado y LLMs (Gemini/OpenAI)", "Completada", 2),
        (3, "3. Automatización & IA Aplicada", 4, "Arquitectura de agentes autónomos y herramientas MCP", "Completada", 2),
        (3, "3. Automatización & IA Aplicada", 5, "Web scraping ético y extracción de metadatos (trafilatura)", "Completada", 1),
        (3, "3. Automatización & IA Aplicada", 6, "Automatización de reportes de calidad industrial", "Pendiente", 1),
        (3, "3. Automatización & IA Aplicada", 7, "Integración de Bot de Telegram para captura móvil", "En Progreso", 2),
        (3, "3. Automatización & IA Aplicada", 8, "Despliegue autónomo 24/7 en la nube (NEXUS Life OS)", "Completada", 2),

        # Pilar 4: Inglés Profesional C1
        (4, "4. Inglés Profesional C1", 1, "Escucha diaria de 30 min (podcasts de ingeniería/tech)", "En Progreso", 1),
        (4, "4. Inglés Profesional C1", 2, "Práctica semanal de conversación técnica y pronunciación", "En Progreso", 2),
        (4, "4. Inglés Profesional C1", 3, "Redacción técnica de documentación y READMEs en inglés", "Completada", 1),
        (4, "4. Inglés Profesional C1", 4, "Simulación de entrevistas técnicas laborales en inglés", "Pendiente", 2),
        (4, "4. Inglés Profesional C1", 5, "Lectura de documentación oficial en inglés sin traducir", "Completada", 1),
        (4, "4. Inglés Profesional C1", 6, "Certificación formal de nivel (EF SET / Duolingo English)", "Pendiente", 1),
        (4, "4. Inglés Profesional C1", 7, "Configuración del OS y herramientas 100% en inglés", "Completada", 1),
        (4, "4. Inglés Profesional C1", 8, "Networking en comunidades de Discord/Reddit técnicas", "Pendiente", 1),

        # Pilar 5: Finanzas Personales & FIRE (InvernovAH)
        (5, "5. Finanzas Personales & FIRE", 1, "Registro diario sin falta de ingresos y gastos", "Completada", 2),
        (5, "5. Finanzas Personales & FIRE", 2, "Mantener tasa de ahorro sistemática > 40%", "En Progreso", 2),
        (5, "5. Finanzas Personales & FIRE", 3, "Construir colchón de seguridad de 6 meses de gastos", "En Progreso", 2),
        (5, "5. Finanzas Personales & FIRE", 4, "Cuenta de corretaje internacional verificada (IBKR)", "En Progreso", 2),
        (5, "5. Finanzas Personales & FIRE", 5, "Inversión indexada pasiva recurrente (S&P 500 / MSCI World)", "Pendiente", 2),
        (5, "5. Finanzas Personales & FIRE", 6, "Eliminación sistemática de compras impulsivas y gastos fuga", "En Progreso", 1),
        (5, "5. Finanzas Personales & FIRE", 7, "Estrategia de custodia y cobros en divisas fuertes (USD)", "En Progreso", 1),
        (5, "5. Finanzas Personales & FIRE", 8, "Balance y revisión trimestral de patrimonio neto", "Pendiente", 1),

        # Pilar 6: Salud Física & Energía
        (6, "6. Salud Física & Energía", 1, "Dormir 7 a 8 horas con horario regular y sin pantallas pre-sueño", "En Progreso", 2),
        (6, "6. Salud Física & Energía", 2, "Entrenamiento de fuerza 4 días por semana", "En Progreso", 2),
        (6, "6. Salud Física & Energía", 3, "Hidratación sistemática (2.5 litros de agua al día)", "En Progreso", 1),
        (6, "6. Salud Física & Energía", 4, "Nutrición con proteína adecuada y mínimo ultraprocesados", "En Progreso", 1),
        (6, "6. Salud Física & Energía", 5, "Caminata y luz solar 15 minutos en la mañana", "En Progreso", 1),
        (6, "6. Salud Física & Energía", 6, "Ergonomía de escritorio y pausas activas pomodoro", "En Progreso", 1),
        (6, "6. Salud Física & Energía", 7, "Desconexión digital total 1 tarde por semana", "Pendiente", 1),
        (6, "6. Salud Física & Energía", 8, "Chequeo médico y analítica de control anual", "Pendiente", 1),

        # Pilar 7: Marca Personal & Networking Tech
        (7, "7. Marca Personal & Networking Tech", 1, "Perfil de LinkedIn con enfoque en Ingeniería Industrial 4.0", "Completada", 2),
        (7, "7. Marca Personal & Networking Tech", 2, "Publicar 1 aprendizaje o proyecto técnico a la semana", "Pendiente", 1),
        (7, "7. Marca Personal & Networking Tech", 3, "README de GitHub pulido con proyectos destacados", "Completada", 2),
        (7, "7. Marca Personal & Networking Tech", 4, "Conectar con 5 ingenieros y líderes tech por semana", "Pendiente", 1),
        (7, "7. Marca Personal & Networking Tech", 5, "Participar en eventos de tecnología y analítica en Bolivia", "Pendiente", 1),
        (7, "7. Marca Personal & Networking Tech", 6, "Currículum en inglés formato Harvard / ATS-Friendly", "En Progreso", 2),
        (7, "7. Marca Personal & Networking Tech", 7, "Documentar métricas de impacto en proyectos académicos", "En Progreso", 1),
        (7, "7. Marca Personal & Networking Tech", 8, "Crear repositorio de plantillas y snippets reutilizables", "Completada", 1),

        # Pilar 8: Gestión de Proyectos & Liderazgo
        (8, "8. Gestión de Proyectos & Liderazgo", 1, "Aplicación de metodología Kanban en tareas diarias", "Completada", 1),
        (8, "8. Gestión de Proyectos & Liderazgo", 2, "Bloques estrictos de trabajo profundo (Deep Work 90 min)", "En Progreso", 2),
        (8, "8. Gestión de Proyectos & Liderazgo", 3, "Comunicación asertiva y negociación de entregables", "En Progreso", 1),
        (8, "8. Gestión de Proyectos & Liderazgo", 4, "Resolución de problemas con método 5 Porqués e Ishikawa", "En Progreso", 1),
        (8, "8. Gestión de Proyectos & Liderazgo", 5, "Priorización implacable con la Matriz de Eisenhower", "Completada", 1),
        (8, "8. Gestión de Proyectos & Liderazgo", 6, "Liderazgo activo en grupos universitarios de la UMSA", "En Progreso", 2),
        (8, "8. Gestión de Proyectos & Liderazgo", 7, "Protocolo de contingencia y resiliencia ante exámenes", "En Progreso", 1),
        (8, "8. Gestión de Proyectos & Liderazgo", 8, "Revisión retrospectiva semanal estilo Scrum los domingos", "En Progreso", 2)
    ]
    cursor.executemany("""
    INSERT INTO lotus_blossom (pillar_id, pillar_name, micro_task_num, action_title, status, impact_weight)
    VALUES (?, ?, ?, ?, ?, ?)
    """, matrix)

def seed_daily_metrics(cursor):
    """Inserta métricas iniciales de los últimos días para alimentar los gráficos de energía y sueño."""
    metrics = [
        ("2026-09-17", 7.2, 8, 8, 5.5, "Sesión de estudio y avance de proyectos"),
        ("2026-09-18", 6.8, 7, 7, 4.0, "Clases UMSA y revisión de laboratorios"),
        ("2026-09-19", 7.5, 9, 8, 6.0, "Deep work en programación y desarrollo"),
        ("2026-09-20", 8.0, 9, 9, 6.5, "Desarrollo de NEXUS Life OS y testing"),
        ("2026-09-21", 7.0, 8, 8, 5.0, "Despliegue y optimización en la nube"),
        ("2026-09-22", 7.4, 8, 8, 5.5, "Retorno y planificación de módulos")
    ]
    cursor.executemany("""
    INSERT OR IGNORE INTO daily_metrics (date, sleep_hours, energy_level, mood, productive_hours, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    """, metrics)

def seed_finance_transactions(cursor):
    """Inserta transacciones base para activar el cálculo de Tasa de Ahorro y Fondo de Emergencia."""
    transactions = [
        ("2026-09-01", "Ingreso", "Ingresos Principales / Remoto", 1200.0, "Ingreso mensual estimado"),
        ("2026-09-02", "Gasto Fijo", "Alquiler & Servicios", 350.0, "Gastos esenciales de vivienda"),
        ("2026-09-03", "Gasto Fijo", "Alimentación Saludable", 220.0, "Supermercado y nutrición"),
        ("2026-09-04", "Gasto Fijo", "Transporte & Universidad UMSA", 60.0, "Pasajes y materiales"),
        ("2026-09-05", "Gasto Opcional", "Suscripciones / Internet de alta velocidad", 40.0, "Conectividad tech"),
        ("2026-09-10", "Ahorro / Inversión", "Fondo de Emergencia (Ahorro)", 300.0, "Traspaso a colchón de seguridad"),
        ("2026-09-15", "Ahorro / Inversión", "Inversión Indexada Pasiva (FIRE)", 230.0, "Aporte a índice global")
    ]
    cursor.executemany("""
    INSERT INTO finance_transactions (date, type, category, amount, description)
    VALUES (?, ?, ?, ?, ?)
    """, transactions)

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
