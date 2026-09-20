import sqlite3
import re
import urllib.parse
from typing import Dict, List, Tuple, Optional, Any

# Canonical catalog of known tools, platforms, courses, and certifications
KNOWN_RESOURCES = {
    "harvard_cs50": {
        "name": "Harvard CS50x (Ciencias de la Computación)",
        "patterns": [r"\bcs50x?\b", r"harvard\s*(?:cs50|comput)"],
        "url": "https://cs50.harvard.edu/x/",
        "category": "💻 Programación & Computer Science",
        "employability": 95,
        "employability_details": "Gold Standard en CS. Altamente valorado por BigTech y startups.",
        "has_cert": "Certificado Verificado Gratuito (edX / Harvard)",
        "recruiter_weight": "Excelente (Prueba de rigor técnico y algoritmos)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Acceso total sin restricciones para estudiantes en Bolivia."
    },
    "nvidia_dli": {
        "name": "NVIDIA Deep Learning Institute",
        "patterns": [r"nvidia.*?(?:dli|deep learning|certificaci|curso)"],
        "url": "https://learn.nvidia.com",
        "category": "🤖 Inteligencia Artificial & Agentes",
        "employability": 96,
        "employability_details": "Máximo estándar en aceleración por hardware y Deep Learning.",
        "has_cert": "Certificado Oficial NVIDIA",
        "recruiter_weight": "Crítico (Líder mundial en infraestructura de IA)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Disponible en línea con laboratorios en la nube."
    },
    "nasa_lspace": {
        "name": "NASA L'SPACE / Academy",
        "patterns": [r"nasa.*?(?:l'?space|academy|stem)"],
        "url": "https://www.lspace.asu.edu",
        "category": "🚀 Pasantías, Becas & CV",
        "employability": 98,
        "employability_details": "Prestigio internacional de primer nivel para proyectos de ingeniería aeroespacial.",
        "has_cert": "Certificado de Participación de Proyecto NASA",
        "recruiter_weight": "Élite (Distingue fuertemente en postulaciones internacionales)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Abierto a postulantes internacionales según convocatoria."
    },
    "claude_code": {
        "name": "Anthropic Claude Code (Agente CLI en Terminal)",
        "patterns": [r"claude code", r"claude en terminal", r"claude.*?(?:cli|terminal)"],
        "url": "https://docs.anthropic.com/en/docs/agents-and-tools/claude-code",
        "category": "🤖 Inteligencia Artificial & Agentes",
        "employability": 94,
        "employability_details": "Herramienta de desarrollo agéntico puntera para ingenieros de software e IA.",
        "has_cert": "Habilidad Práctica / Open Source",
        "recruiter_weight": "Innovación (Demuestra adopción temprana de agentes autónomos)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Utilizable mediante clave de API de Anthropic o Google Cloud Vertex."
    },
    "claude_academy": {
        "name": "Anthropic Claude Certified Architect & Academy",
        "patterns": [r"claude.*?(?:certificaci|certified|13 certificaciones|skilljar|curso online gratis)"],
        "url": "https://anthropic.skilljar.com",
        "category": "🤖 Inteligencia Artificial & Agentes",
        "employability": 95,
        "employability_details": "Certificación oficial del creador de Claude (Anthropic).",
        "has_cert": "Certificado Oficial Anthropic",
        "recruiter_weight": "Muy Alto (Validación directa del proveedor del modelo)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Cursos en línea gratuitos sin restricciones geográficas."
    },
    "mcp_anthropic": {
        "name": "Model Context Protocol (MCP - Anthropic)",
        "patterns": [r"\bmcp\b", r"model context protocol"],
        "url": "https://modelcontextprotocol.io",
        "category": "🤖 Inteligencia Artificial & Agentes",
        "employability": 93,
        "employability_details": "Nuevo estándar abierto de la industria para interconectar IAs con datos locales.",
        "has_cert": "Estándar de la Industria",
        "recruiter_weight": "Vanguardia (Arquitectura de software de última generación)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Código y protocolos abiertos en GitHub."
    },
    "purdue_krach": {
        "name": "Krach Institute Purdue Tech Diplomacy",
        "patterns": [r"purdue", r"krach institute", r"techdiplomacy"],
        "url": "https://techdiplomacy.org",
        "category": "🚀 Pasantías, Becas & CV",
        "employability": 92,
        "employability_details": "Formación estratégica en intersección de geopolítica, IA y gobernanza tecnológica.",
        "has_cert": "Certificado Ejecutivo / Académico",
        "recruiter_weight": "Estratégico (Ideal para roles de consultoría y dirección)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Programas en línea abiertos."
    },
    "n8n_automation": {
        "name": "n8n Workflow Automation (Auto-alojado)",
        "patterns": [r"\bn8n\b"],
        "url": "https://n8n.io",
        "category": "⚙️ Automatización & Productividad",
        "employability": 94,
        "employability_details": "Herramienta nº1 para automatización corporativa con soporte nativo de IA.",
        "has_cert": "Portafolio de Flujos / Pipelines",
        "recruiter_weight": "Altamente Práctico (Automatiza operaciones de negocio en Ing. Industrial)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Open source, se puede correr gratis en Docker local o VPS."
    },
    "make_automation": {
        "name": "Make.com (Integromat Automation)",
        "patterns": [r"make\.com", r"\bmake\b.*?(?:automatiz|integromat)"],
        "url": "https://www.make.com",
        "category": "⚙️ Automatización & Productividad",
        "employability": 88,
        "employability_details": "Plataforma no-code/low-code ampliamente adoptada por agencias y empresas.",
        "has_cert": "Certificaciones Oficiales Make Academy",
        "recruiter_weight": "Práctico (Optimización de procesos)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Plan gratuito disponible con 1,000 operaciones mensuales."
    },
    "v0_vercel": {
        "name": "V0.dev Generador UI por Vercel",
        "patterns": [r"v0\.dev", r"\bv0\b.*?(?:vercel|ui|interfaz|diseño)"],
        "url": "https://v0.dev",
        "category": "💻 Programación & Computer Science",
        "employability": 90,
        "employability_details": "Generación instantánea de interfaces con React, Tailwind y Next.js.",
        "has_cert": "Portafolio Frontend",
        "recruiter_weight": "Alto en Startups (Acelera prototipado 10x)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Acceso web gratuito con créditos diarios."
    },
    "bolt_new": {
        "name": "Bolt.new Web Dev (StackBlitz)",
        "patterns": [r"bolt\.new", r"\bbolt\b.*?(?:stackblitz|web|fullstack|app)"],
        "url": "https://bolt.new",
        "category": "💻 Programación & Computer Science",
        "employability": 89,
        "employability_details": "Entorno completo en el navegador con soporte de despliegue directo.",
        "has_cert": "Portafolio Web Fullstack",
        "recruiter_weight": "Práctico (Velocidad de entrega)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Gratuito con cuota diaria de tokens."
    },
    "cursor_ai": {
        "name": "Cursor AI Code Editor",
        "patterns": [r"cursor.*?(?:editor|ide|ai|code)"],
        "url": "https://www.cursor.com",
        "category": "💻 Programación & Computer Science",
        "employability": 93,
        "employability_details": "El editor de código con IA más utilizado por programadores de Silicon Valley.",
        "has_cert": "Dominio de Herramienta",
        "recruiter_weight": "Multiplicador de Productividad",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Descarga gratuita y plan Hobby funcional sin coste."
    },
    "ollama_local": {
        "name": "Ollama Local LLM Runtime",
        "patterns": [r"\bollama\b"],
        "url": "https://ollama.com",
        "category": "🤖 Inteligencia Artificial & Agentes",
        "employability": 92,
        "employability_details": "Ejecución de modelos LLM locales sin coste de API ni dependencia de nube.",
        "has_cert": "Ingeniería de Sistemas de IA",
        "recruiter_weight": "Alto (Privacidad de datos y arquitectura local)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "100% Open source, corre offline en tu PC."
    },
    "deepseek_ai": {
        "name": "DeepSeek AI (R1 & V3)",
        "patterns": [r"\bdeepseek\b"],
        "url": "https://www.deepseek.com",
        "category": "🤖 Inteligencia Artificial & Agentes",
        "employability": 91,
        "employability_details": "Modelos de razonamiento matemático y de código con arquitectura MoE puntera.",
        "has_cert": "Investigación y Aplicación",
        "recruiter_weight": "Alto (Modelos eficientes de última generación)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Acceso web y API a costos mínimos."
    },
    "google_cloud_skills": {
        "name": "Google Cloud Skills Boost / Google AI",
        "patterns": [r"google.*?(?:cloud skills|ai pro|skills boost|cloud learning)"],
        "url": "https://www.cloudskillsboost.google",
        "category": "🤖 Inteligencia Artificial & Agentes",
        "employability": 93,
        "employability_details": "Laboratorios oficiales de Google Cloud en GCP, Vertex AI y BigQuery.",
        "has_cert": "Insignias y Credenciales Digitales Google Cloud",
        "recruiter_weight": "Muy Alto (Validación oficial de Google)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Disponible en español e inglés para Bolivia."
    },
    "google_ai_essentials": {
        "name": "Google IA Esenciales (Certificado Oficial)",
        "patterns": [r"google.*?ia esenciales", r"ia esenciales.*?google"],
        "url": "https://grow.google/certificates/es/ai-essentials/",
        "category": "🤖 Inteligencia Artificial & Agentes",
        "employability": 89,
        "employability_details": "Certificación fundamental emitida por Google sobre uso productivo de IA.",
        "has_cert": "Certificado Oficial Google Career Certificate",
        "recruiter_weight": "Sólido (Acredita alfabetización de IA a nivel corporativo)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "100% en línea y en español."
    },
    "microsoft_students": {
        "name": "Microsoft Learn & Azure for Students",
        "patterns": [r"microsoft.*?(?:estudiantes|learn|azure for students|founders hub)"],
        "url": "https://learn.microsoft.com",
        "category": "💻 Programación & Computer Science",
        "employability": 92,
        "employability_details": "Créditos gratuitos de Azure y certificaciones Microsoft para universitarios.",
        "has_cert": "Certificaciones Microsoft Fundamentals (AZ-900, AI-900)",
        "recruiter_weight": "Corporativo (Reconocido por reclutadores internacionales)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Verificable con correo institucional de la UMSA (.umsa.bo)."
    },
    "github_student_pack": {
        "name": "GitHub Student Developer Pack",
        "patterns": [r"github student pack", r"student developer pack"],
        "url": "https://education.github.com/pack",
        "category": "💻 Programación & Computer Science",
        "employability": 94,
        "employability_details": "Acceso gratuito a Copilot, dominios, hosting y herramientas Pro valoradas en $200k.",
        "has_cert": "Herramientas de Industria",
        "recruiter_weight": "Esencial para cualquier estudiante de tecnología",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Aprobación con carnet universitario o matrícula UMSA."
    },
    "mit_ocw": {
        "name": "MIT OpenCourseWare (Computer Science & Math)",
        "patterns": [r"mit.*?(?:ocw|openlearning|6\.0001|6\.0002)"],
        "url": "https://ocw.mit.edu",
        "category": "💻 Programación & Computer Science",
        "employability": 97,
        "employability_details": "El contenido pedagógico y tareas de la mejor universidad técnica del planeta.",
        "has_cert": "Autoaprendizaje Riguroso MIT",
        "recruiter_weight": "Prestigio Máximo (Validación técnica demostrable en proyectos)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "100% de libre acceso gratuito mundial."
    },
    "coursera_free": {
        "name": "Coursera Catálogo de Cursos Gratuitos",
        "patterns": [r"coursera.*?(?:gratis|free|cursos)"],
        "url": "https://www.coursera.org/courses?query=free",
        "category": "💻 Programación & Computer Science",
        "employability": 88,
        "employability_details": "Cursos de universidades como Stanford, DeepLearning.AI y Google en modo auditoría gratuita.",
        "has_cert": "Auditoría Gratuita / Beca Financiera de Certificado",
        "recruiter_weight": "Reconocido globalmente",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Ayuda económica disponible al 100% para Bolivia."
    },
    "edx_free": {
        "name": "edX Programas Abiertos de Universidades",
        "patterns": [r"edx.*?(?:gratis|cursos|free)"],
        "url": "https://www.edx.org",
        "category": "💻 Programación & Computer Science",
        "employability": 90,
        "employability_details": "Cursos oficiales de Harvard, MIT, Berkeley en modalidad de acceso abierto.",
        "has_cert": "Auditoría Gratuita",
        "recruiter_weight": "Académico de Alto Nivel",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Acceso libre desde Bolivia."
    },
    "futurelearn_free": {
        "name": "FutureLearn Cursos Universitarios",
        "patterns": [r"futurelearn"],
        "url": "https://www.futurelearn.com/courses",
        "category": "💻 Programación & Computer Science",
        "employability": 84,
        "employability_details": "Cursos de universidades británicas y europeas.",
        "has_cert": "Acceso gratuito con opción de certificado",
        "recruiter_weight": "Complementario",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Disponible en línea."
    },
    "alison_free": {
        "name": "Alison Certificaciones y Cursos Gratuitos",
        "patterns": [r"alison.*?(?:cursos|diploma|certificad)"],
        "url": "https://alison.com/es/cursos",
        "category": "⚙️ Automatización & Productividad",
        "employability": 80,
        "employability_details": "Diplomados y cursos técnicos en seguridad industrial, ISO 9001 y operaciones.",
        "has_cert": "Certificado / Diploma Gratuito de Finalización",
        "recruiter_weight": "Formativo / Operativo",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "100% gratuito y disponible en español."
    },
    "huggingface_learn": {
        "name": "Hugging Face LLM Course & Transformers",
        "patterns": [r"hugging\s*face.*?(?:llm|course|curso|transformers)"],
        "url": "https://huggingface.co/learn",
        "category": "🤖 Inteligencia Artificial & Agentes",
        "employability": 95,
        "employability_details": "La comunidad nº1 de modelos abiertos de Machine Learning.",
        "has_cert": "Certificado Digital Hugging Face",
        "recruiter_weight": "Crítico para perfiles de AI Engineer",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Cursos y repositorio abiertos sin costo."
    },
    "fastai_course": {
        "name": "fast.ai - Practical Deep Learning for Coders",
        "patterns": [r"fast\.ai", r"practical deep learning for coders"],
        "url": "https://course.fast.ai",
        "category": "🤖 Inteligencia Artificial & Agentes",
        "employability": 94,
        "employability_details": "El curso de Deep Learning práctico más elogiado por ingenieros de la industria.",
        "has_cert": "Portafolio Práctico de Modelos",
        "recruiter_weight": "Muy respetado por practicantes técnicos de IA",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "100% libre y gratuito en línea."
    },
    "kaggle_learn": {
        "name": "Kaggle Competitions & Micro-Courses",
        "patterns": [r"\bkaggle\b"],
        "url": "https://www.kaggle.com",
        "category": "📊 Datos, Estadística & Analítica",
        "employability": 95,
        "employability_details": "Plataforma de ciencia de datos de Google. El ranking de Kaggle es garantía de contratación.",
        "has_cert": "Certificados de Micro-Cursos Kaggle & Medallas de Competición",
        "recruiter_weight": "Élite en Data Science y Machine Learning",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Acceso total a notebooks en GPUs gratuitas (T4/P100)."
    },
    "stimuler_english": {
        "name": "Stimuler English App & Speaking",
        "patterns": [r"stimuler"],
        "url": "https://www.stimuler.com",
        "category": "🗣️ Idiomas & Comunicación Global",
        "employability": 87,
        "employability_details": "Práctica oral intensiva de inglés con retroalimentación instantánea de IA.",
        "has_cert": "Evaluación de Nivel CEFR (B1, B2, C1)",
        "recruiter_weight": "Requisito Fundamental (El inglés duplica el salario)",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Disponible en App Store y Google Play."
    },
    "notion_os": {
        "name": "Notion AI & Sistema de Productividad",
        "patterns": [r"\bnotion\b"],
        "url": "https://www.notion.so",
        "category": "⚙️ Automatización & Productividad",
        "employability": 86,
        "employability_details": "Organización personal, gestión ágil de proyectos y base de conocimiento.",
        "has_cert": "Notion Certified",
        "recruiter_weight": "Habilidad de Gestión",
        "bolivia_eligible": "✅ 100% Disponible en Bolivia",
        "bolivia_details": "Plan Personal Pro 100% gratuito para estudiantes universitarios con correo institucional."
    }
}

URL_REGEX = re.compile(r'https?://[^\s\)\]\"\'<>]+')

def normalize_url(url: str) -> str:
    """Clean and normalize URL for robust comparison."""
    if not url:
        return ""
    url = url.strip().rstrip('.,;:/-')
    parsed = urllib.parse.urlparse(url)
    clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
    return clean.lower()

def extract_external_links(text: str) -> List[str]:
    """Extract non-social external links from text."""
    if not text:
        return []
    raw = URL_REGEX.findall(text)
    results = []
    for l in raw:
        cl = l.rstrip('.,;:/-')
        low = cl.lower()
        if "instagram.com" not in low and "facebook.com" not in low and "tiktok.com" not in low:
            results.append(cl)
    return results

def detect_resources_in_text(text: str, main_url: str = "") -> List[Dict[str, Any]]:
    """
    Detect all discrete canonical resources mentioned in a post or publication.
    """
    full_text = f"{text} {main_url}".lower()
    detected = []
    seen_ids = set()

    # 1. Match known canonical entities
    for res_id, res_info in KNOWN_RESOURCES.items():
        matched = False
        for pat in res_info["patterns"]:
            if re.search(pat, full_text, re.IGNORECASE):
                matched = True
                break
        if not matched and res_info["url"]:
            parsed_target = urllib.parse.urlparse(res_info["url"]).netloc.lower()
            if parsed_target and parsed_target in full_text:
                matched = True

        if matched and res_id not in seen_ids:
            seen_ids.add(res_id)
            detected.append({
                "type": "cataloged",
                "canonical_id": res_id,
                "name": res_info["name"],
                "url": res_info["url"],
                "category": res_info["category"],
                "employability": res_info["employability"],
                "employability_details": res_info["employability_details"],
                "has_cert": res_info["has_cert"],
                "recruiter_weight": res_info["recruiter_weight"],
                "bolivia_eligible": res_info["bolivia_eligible"],
                "bolivia_details": res_info["bolivia_details"]
            })

    # 2. Extract external URLs that might be distinct tools/repos
    ext_links = extract_external_links(text)
    for link in ext_links:
        norm = normalize_url(link)
        already_covered = any(normalize_url(d["url"]) == norm for d in detected)
        if not already_covered:
            parsed = urllib.parse.urlparse(link)
            domain = parsed.netloc.replace("www.", "")
            path_parts = [p for p in parsed.path.split('/') if p]
            if "github.com" in domain and len(path_parts) >= 2:
                name = f"GitHub: {path_parts[0]}/{path_parts[1]}"
                res_key = f"gh_{path_parts[0]}_{path_parts[1]}".lower()
            else:
                name = f"{domain.capitalize()}: {path_parts[-1] if path_parts else domain}"
                res_key = f"ext_{domain}".lower()

            if res_key not in seen_ids:
                seen_ids.add(res_key)
                detected.append({
                    "type": "external_link",
                    "canonical_id": res_key,
                    "name": name,
                    "url": link,
                    "category": "🌐 Enlace Directo",
                    "employability": 80,
                    "employability_details": "Recurso técnico externo.",
                    "has_cert": "Por verificar",
                    "recruiter_weight": "Práctico",
                    "bolivia_eligible": "✅ 100% Disponible en Bolivia",
                    "bolivia_details": "Acceso libre."
                })

    return detected

def analyze_against_db(
    cur: sqlite3.Cursor,
    text: str,
    url: str = "",
    direct_url: str = "",
    exclude_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Analyzes a publication against current DB records.
    Returns:
    - status: 'PURE_DUPLICATE' | 'MIXED' | 'NEW'
    - detected_resources: List of all detected resources
    - new_resources: List of non-repeated resources
    - repeated_resources: List of repeated resources with reference to existing DB row
    - primary_id: DB row ID if duplicate
    - primary_title: DB row title if duplicate
    """
    norm_url = normalize_url(url)
    norm_direct = normalize_url(direct_url)

    # 1. Exact URL match
    if norm_url and "instagram.com" not in norm_url:
        query = "SELECT id, title, direct_url_clean, url FROM resources WHERE LOWER(url) = ? OR LOWER(direct_url_clean) = ?"
        params = [norm_url, norm_url]
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)
        cur.execute(query, params)
        exact_match = cur.fetchone()
        if exact_match:
            return {
                "status": "PURE_DUPLICATE",
                "reason": f"La URL ya se encuentra registrada en el recurso #{exact_match[0]} ('{exact_match[1]}')",
                "primary_id": exact_match[0],
                "primary_title": exact_match[1],
                "detected_resources": [],
                "new_resources": [],
                "repeated_resources": [{"name": exact_match[1], "url": exact_match[2] or exact_match[3], "existing_id": exact_match[0], "existing_title": exact_match[1]}]
            }

    # 2. Exact Direct URL match
    if norm_direct and "instagram.com" not in norm_direct:
        query = "SELECT id, title, direct_url_clean, url FROM resources WHERE LOWER(direct_url_clean) = ? OR LOWER(url) = ?"
        params = [norm_direct, norm_direct]
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)
        cur.execute(query, params)
        exact_match = cur.fetchone()
        if exact_match:
            return {
                "status": "PURE_DUPLICATE",
                "reason": f"El enlace directo ya se encuentra registrado en el recurso #{exact_match[0]} ('{exact_match[1]}')",
                "primary_id": exact_match[0],
                "primary_title": exact_match[1],
                "detected_resources": [],
                "new_resources": [],
                "repeated_resources": [{"name": exact_match[1], "url": exact_match[2] or exact_match[3], "existing_id": exact_match[0], "existing_title": exact_match[1]}]
            }

    # 3. Extract and check detected resources
    detected = detect_resources_in_text(f"{text} {direct_url}", url)
    if not detected:
        return {
            "status": "NEW",
            "reason": "Recurso independiente sin herramientas comunes detectadas.",
            "detected_resources": [],
            "new_resources": [],
            "repeated_resources": []
        }

    new_res = []
    rep_res = []

    for item in detected:
        cid = item["canonical_id"]
        cid_hyphen = cid.replace('_', '-')
        cid_under = cid.replace('-', '_')
        cname = item["name"]
        curl = item["url"]
        norm_item_url = normalize_url(curl)

        query = """
        SELECT id, title FROM resources
        WHERE (canonical_key IN (?, ?) 
               OR RTRIM(LOWER(direct_url_clean), '/') = ? 
               OR RTRIM(LOWER(url), '/') = ?
               OR LOWER(title) LIKE ?)
        """
        # extract short search token from name (e.g. 'CS50' or 'NVIDIA')
        token = cname.split(' ')[0] if ' ' in cname else cname
        params = [cid_hyphen, cid_under, norm_item_url, norm_item_url, f"%{token.lower()}%"]
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)
        query += " ORDER BY id ASC LIMIT 1"

        cur.execute(query, params)
        row = cur.fetchone()

        if row:
            rep_res.append({
                "canonical_id": cid,
                "name": cname,
                "url": curl,
                "existing_id": row[0],
                "existing_title": row[1]
            })
        else:
            new_res.append(item)

    if len(detected) >= 1 and len(new_res) == 0:
        existing_info = ", ".join(f"'{r['name']}' (en #{r['existing_id']})" for r in rep_res)
        return {
            "status": "PURE_DUPLICATE",
            "reason": f"Todos los recursos de esta publicación ya fueron guardados previamente: {existing_info}",
            "primary_id": rep_res[0]["existing_id"],
            "primary_title": rep_res[0]["existing_title"],
            "detected_resources": detected,
            "new_resources": [],
            "repeated_resources": rep_res
        }
    elif len(new_res) > 0 and len(rep_res) > 0:
        return {
            "status": "MIXED",
            "reason": f"Publicación con {len(new_res)} recurso(s) NUEVO(S) y {len(rep_res)} repetido(s).",
            "detected_resources": detected,
            "new_resources": new_res,
            "repeated_resources": rep_res
        }
    else:
        return {
            "status": "NEW",
            "reason": f"Contiene {len(new_res)} recurso(s) completamente nuevo(s).",
            "detected_resources": detected,
            "new_resources": new_res,
            "repeated_resources": []
        }

def format_mixed_markdown(new_resources: List[Dict[str, Any]], repeated_resources: List[Dict[str, Any]]) -> Tuple[str, str]:
    """
    Format user-facing markdown lists highlighting new vs repeated resources.
    """
    new_lines = []
    for item in new_resources:
        name = item.get("name", "Recurso")
        url = item.get("url", "#")
        new_lines.append(f"🟢 **{name}** — [Acceder al enlace directo 🚀]({url})")

    rep_lines = []
    for item in repeated_resources:
        name = item.get("name", "Recurso")
        eid = item.get("existing_id", "?")
        etitle = item.get("existing_title", "")
        if etitle:
            etitle_clean = etitle[:45] + ("..." if len(etitle) > 45 else "")
            rep_lines.append(f"⚠️ **{name}** — ya catalogado en tu biblioteca en **#{eid}** (*{etitle_clean}*)")
        else:
            rep_lines.append(f"⚠️ **{name}** — ya catalogado en tu biblioteca en **#{eid}**")

    new_str = "\n".join(new_lines) if new_lines else "Ninguno adicional."
    rep_str = "\n".join(rep_lines) if rep_lines else "Ninguno previo."
    return new_str, rep_str
