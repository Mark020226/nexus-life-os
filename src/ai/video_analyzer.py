import os
import re
import json
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional

def clean_direct_url(url: str) -> str:
    """Elimina parámetros de rastreo y tracking para obtener URLs canónicas limpias."""
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlparse(url.strip())
        query_dict = urllib.parse.parse_qs(parsed.query)
        # Quitar parámetros de tracking comunes
        tracking_params = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 
                           'utm_content', 'igshid', 'fbclid', 'gclid', 'ref', 'source'}
        cleaned_query = {k: v for k, v in query_dict.items() if k.lower() not in tracking_params}
        new_query = urllib.parse.urlencode(cleaned_query, doseq=True)
        cleaned_path = parsed.path.rstrip('/')
        cleaned_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            cleaned_path,
            parsed.params,
            new_query,
            ''
        ))
        return cleaned_url
    except Exception:
        return url.strip()

def fetch_url_metadata(url: str) -> Dict[str, Any]:
    """Extrae metadatos básicos, título y descripción desde la web o video."""
    meta = {
        "title": "",
        "author": "",
        "description": "",
        "direct_link": "",
        "is_video": False,
        "platform": "Web"
    }
    
    clean_url = url.strip()
    
    # 1. Detección de YouTube
    yt_match = re.search(r'(?:youtube\.com\/(?:watch\?v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})', clean_url)
    if yt_match:
        meta["is_video"] = True
        meta["platform"] = "YouTube"
        video_id = yt_match.group(1)
        meta["direct_link"] = f"https://www.youtube.com/watch?v={video_id}"
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    meta["title"] = data.get("title", "")
                    meta["author"] = data.get("author_name", "")
                    meta["description"] = f"Video de YouTube por {meta['author']}: {meta['title']}"
        except Exception:
            meta["title"] = f"YouTube Video ({video_id})"
        return meta

    # 2. Detección de Instagram
    ig_match = re.search(r'instagram\.com\/(?:p|reel|tv)\/([a-zA-Z0-9_-]+)', clean_url)
    if ig_match:
        meta["is_video"] = True
        meta["platform"] = "Instagram"
        code = ig_match.group(1)
        meta["title"] = f"Instagram Publicación/Reel ({code})"
        meta["author"] = "Instagram Creator"
        return meta

    # 3. Web General / Trafilatura
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(clean_url)
        if downloaded:
            extracted = trafilatura.extract(downloaded, include_comments=False)
            metadata = trafilatura.extract_metadata(downloaded)
            if metadata:
                meta["title"] = metadata.title or ""
                meta["author"] = metadata.author or ""
                meta["description"] = (metadata.description or extracted or "")[:800]
            elif extracted:
                meta["description"] = extracted[:800]
                meta["title"] = clean_url.split('/')[-1] or clean_url
    except Exception:
        pass

    if not meta["title"]:
        # Fallback de título basado en dominio
        parsed = urllib.parse.urlparse(clean_url)
        meta["title"] = f"Recurso en {parsed.netloc}"
        
    return meta

def analyze_with_gemini(url: str, meta: Dict[str, Any], custom_prompt: Optional[str] = None, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Consulta la API de Google Gemini para clasificar y responder preguntas sobre el recurso."""
    if not api_key:
        return None
        
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    system_instruction = """
    Eres el Asistente de Inteligencia Artificial de 'NEXUS Life OS', un sistema de optimización personal basado en la filosofía de Álvaro Hernández (InvernovAH):
    - Enfoque: Ingeniería Industrial aplicada a la vida, productividad de alta rentabilidad, tecnología y empleo remoto en USD.
    - Usuario: Mark Hazard, estudiante de Ingeniería Industrial (UMSA, Bolivia), enfocado en habilidades tecnológicas de alto valor (Python, IA, automatización, cloud, finanzas FIRE).
    
    Analiza el enlace y los metadatos proporcionados. Responde estrictamente con un objeto JSON válido con los siguientes campos:
    {
      "title": "Nombre claro y conciso del recurso real",
      "direct_url": "Enlace directo y real al recurso, curso o herramienta (NO a la publicación o intermediario)",
      "category": "Una de: [Cursos & Certificaciones, Inteligencia Artificial, Herramientas & Productividad, Programación & Data, Finanzas & Inversión, Carrera & Empleo]",
      "author": "Autor o entidad creadora",
      "ai_what_it_does": "Explicación directa de qué es o qué hace este recurso",
      "ai_how_it_helps": "Cómo ayuda concretamente a Mark en su carrera, habilidades o proyectos",
      "employability_index": (número entero entre 0 y 100 que refleja la demanda real y retorno de empleabilidad en el mercado global tech/industrial),
      "employability_details": "Justificación objetiva del porcentaje de empleabilidad",
      "has_certification": "Detalle de certificación: 'Certificado Gratuito Oficial', 'Certificado con Costo', o 'Sin Certificación'",
      "bolivia_eligible": "Una de: ['Sí', 'Parcial', 'No'] (acceso y validez desde Bolivia)",
      "bolivia_details": "Detalle sobre elegibilidad, pagos o restricciones en Bolivia",
      "user_custom_analysis": "Respuesta directa y detallada a la pregunta específica del usuario (si la formuló)"
    }
    """
    
    user_content = f"Enlace: {url}\nTítulo extraído: {meta.get('title')}\nDescripción/Contexto: {meta.get('description')}\nPlataforma: {meta.get('platform')}\n"
    if custom_prompt:
        user_content += f"\nPREGUNTA ESPECÍFICA DEL USUARIO: {custom_prompt}\n"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": system_instruction},
                {"text": user_content}
            ]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }
    
    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                raw_text = result['candidates'][0]['content']['parts'][0]['text']
                data = json.loads(raw_text)
                return data
    except Exception as e:
        print(f"Error consultando Gemini API: {e}")
        return None

def analyze_with_heuristics(url: str, meta: Dict[str, Any], custom_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Motor heurístico offline de respaldo: analiza y categoriza con alta precisión según bases de conocimiento tecnológicas."""
    clean_url = clean_direct_url(url)
    lower_url = clean_url.lower()
    title = meta.get("title", "")
    desc = meta.get("description", "").lower()
    
    # Detección de entidades reconocidas
    direct_link = clean_url
    category = "Herramientas & Productividad"
    emp_index = 75
    emp_details = "Herramienta con demanda positiva en flujos de trabajo profesionales y de productividad."
    has_cert = "Sin Certificación"
    bolivia_ok = "Sí"
    bol_details = "100% accesible vía web desde Bolivia sin restricciones de región."
    what_it_does = "Recurso digital enfocado en desarrollo de habilidades, productividad o flujos de trabajo."
    how_it_helps = "Aporta conocimientos prácticos y optimización de tiempo aplicables a proyectos técnicos e industriales."
    
    # 1. Educación / Cursos de Alta Gama
    if any(k in lower_url or k in desc for k in ['harvard', 'cs50', 'edx.org', 'coursera.org', 'mit.edu', 'stanford']):
        category = "Cursos & Certificaciones"
        emp_index = 95
        emp_details = "Reconocimiento global máximo por reclutadores internacionales y base sólida de ciencias de la computación."
        has_cert = "Certificado Oficial (Auditoría Gratuita disponible)"
        what_it_does = "Formación académica de élite en fundamentos computacionales y ciencias aplicadas."
        how_it_helps = "Diferenciador curricular de primer nivel para postular a pasantías y empleos remotos en USD."
    elif any(k in lower_url or k in desc for k in ['google', 'grow.google', 'deeplearning.ai', 'microsoft', 'aws', 'amazon', 'nvidia']):
        category = "Cursos & Certificaciones"
        emp_index = 92
        emp_details = "Certificaciones tecnológicas corporativas de alta demanda y relevancia directa en la industria moderna."
        has_cert = "Certificado Oficial Profesional"
        what_it_does = "Especialización tecnológica validada por los mayores proveedores de infraestructura del mundo."
        how_it_helps = "Alinea tu perfil de Ingeniería Industrial con la nube, analítica y computación empresarial."
    # 2. IA y Automatización
    elif any(k in lower_url or k in desc for k in ['n8n', 'zapier', 'make.com', 'huggingface', 'openai', 'anthropic', 'claude', 'langchain']):
        category = "Inteligencia Artificial"
        emp_index = 90
        emp_details = "La automatización de procesos con IA es la habilidad de mayor crecimiento en optimización industrial."
        what_it_does = "Plataforma de automatización de flujos de trabajo y desarrollo con modelos de inteligencia artificial."
        how_it_helps = "Permite automatizar procesos operativos reduciendo horas hombre, núcleo de la ingeniería industrial 4.0."
    # 3. Finanzas e Inversión
    elif any(k in lower_url or k in desc for k in ['fire', 'inversion', 'interactive brokers', 'ibkr', 'etf', 'vanguard', 'bolsa']):
        category = "Finanzas & Inversión"
        emp_index = 80
        emp_details = "Habilidad de gestión de capital y finanzas corporativas/personales sistemáticas."
        what_it_does = "Educación y herramientas de gestión financiera, interés compuesto e inversión pasiva indexada."
        how_it_helps = "Permite construir independencia financiera y aplicar modelos cuantitativos a tu patrimonio."
    # 4. Programación y Datos
    elif any(k in lower_url or k in desc for k in ['github', 'python', 'kaggle', 'sql', 'pandas', 'tableau', 'powerbi']):
        category = "Programación & Data"
        emp_index = 88
        emp_details = "El análisis de datos con Python y SQL es el estándar de la industria para optimización de operaciones."
        what_it_does = "Entorno y recursos para programación técnica, análisis exploratorio de datos y modelos estadísticos."
        how_it_helps = "Sinergia directa con materias de la UMSA (IND-312 Informática, IND-521 Econometría, IND-532 Calidad)."

    # Respuesta personalizada si el usuario formuló una pregunta
    user_custom = ""
    if custom_prompt:
        user_custom = (
            f"Evaluación personalizada para: '{custom_prompt}':\n"
            f"- Este recurso pertenece al área de {category}.\n"
            f"- Desde el marco de optimización de InvernovAH, te otorga un retorno estimado del {emp_index}% en empleabilidad, "
            f"apoyando tu preparación tanto para materias cuantitativas de la UMSA como para el mercado laboral internacional."
        )

    return {
        "title": title or f"Recurso ({category})",
        "direct_url": direct_link,
        "category": category,
        "author": meta.get("author", "Especialista Tech"),
        "ai_what_it_does": what_it_does,
        "ai_how_it_helps": how_it_helps,
        "employability_index": emp_index,
        "employability_details": emp_details,
        "has_certification": has_cert,
        "bolivia_eligible": bolivia_ok,
        "bolivia_details": bol_details,
        "user_custom_analysis": user_custom
    }

def analyze_url(url: str, custom_prompt: Optional[str] = None, gemini_api_key: Optional[str] = None) -> Dict[str, Any]:
    """Punto de entrada principal: analiza un enlace utilizando Gemini AI si está disponible, o el motor heurístico."""
    clean_url = clean_direct_url(url)
    meta = fetch_url_metadata(clean_url)
    
    # 1. Intentar con Gemini si hay API Key disponible
    ai_result = None
    if gemini_api_key:
        ai_result = analyze_with_gemini(clean_url, meta, custom_prompt, gemini_api_key)
        
    # 2. Si no hay Gemini o falló, usar motor heurístico avanzado
    if not ai_result:
        ai_result = analyze_with_heuristics(clean_url, meta, custom_prompt)
        
    # 3. Consolidar campos completos para la base de datos
    direct_link = clean_direct_url(ai_result.get("direct_url") or clean_url)
    parsed_direct = urllib.parse.urlparse(direct_link)
    domain = parsed_direct.netloc.replace("www.", "")
    path = parsed_direct.path.strip("/")
    canonical_key = f"{domain}:{path}" if path else domain
    
    return {
        "title": ai_result.get("title", meta.get("title", "Nuevo Recurso")),
        "url": clean_url,
        "post_url": clean_url if meta.get("is_video") else "",
        "direct_url": direct_link,
        "direct_url_clean": direct_link,
        "canonical_key": canonical_key,
        "canonical_name": ai_result.get("title", "Nuevo Recurso"),
        "category": ai_result.get("category", "Herramientas & Productividad"),
        "author": ai_result.get("author", meta.get("author", "Autor Desconocido")),
        "summary": ai_result.get("ai_what_it_does", meta.get("description", "")),
        "ai_what_it_does": ai_result.get("ai_what_it_does", ""),
        "ai_how_it_helps": ai_result.get("ai_how_it_helps", ""),
        "employability_index": int(ai_result.get("employability_index", 75)),
        "employability_details": ai_result.get("employability_details", ""),
        "has_certification": ai_result.get("has_certification", "Sin Certificación"),
        "recruiter_weight": "Alto" if int(ai_result.get("employability_index", 75)) >= 85 else "Medio",
        "bolivia_eligible": ai_result.get("bolivia_eligible", "Sí"),
        "bolivia_details": ai_result.get("bolivia_details", "Accesible vía web"),
        "found_by_ai": 1,
        "user_custom_analysis": ai_result.get("user_custom_analysis", "")
    }
