import sys
import os

# Ensure repository root is always in sys.path regardless of execution environment
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

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime, date

from src.ai.video_analyzer import analyze_url
from src.database.cloud_sync import export_db_to_json, sync_to_github
from src.database.dedup_engine import analyze_against_db, format_mixed_markdown

# Page Config
st.set_page_config(
    page_title="NEXUS Life OS | InvernovAH",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database path with automatic self-healing initialization
DB_PATH = os.path.join(ROOT_DIR, "data", "nexus.db")
JSON_PATH = os.path.join(ROOT_DIR, "data", "instagram_resources.json")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH):
        try:
            from src.database.db_manager import init_db
            init_db()
        except Exception as e:
            print(f"Warning: init_db encountered: {e}")
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_secret(key, default=""):
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
        return os.environ.get(key, default)
    except Exception:
        return os.environ.get(key, default)

# ------------------------------------------------------------
# DEFENSIVE TYPE-SAFETY HELPERS
# ------------------------------------------------------------
def safe_int(v, default=0):
    try:
        if v is None or pd.isna(v):
            return default
        if isinstance(v, str):
            clean = re.sub(r'[^\d.]', '', v)
            if not clean:
                return default
            return int(float(clean))
        return int(float(v))
    except Exception:
        return default

def safe_float(v, default=0.0):
    try:
        if v is None or pd.isna(v):
            return default
        if isinstance(v, str):
            clean = re.sub(r'[^\d.]', '', v)
            if not clean:
                return default
            return float(clean)
        return float(v)
    except Exception:
        return default

def safe_str(v, default=""):
    if v is None or pd.isna(v):
        return default
    return str(v).strip()

# Clean, modern CSS styling
st.markdown("""
<style>
    .resource-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11.5px;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-dup { background-color: #fef3c7; color: #92400e; border: 1px solid #f59e0b; }
    .badge-ai { background-color: #e0f2fe; color: #0369a1; border: 1px solid #38bdf8; }
    .badge-bolivia-ok { background-color: #dcfce7; color: #166534; border: 1px solid #22c55e; }
    .badge-bolivia-warn { background-color: #fee2e2; color: #991b1b; border: 1px solid #ef4444; }
    .box-what {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin: 8px 0;
        font-size: 13.5px;
        color: #1e293b;
    }
    .box-how {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin: 8px 0;
        font-size: 13.5px;
        color: #064e3b;
    }
    .box-custom {
        background-color: #faf5ff;
        border-left: 4px solid #a855f7;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin: 8px 0;
        font-size: 13.5px;
        color: #581c87;
    }
    .direct-link-btn {
        display: inline-block;
        background-color: #16a34a;
        color: #ffffff !important;
        font-weight: 700;
        padding: 7px 14px;
        border-radius: 6px;
        text-decoration: none !important;
        font-size: 13px;
        margin-top: 4px;
        margin-right: 8px;
    }
    .post-link-btn {
        display: inline-block;
        background-color: #f1f5f9;
        color: #475569 !important;
        font-weight: 500;
        padding: 7px 12px;
        border-radius: 6px;
        text-decoration: none !important;
        font-size: 13px;
        border: 1px solid #cbd5e1;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Detect API Status
gemini_key = get_secret("GEMINI_API_KEY")
github_token = get_secret("GITHUB_TOKEN")

conn = get_db()
cur = conn.cursor()

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.title("🧠 NEXUS Life OS")
    st.markdown("**Usuario:** Mark Hazard (`@Mark020226`)")
    st.markdown("**Enfoque:** 🇧🇴 UMSA Ing. Industrial | Filosofía InvernovAH")
    st.markdown("---")
    
    # Cloud AI Status indicator
    if gemini_key:
        st.success("🟢 **Google Gemini AI:** Conectado")
    else:
        st.info("⚡ **Motor IA:** Heurístico Activo\n*(Añade `GEMINI_API_KEY` en Secrets para potenciar)*")
        
    if github_token:
        st.success("☁️ **Auto-Sync GitHub:** Activo")
    else:
        st.caption("💡 Respaldo local JSON automático activo.")
        
    st.markdown("---")
    st.markdown("### 🔍 Filtros Globales de Recursos")
    filter_dup = st.checkbox("⚠️ Solo recursos repetidos", value=False)
    filter_mixed = st.checkbox("📦 Solo publicaciones compuestas", value=False)
    filter_high_emp = st.checkbox("🔥 Solo Alta Empleabilidad (>= 85%)", value=False)
    filter_cert = st.checkbox("📜 Solo con Certificación Oficial", value=False)
    filter_bolivia = st.checkbox("🇧🇴 Solo 100% elegibles en Bolivia", value=False)
    st.markdown("---")
    st.caption("NEXUS v3.2 — Ingeniería Personal & FIRE.")

# Top KPIs Bar
cur.execute("SELECT COUNT(*) FROM resources")
total_res = safe_int(cur.fetchone()[0], 0)
cur.execute("SELECT COUNT(*) FROM resources WHERE is_duplicate = 1")
dup_res_count = safe_int(cur.fetchone()[0], 0)
cur.execute("SELECT COUNT(*) FROM resources WHERE CAST(employability_index AS INTEGER) >= 85")
high_employability_count = safe_int(cur.fetchone()[0], 0)
cur.execute("SELECT COUNT(*) FROM resources WHERE has_certification LIKE '%Certificado%'")
cert_count = safe_int(cur.fetchone()[0], 0)

col_k1, col_k2, col_k3, col_k4 = st.columns(4)
with col_k1:
    st.metric("💡 Recursos en Memoria", f"{total_res}", "Segundo Cerebro Activo")
with col_k2:
    st.metric("🔥 Alta Empleabilidad", f"{high_employability_count}", "Validado por Industria Tech")
with col_k3:
    st.metric("📜 Con Certificación", f"{cert_count}", "Oficial y Verificable")
with col_k4:
    st.metric("🔁 Duplicados Filtrados", f"{dup_res_count}", "Cero Ruido")

st.markdown("---")

# ------------------------------------------------------------
# MAIN TABS (INVERNOVAH ARCHITECTURE)
# ------------------------------------------------------------
tab_brain, tab_nasa, tab_lotus, tab_fire, tab_umsa = st.tabs([
    "💡 Segundo Cerebro & Clasificador IA",
    "🚀 Planificación Diaria NASA (3 Hojas)",
    "🌸 Matriz Flor de Loto (8x8 Matsumura)",
    "💰 Finanzas Personales & FIRE",
    "🎓 Malla UMSA & Informática MIT"
])

# ============================================================
# TAB 1: SEGUNDO CEREBRO & CLASIFICADOR IA
# ============================================================
with tab_brain:
    st.subheader("💡 Segundo Cerebro Inteligente: Gestión Dinámica de Recursos")
    st.markdown(
        "Agrega o quita enlaces de videos, reels o herramientas. La **IA extrae automáticamente el enlace directo al recurso real**, "
        "calcula el índice objetivo de empleabilidad y responde tus preguntas a demanda."
    )
    
    # Formulario Expandible para Agregar Enlace
    with st.expander("➕ **Agregar Nuevo Recurso / Video con Clasificación IA**", expanded=False):
        col_in1, col_in2 = st.columns([2, 1])
        with col_in1:
            new_url = st.text_input("🔗 Enlace del Video o Recurso:", placeholder="https://www.youtube.com/watch?v=... o https://instagram.com/reel/...")
            user_question = st.text_input("❓ ¿Qué quieres que la IA evalúe o extraiga de este video/enlace? (Opcional):", 
                                         placeholder="Ej: ¿Sirve para conseguir empleo en USD sin título? / ¿Cómo se relaciona con IND-312?")
        with col_in2:
            st.markdown("<br>", unsafe_allow_html=True)
            submit_analyze = st.button("🚀 Analizar, Clasificar y Guardar", use_container_width=True, type="primary")

        if submit_analyze:
            if not new_url or not new_url.strip():
                st.error("Por favor ingresa un enlace válido.")
            else:
                with st.spinner("🧠 Analizando metadatos, verificando duplicados y clasificando con IA..."):
                    # 1. Comprobación de duplicados
                    dedup_check = analyze_against_db(cur, user_question or "", new_url.strip(), new_url.strip())
                    
                    if dedup_check["status"] == "PURE_DUPLICATE":
                        st.warning(f"⚠️ **Recurso ya existente:** {dedup_check['reason']}")
                    else:
                        # 2. Análisis con IA (Gemini o Heurístico)
                        ai_data = analyze_url(new_url.strip(), user_question, gemini_key)
                        
                        # Si es compuesto, formatear listas
                        new_md = ""
                        rep_md = ""
                        has_mixed = 0
                        if dedup_check["status"] == "MIXED":
                            has_mixed = 1
                            new_md, rep_md = format_mixed_markdown(dedup_check["new_resources"], dedup_check["repeated_resources"])
                        
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        # 3. Guardar en SQLite
                        cur.execute("""
                        INSERT INTO resources (
                            url, direct_url, direct_url_clean, post_url, canonical_key, canonical_name,
                            title, summary, ai_what_it_does, ai_how_it_helps, employability_index,
                            employability_details, has_certification, recruiter_weight, bolivia_eligible,
                            bolivia_details, category, date_added, source, author, status,
                            has_mixed_resources, new_resources_list, repeated_resources_list,
                            user_custom_analysis, found_by_ai
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            ai_data["url"], ai_data["direct_url"], ai_data["direct_url_clean"],
                            ai_data["post_url"], ai_data["canonical_key"], ai_data["canonical_name"],
                            ai_data["title"], ai_data["summary"], ai_data["ai_what_it_does"],
                            ai_data["ai_how_it_helps"], ai_data["employability_index"],
                            ai_data["employability_details"], ai_data["has_certification"],
                            ai_data["recruiter_weight"], ai_data["bolivia_eligible"],
                            ai_data["bolivia_details"], ai_data["category"], now_str,
                            "Entrada de Usuario con IA", ai_data["author"], "Guardado",
                            has_mixed, new_md, rep_md, ai_data.get("user_custom_analysis", ""), 1
                        ))
                        conn.commit()
                        
                        # 4. Sincronización en la nube
                        export_db_to_json(DB_PATH, JSON_PATH)
                        if github_token:
                            sync_to_github(DB_PATH, token=github_token)
                            sync_to_github(JSON_PATH, token=github_token)
                            
                        st.success(f"✅ ¡Recurso catalogado exitosamente! Empleabilidad estimada: **{ai_data['employability_index']}%**")
                        st.rerun()

    # Buscador y Selector de Categorías
    col_search, col_cat = st.columns([2, 1])
    cur.execute("SELECT DISTINCT category FROM resources WHERE category IS NOT NULL AND category != '' ORDER BY category")
    categories = [r[0] for r in cur.fetchall()]
    
    with col_search:
        search_query = st.text_input("🔍 Buscar por herramienta, curso, habilidad o tecnología (ej. CS50, Python, n8n, Harvard, AWS, SQL):", "")
    with col_cat:
        cat_filter = st.selectbox("Categoría:", ["Todas"] + categories)

    # Construcción de la consulta con filtros
    query = """
    SELECT id, title, category, author, date_added, url, post_url, direct_url_clean,
           ai_what_it_does, ai_how_it_helps, employability_index, employability_details,
           has_certification, recruiter_weight, bolivia_eligible, bolivia_details,
           is_duplicate, duplicate_count, duplicate_sources, found_by_ai, summary,
           has_mixed_resources, new_resources_list, repeated_resources_list, user_custom_analysis
    FROM resources
    WHERE 1=1
    """
    params = []
    
    if search_query:
        query += " AND (title LIKE ? OR summary LIKE ? OR ai_what_it_does LIKE ? OR ai_how_it_helps LIKE ? OR direct_url_clean LIKE ?)"
        term = f"%{search_query}%"
        params.extend([term, term, term, term, term])
        
    if cat_filter != "Todas":
        query += " AND category = ?"
        params.append(cat_filter)
        
    if filter_dup:
        query += " AND is_duplicate = 1"
    if filter_mixed:
        query += " AND has_mixed_resources = 1"
    if filter_high_emp:
        query += " AND CAST(employability_index AS INTEGER) >= 85"
    if filter_cert:
        query += " AND has_certification LIKE '%Certificado%'"
    if filter_bolivia:
        query += " AND (bolivia_eligible = 'Sí' OR bolivia_eligible LIKE '%100%')"
        
    query += " ORDER BY id DESC"
    
    cur.execute(query, params)
    resources = cur.fetchall()
    
    # Manejo de borrado si se solicitó en sesión
    if "resource_to_delete" in st.session_state and st.session_state["resource_to_delete"] is not None:
        del_id = st.session_state["resource_to_delete"]
        cur.execute("DELETE FROM resources WHERE id = ?", (del_id,))
        conn.commit()
        export_db_to_json(DB_PATH, JSON_PATH)
        if github_token:
            sync_to_github(DB_PATH, token=github_token)
        st.session_state["resource_to_delete"] = None
        st.success("🗑️ Recurso eliminado correctamente.")
        st.rerun()

    # Paginación Dinámica
    total_found = len(resources)
    st.markdown(f"**Mostrando {total_found} recursos encontrados**")
    
    col_page, col_size = st.columns([3, 1])
    with col_size:
        page_size_option = st.selectbox("Elementos por página:", [25, 50, 100, "Ver Todos"], index=0)
    
    if page_size_option == "Ver Todos":
        page_size = max(1, total_found)
        total_pages = 1
        page_num = 1
    else:
        page_size = int(page_size_option)
        total_pages = max(1, (total_found + page_size - 1) // page_size)
        with col_page:
            page_num = st.number_input(f"Página (1 de {total_pages}):", min_value=1, max_value=total_pages, value=1)
            
    start_idx = (page_num - 1) * page_size
    end_idx = min(start_idx + page_size, total_found)
    paged_resources = resources[start_idx:end_idx]

    # Renderizado de Tarjetas de Recursos
    for row in paged_resources:
        r_id = row['id']
        r_title = safe_str(row['title'], "Recurso")
        r_cat = safe_str(row['category'], "General")
        r_author = safe_str(row['author'], "Desconocido")
        r_direct = safe_str(row['direct_url_clean']) or safe_str(row['url'])
        r_post = safe_str(row['post_url'])
        r_what = safe_str(row['ai_what_it_does']) or safe_str(row['summary'])
        r_how = safe_str(row['ai_how_it_helps'])
        r_emp = safe_int(row['employability_index'], 70)
        r_emp_det = safe_str(row['employability_details'])
        r_cert = safe_str(row['has_certification'], "Sin Certificación")
        r_bolivia = safe_str(row['bolivia_eligible'], "Sí")
        r_bol_det = safe_str(row['bolivia_details'])
        r_custom = safe_str(row['user_custom_analysis'])
        r_is_dup = safe_int(row['is_duplicate'], 0) == 1
        r_dup_cnt = safe_int(row['duplicate_count'], 1)
        r_dup_src = safe_str(row['duplicate_sources'])
        r_mixed = safe_int(row['has_mixed_resources'], 0) == 1
        r_new_list = safe_str(row['new_resources_list'])
        r_rep_list = safe_str(row['repeated_resources_list'])
        
        # Color del índice de empleabilidad
        emp_color = "#16a34a" if r_emp >= 85 else ("#ca8a04" if r_emp >= 70 else "#dc2626")

        with st.container():
            st.markdown(f"""
            <div class="resource-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h4 style="margin: 0 0 6px 0; color: #0f172a;">{r_title}</h4>
                        <span class="badge" style="background-color: #f1f5f9; color: #334155; border: 1px solid #cbd5e1;">📁 {r_cat}</span>
                        <span class="badge" style="background-color: {emp_color}15; color: {emp_color}; border: 1px solid {emp_color};">🔥 Empleabilidad: {r_emp}%</span>
                        <span class="badge badge-ai">📜 {r_cert}</span>
                        <span class="badge {'badge-bolivia-ok' if 'Sí' in r_bolivia or '100%' in r_bolivia else 'badge-bolivia-warn'}">🇧🇴 {r_bolivia}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if r_is_dup:
                st.markdown(f"""
                <div style="background-color: #fffbeb; border: 1px solid #fef3c7; padding: 8px 12px; border-radius: 6px; margin: 8px 0; font-size: 13px; color: #92400e;">
                    ⚠️ <b>Recurso Repetido / Multi-mencionado ({r_dup_cnt} veces):</b> {r_dup_src or 'Ha aparecido en múltiples videos guardados.'}
                </div>
                """, unsafe_allow_html=True)
                
            if r_what:
                st.markdown(f'<div class="box-what"><b>💡 ¿Qué es / Qué hace?</b><br>{r_what}</div>', unsafe_allow_html=True)
            if r_how:
                st.markdown(f'<div class="box-how"><b>🚀 ¿Cómo te aporta a tu carrera y metas?</b><br>{r_how}</div>', unsafe_allow_html=True)
            if r_custom:
                st.markdown(f'<div class="box-custom"><b>💬 Respuesta de la IA a tu consulta:</b><br>{r_custom}</div>', unsafe_allow_html=True)
                
            if r_mixed:
                if r_new_list:
                    st.markdown(f"**🟢 Recursos Nuevos descubiertos en esta publicación:**\n\n{r_new_list}")
                if r_rep_list:
                    st.markdown(f"**⚠️ Recursos ya conocidos en esta publicación:**\n\n{r_rep_list}")

            col_btn1, col_btn2, col_del = st.columns([2, 2, 1])
            with col_btn1:
                if r_direct:
                    st.markdown(f'<a href="{r_direct}" target="_blank" class="direct-link-btn">🚀 Ir al Recurso Real Directo</a>', unsafe_allow_html=True)
            with col_btn2:
                if r_post and r_post != r_direct:
                    st.markdown(f'<a href="{r_post}" target="_blank" class="post-link-btn">📱 Ver Video / Post Original</a>', unsafe_allow_html=True)
            with col_del:
                with st.popover("🗑️ Quitar", use_container_width=True):
                    st.write(f"¿Eliminar '{r_title[:35]}...'?")
                    if st.button("Confirmar Borrado", key=f"del_confirm_{r_id}", type="primary"):
                        st.session_state["resource_to_delete"] = r_id
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# TAB 2: PLANIFICACIÓN DIARIA NASA (SISTEMA DE 3 HOJAS - INVERNOVAH)
# ============================================================
with tab_nasa:
    st.subheader("🚀 Sistema de Productividad de 3 Hojas (Metodología NASA & InvernovAH)")
    st.markdown(
        "Álvaro Hernández adapta los protocolos aeroespaciales de la NASA a la ingeniería personal: "
        "*'No se inicia el día sin una lista de pre-vuelo clara y medible'*. Divide tu vida en 3 niveles de abstracción:"
    )
    
    subtab_h1, subtab_h2, subtab_h3 = st.tabs([
        "📄 Hoja 1: Macro-Visión & OKRs",
        "📊 Hoja 2: Hábitos & Energía Diaria",
        "📋 Hoja 3: Checklist Pre-Vuelo Diario NASA"
    ])
    
    # ------------------ HOJA 1: MACRO-VISIÓN ------------------
    with subtab_h1:
        st.markdown("#### 🎯 Hoja 1: Visión de Alto Nivel y Metas Trimestrales (OKRs)")
        st.caption("Los 3 grandes objetivos estratégicos que rigen tus decisiones semanales:")
        
        col_okr1, col_okr2, col_okr3 = st.columns(3)
        with col_okr1:
            st.markdown("""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
                <h4 style="color:#1e40af; margin-top:0;">🎓 1. Excelencia UMSA</h4>
                <p style="font-size:13px; color:#475569;">Aprobar el 3er semestre de Ing. Industrial con promedio > 75 y dominar Informática (IND-312) y Probabilidades (IND-311).</p>
                <div style="background:#e2e8f0; border-radius:10px; height:12px; margin-top:10px;">
                    <div style="background:#3b82f6; height:12px; border-radius:10px; width:70%;"></div>
                </div>
                <p style="font-size:12px; font-weight:600; margin-top:4px; text-align:right;">Avance: 70%</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_okr2:
            st.markdown("""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
                <h4 style="color:#065f46; margin-top:0;">💻 2. Empleo Remoto Tech en USD</h4>
                <p style="font-size:13px; color:#475569;">Desarrollar portafolio en GitHub de automatización con Python, n8n y análisis de datos para ofertas remotas de $1,500 - $3,000 USD/mes.</p>
                <div style="background:#e2e8f0; border-radius:10px; height:12px; margin-top:10px;">
                    <div style="background:#10b981; height:12px; border-radius:10px; width:60%;"></div>
                </div>
                <p style="font-size:12px; font-weight:600; margin-top:4px; text-align:right;">Avance: 60%</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_okr3:
            st.markdown("""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px;">
                <h4 style="color:#854d0e; margin-top:0;">💰 3. Independencia Financiera (FIRE)</h4>
                <p style="font-size:13px; color:#475569;">Construir fondo de emergencia de 6 meses de gastos y aportar sistemáticamente a fondos indexados globales (S&P 500 / VWCE).</p>
                <div style="background:#e2e8f0; border-radius:10px; height:12px; margin-top:10px;">
                    <div style="background:#f59e0b; height:12px; border-radius:10px; width:45%;"></div>
                </div>
                <p style="font-size:12px; font-weight:600; margin-top:4px; text-align:right;">Avance: 45%</p>
            </div>
            """, unsafe_allow_html=True)

    # ------------------ HOJA 2: HÁBITOS & ENERGÍA ------------------
    with subtab_h2:
        st.markdown("#### ⚡ Hoja 2: Gráfico de Control Estadístico de Hábitos & Energía (Método Shewhart)")
        st.caption("Registra tu combustible biológico diario para correlacionar descanso con rendimiento:")
        
        with st.form("nasa_metric_form"):
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            with col_m1:
                in_date = st.date_input("Fecha:", date.today())
            with col_m2:
                in_sleep = st.number_input("Horas de Sueño:", min_value=0.0, max_value=16.0, value=7.5, step=0.5)
            with col_m3:
                in_energy = st.slider("Nivel de Energía (1-10):", 1, 10, 8)
            with col_m4:
                in_deep = st.number_input("Deep Work (Horas):", min_value=0.0, max_value=16.0, value=4.5, step=0.5)
            with col_m5:
                in_mood = st.slider("Estado de Ánimo (1-10):", 1, 10, 8)
                
            in_notes = st.text_input("Notas / Aprendizajes del día:", placeholder="Sesión productiva de programación y clases UMSA...")
            submit_m = st.form_submit_button("💾 Guardar Registro Diario", type="primary")
            
            if submit_m:
                cur.execute("""
                INSERT OR REPLACE INTO daily_metrics (date, sleep_hours, energy_level, mood, productive_hours, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (str(in_date), in_sleep, in_energy, in_mood, in_deep, in_notes))
                conn.commit()
                st.success("¡Registro de energía y hábitos guardado!")
                st.rerun()

        # Visualización de Tendencia de Energía vs Sueño
        df_metrics = pd.read_sql_query("SELECT * FROM daily_metrics ORDER BY date", conn)
        if not df_metrics.empty:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=df_metrics['date'], y=df_metrics['sleep_hours'], mode='lines+markers', name='Horas de Sueño', line=dict(color='#3b82f6', width=3)))
            fig_trend.add_trace(go.Scatter(x=df_metrics['date'], y=df_metrics['energy_level'], mode='lines+markers', name='Energía (1-10)', line=dict(color='#10b981', width=3)))
            fig_trend.add_trace(go.Scatter(x=df_metrics['date'], y=df_metrics['productive_hours'], mode='lines+markers', name='Deep Work (h)', line=dict(color='#f59e0b', width=2, dash='dot')))
            fig_trend.update_layout(title="Correlación: Horas de Sueño vs Nivel de Energía y Deep Work", xaxis_title="Fecha", yaxis_title="Escala / Horas", hovermode="x unified")
            st.plotly_chart(fig_trend, use_container_width=True)

    # ------------------ HOJA 3: CHECKLIST PRE-VUELO NASA ------------------
    with subtab_h3:
        st.markdown("#### 📋 Hoja 3: Checklist Pre-Vuelo Diario NASA")
        st.markdown(
            "> **Principio de Álvaro Hernández:** *'En la NASA, un cohete jamás despega con pendientes en su checklist. "
            "Elige un máximo de 3 tareas no negociables al día. Si las cumples, el día fue un éxito total.'*"
        )
        
        today_str = str(date.today())
        
        # Formulario para añadir tarea pre-vuelo
        with st.form("add_nasa_task"):
            col_t1, col_t2 = st.columns([3, 1])
            with col_t1:
                task_txt = st.text_input("Nueva tarea crítica no negociable para hoy:", placeholder="Ej: Resolver laboratorio IND-312 de algoritmos en Python")
            with col_t2:
                task_crit = st.checkbox("🔥 ¿Es una de las TOP 3 Críticas?", value=True)
            submit_task = st.form_submit_button("➕ Añadir a la Lista de Despegue")
            
            if submit_task and task_txt.strip():
                cur.execute("""
                INSERT INTO nasa_tasks (date, step_number, task_description, is_critical, completed, time_estimate_min)
                VALUES (?, 1, ?, ?, 0, 45)
                """, (today_str, task_txt.strip(), 1 if task_crit else 0))
                conn.commit()
                st.success("Tarea pre-vuelo añadida.")
                st.rerun()

        # Listado de Tareas Pre-vuelo de Hoy
        cur.execute("SELECT id, task_description, is_critical, completed FROM nasa_tasks WHERE date = ? ORDER BY is_critical DESC, id ASC", (today_str,))
        today_tasks = cur.fetchall()
        
        if today_tasks:
            st.markdown(f"**Lista de Despegue para Hoy ({today_str}):**")
            for t in today_tasks:
                t_id, t_desc, t_crit, t_comp = t[0], t[1], t[2], t[3]
                col_chk, col_desc, col_act = st.columns([0.5, 4, 1])
                
                with col_chk:
                    is_done = st.checkbox("", value=bool(t_comp), key=f"nasa_chk_{t_id}")
                    if is_done != bool(t_comp):
                        cur.execute("UPDATE nasa_tasks SET completed = ? WHERE id = ?", (1 if is_done else 0, t_id))
                        conn.commit()
                        st.rerun()
                        
                with col_desc:
                    prefix = "🔥 **[CRÍTICA TOP 3]** " if t_crit else "⚡ "
                    if t_comp:
                        st.markdown(f"~~{prefix}{t_desc}~~ ✅")
                    else:
                        st.markdown(f"{prefix}{t_desc}")
                        
                with col_act:
                    if st.button("🗑️", key=f"del_task_{t_id}", help="Eliminar tarea"):
                        cur.execute("DELETE FROM nasa_tasks WHERE id = ?", (t_id,))
                        conn.commit()
                        st.rerun()
        else:
            st.info("No tienes tareas pre-vuelo registradas para hoy. Define tus 3 prioridades no negociables en el formulario superior.")

# ============================================================
# TAB 3: MATRIZ FLOR DE LOTO (LOTUS BLOSSOM 8x8 - MATSUMURA)
# ============================================================
with tab_lotus:
    st.subheader("🌸 Matriz Flor de Loto (Matsumura 8x8 Matrix)")
    st.markdown(
        "La metodología de la **Flor de Loto (Lotus Blossom)**, popularizada por Yasuo Matsumura y recomendada por **InvernovAH**, "
        "descompone un macro-objetivo central en **8 pilares estratégicos**, y cada pilar en **8 micro-acciones concretas** (64 acciones en total)."
    )
    
    st.info("🎯 **META CENTRAL:** **Graduación con Honores en Ingeniería Industrial UMSA + Empleo Remoto Tech en USD ($2,500+/mes)**")

    # Pilares de la Flor de Loto
    cur.execute("SELECT DISTINCT pillar_id, pillar_name FROM lotus_blossom ORDER BY pillar_id")
    pillars = cur.fetchall()
    
    pillar_names = [p[1] for p in pillars]
    selected_pillar_name = st.selectbox("Selecciona un Pilar Estratégico para ver o actualizar sus 8 Micro-Acciones:", pillar_names)
    selected_pillar_id = [p[0] for p in pillars if p[1] == selected_pillar_name][0]
    
    # Progreso Global del Pilar Seleccionado
    cur.execute("SELECT status, COUNT(*) FROM lotus_blossom WHERE pillar_id = ? GROUP BY status", (selected_pillar_id,))
    status_counts = dict(cur.fetchall())
    comp_p = status_counts.get("Completada", 0)
    prog_p = status_counts.get("En Progreso", 0)
    pend_p = status_counts.get("Pendiente", 0)
    total_p = comp_p + prog_p + pend_p
    progress_val = int((comp_p / max(1, total_p)) * 100)
    
    col_prog1, col_prog2, col_prog3, col_prog4 = st.columns(4)
    with col_prog1:
        st.metric("Completadas", f"{comp_p} / {total_p}")
    with col_prog2:
        st.metric("En Progreso", f"{prog_p}")
    with col_prog3:
        st.metric("Pendientes", f"{pend_p}")
    with col_prog4:
        st.metric("Avance del Pilar", f"{progress_val}%")
        
    st.progress(progress_val / 100.0)
    st.markdown("---")

    # Listado interactivo de las 8 micro-acciones del pilar
    cur.execute("SELECT id, micro_task_num, action_title, status FROM lotus_blossom WHERE pillar_id = ? ORDER BY micro_task_num", (selected_pillar_id,))
    actions = cur.fetchall()
    
    for act in actions:
        a_id, a_num, a_title, a_status = act[0], act[1], act[2], act[3]
        col_num, col_t, col_st = st.columns([0.6, 3.4, 1.2])
        
        with col_num:
            st.markdown(f"**{selected_pillar_id}.{a_num}**")
        with col_t:
            st.markdown(f"{a_title}")
        with col_st:
            new_st = st.selectbox(
                "",
                ["Pendiente", "En Progreso", "Completada"],
                index=["Pendiente", "En Progreso", "Completada"].index(a_status),
                key=f"lotus_st_{a_id}",
                label_visibility="collapsed"
            )
            if new_st != a_status:
                cur.execute("UPDATE lotus_blossom SET status = ? WHERE id = ?", (new_st, a_id))
                conn.commit()
                st.rerun()

# ============================================================
# TAB 4: FINANZAS PERSONALES & FIRE (INVERNOVAH)
# ============================================================
with tab_fire:
    st.subheader("💰 Ingeniería Financiera & Filosofía FIRE (InvernovAH)")
    st.markdown(
        "Álvaro Hernández aplica la ingeniería a las finanzas: "
        "*'La libertad financiera no es cuánto ganas, sino qué porcentaje de tus ingresos conviertes sistemáticamente en activos productivos (Tasa de Ahorro)'*."
    )
    
    # Cálculo de métricas financieras desde la base de datos
    cur.execute("SELECT type, SUM(amount) FROM finance_transactions GROUP BY type")
    fin_sums = dict(cur.fetchall())
    total_income = fin_sums.get("Ingreso", 0.0)
    total_fixed_exp = fin_sums.get("Gasto Fijo", 0.0)
    total_opt_exp = fin_sums.get("Gasto Opcional", 0.0) + fin_sums.get("Gasto", 0.0)
    total_savings = fin_sums.get("Ahorro / Inversión", 0.0)
    total_expenses = total_fixed_exp + total_opt_exp
    
    # Métricas FIRE Estrella
    savings_rate = (total_savings / max(1.0, total_income)) * 100.0 if total_income > 0 else 0.0
    emergency_fund_months = (total_savings * 2.5) / max(1.0, total_expenses) if total_expenses > 0 else 0.0
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        st.metric("💵 Ingresos Registrados", f"${total_income:,.0f} USD")
    with col_f2:
        st.metric("📉 Gastos Totales", f"${total_expenses:,.0f} USD")
    with col_f3:
        rate_color = "normal" if savings_rate >= 40 else "off"
        st.metric("📈 Tasa de Ahorro (FIRE)", f"{savings_rate:.1f}%", "Meta InvernovAH: > 40%")
    with col_f4:
        st.metric("🛡️ Colchón de Emergencia", f"{emergency_fund_months:.1f} Meses", "Meta: 6 Meses de Runway")
        
    st.markdown("---")
    
    # Simulador de Interés Compuesto Pasivo (S&P 500 / MSCI World)
    st.markdown("### 📈 Simulador de Libertad Financiera e Inversión Pasiva Indexada")
    st.caption("Proyección matemática basada en el rendimiento histórico promedio del 8% anual (S&P 500 / Globales vía IBKR):")
    
    col_sim1, col_sim2 = st.columns([1, 2])
    with col_sim1:
        sim_monthly = st.slider("Aporte Mensual (USD):", 50, 1500, 250, step=25)
        sim_years = st.slider("Horizonte de Inversión (Años):", 5, 30, 15)
        sim_rate = st.slider("Rentabilidad Anual Esperada (%):", 5.0, 12.0, 8.0, step=0.5)
        
        # Cálculo del interés compuesto
        r_month = (sim_rate / 100.0) / 12.0
        total_months = sim_years * 12
        
        months_list = list(range(1, total_months + 1))
        capital_invested = [sim_monthly * m for m in months_list]
        future_values = [sim_monthly * (((1 + r_month)**m - 1) / r_month) for m in months_list]
        compound_interest = [fv - inv for fv, inv in zip(future_values, capital_invested)]
        
        final_capital = capital_invested[-1]
        final_interest = compound_interest[-1]
        final_total = future_values[-1]
        
        st.markdown(f"""
        <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:14px; margin-top:10px;">
            <p style="margin:0; font-size:13px; color:#166534;">Patrimonio Proyectado:</p>
            <h3 style="margin:4px 0; color:#15803d;">${final_total:,.0f} USD</h3>
            <p style="margin:0; font-size:12px; color:#166534;">
                Capital Aportado: <b>${final_capital:,.0f} USD</b><br>
                Interés Ganado (Interés Compuesto): <b>${final_interest:,.0f} USD</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_sim2:
        df_sim = pd.DataFrame({
            "Año": [m / 12.0 for m in months_list],
            "Capital Aportado": capital_invested,
            "Interés Compuesto": compound_interest,
            "Patrimonio Total": future_values
        })
        fig_fire = px.area(df_sim, x="Año", y=["Capital Aportado", "Interés Compuesto"],
                           title="Curva Exponencial: Aporte de Capital vs Interés Compuesto",
                           color_discrete_sequence=['#3b82f6', '#10b981'])
        st.plotly_chart(fig_fire, use_container_width=True)

    # Formulario para registrar ingresos / gastos
    with st.expander("➕ **Registrar Transacción / Ingreso / Aporte de Ahorro**"):
        with st.form("add_transaction_form"):
            col_tr1, col_tr2, col_tr3 = st.columns(3)
            with col_tr1:
                t_type = st.selectbox("Tipo:", ["Gasto Fijo", "Gasto Opcional", "Ingreso", "Ahorro / Inversión"])
            with col_tr2:
                t_cat = st.selectbox("Categoría:", [
                    "Ingresos Principales / Remoto",
                    "Alquiler & Servicios",
                    "Alimentación Saludable",
                    "Transporte & Universidad UMSA",
                    "Suscripciones & Herramientas Tech",
                    "Fondo de Emergencia (Ahorro)",
                    "Inversión Indexada Pasiva (FIRE)"
                ])
            with col_tr3:
                t_amount = st.number_input("Monto en USD:", min_value=1.0, value=50.0, step=5.0)
                
            t_desc = st.text_input("Descripción de la transacción:", placeholder="Pago de servidor, curso, ahorro mensual...")
            sub_tr = st.form_submit_button("💾 Guardar Transacción", type="primary")
            
            if sub_tr:
                cur.execute("""
                INSERT INTO finance_transactions (date, type, category, amount, description)
                VALUES (?, ?, ?, ?, ?)
                """, (datetime.now().strftime("%Y-%m-%d"), t_type, t_cat, t_amount, t_desc))
                conn.commit()
                st.success("Transacción registrada.")
                st.rerun()

# ============================================================
# TAB 5: MALLA UMSA & MIT / HARVARD
# ============================================================
with tab_umsa:
    st.subheader("🎓 Malla Curricular UMSA (Ingeniería Industrial) & Equivalencias MIT / Harvard")
    st.markdown(
        "Planifica tu avance académico del plan 2015 de la UMSA y desbloquea equivalencias de computación "
        "de élite mundial para acelerar tu perfil hacia el trabajo remoto en tecnología."
    )
    
    df_courses = pd.read_sql_query("SELECT code, name, semester, status, grade, prereq FROM academic_courses ORDER BY semester, code", conn)
    
    col_sem_flt, col_sem_stat = st.columns([1, 2])
    with col_sem_flt:
        sem_selected = st.slider("Filtrar por Semestre UMSA:", 1, 9, 3)
    
    df_sem = df_courses[df_courses['semester'] == sem_selected]
    
    st.dataframe(
        df_sem.rename(columns={
            "code": "Sigla",
            "name": "Materia",
            "semester": "Semestre",
            "status": "Estado",
            "grade": "Nota",
            "prereq": "Requisitos"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("### 🌟 Equivalencias Abiertas de Alto Valor (MIT & Harvard)")
    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.info("""
        **Sinergia para 3° Semestre:**
        - 💻 **IND-312 Informática:** [Harvard CS50x - Introduction to Computer Science](https://cs50.harvard.edu/x/) (C, Python, SQL y Algoritmos).
        - 🔹 **IND-311 Probabilidades:** [Harvard Stat 110 - Introduction to Probability](https://projects.iq.harvard.edu/stat110) (Joseph Blitzstein).
        """)
    with col_eq2:
        st.info("""
        **Sinergia para Semestres Siguientes:**
        - 📊 **IND-411 Estadística Inferencial:** [MIT 6.0002 - Data Science & Computational Thinking](https://ocw.mit.edu/courses/6-0002-introduction-to-computational-thinking-and-data-science-fall-2016/).
        - 📈 **IND-521 Econometría & IND-532 Control de Calidad:** HarvardX Data Science & Modelos Shewhart.
        """)

conn.close()
