import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="NEXUS Life OS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "nexus.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Custom styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px;
    }
    .badge-dup {
        background-color: #fef3c7;
        color: #92400e;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        display: inline-block;
        margin-right: 6px;
    }
    .badge-ai-found {
        background-color: #ede9fe;
        color: #5b21b6;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        display: inline-block;
        margin-right: 6px;
    }
    .badge-bolivia {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        display: inline-block;
    }
    .ai-what-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 8px 12px;
        border-radius: 0 6px 6px 0;
        margin: 6px 0;
        font-size: 13px;
    }
    .ai-helps-box {
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 8px 12px;
        border-radius: 0 6px 6px 0;
        margin: 6px 0;
        font-size: 13px;
    }
    .table-meta {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 10px;
        font-size: 12px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🧠 NEXUS Life OS")
    st.markdown("**Usuario:** Mark Hazard (`@Mark020226`)")
    st.markdown("**Ubicación:** 🇧🇴 La Paz, Bolivia")
    st.markdown("**Carrera:** Ing. Industrial - UMSA (Plan 2015)")
    st.markdown("---")
    
    st.markdown("### 🎯 Sistema Inteligente")
    st.info("Segundo Cerebro con deduplicación automática, índice de empleabilidad y verificación para Bolivia.")
    st.markdown("---")
    st.caption("v3.2 | Respaldado en GitHub & SQLite")

# Top KPIs
conn = get_db()
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM resources")
total_resources = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM resources WHERE is_duplicate=1")
total_duplicates = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM resources WHERE direct_url IS NOT NULL AND direct_url != post_url AND direct_url != ''")
direct_links_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM academic_courses WHERE status='Aprobada'")
courses_approved = cur.fetchone()[0]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💡 Recursos Totales", f"{total_resources}", f"{total_resources - (total_duplicates // 2)} únicos")
with col2:
    st.metric("⚠️ Recursos Repetidos", f"{total_duplicates}", "Detectados por la IA")
with col3:
    st.metric("🚀 Enlaces Directos Reales", f"{direct_links_count}", "Sitios web / GitHub / Drives")
with col4:
    st.metric("🎓 Avance Malla UMSA", f"{courses_approved} / 54", f"{int((courses_approved/54)*100)}%")

st.markdown("---")

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💡 Segundo Cerebro (Biblioteca Inteligente)",
    "🎓 Malla UMSA & Informática MIT",
    "📊 Hábitos & Energía Diaria",
    "💰 Finanzas (InvernovAH)"
])

# ------------------------------------------------------------
# TAB 1: SEGUNDO CEREBRO (INTELIGENCIA AVANZADA)
# ------------------------------------------------------------
with tab1:
    st.subheader("💡 Biblioteca Inteligente de Recursos & Enlaces")
    st.markdown("""
    Cada recurso cuenta con **deduplicación automática** (te avisa si ya lo guardaste en otra publicación), 
    **enlace directo al recurso real** (encontrado por la IA incluso si el creador no lo puso), 
    **índice de empleabilidad**, **peso de certificación** y **disponibilidad para Bolivia 🇧🇴**.
    """)
    
    # Filter controls
    col_search, col_cat = st.columns([3, 2])
    with col_search:
        search_query = st.text_input("🔍 Buscar por palabra clave (Claude, NASA, NVIDIA, Python, Beca, CS50, n8n, etc.):", "")
        
    cur.execute("SELECT DISTINCT category FROM resources WHERE category IS NOT NULL AND category != ''")
    categories = [r[0] for r in cur.fetchall()]
    
    with col_cat:
        cat_filter = st.selectbox("Categoría:", ["Todas"] + categories)
        
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        only_direct = st.checkbox("🚀 Solo con enlace directo", value=False)
    with col_f2:
        only_cert = st.checkbox("🎓 Solo con certificación", value=False)
    with col_f3:
        only_bolivia = st.checkbox("🇧🇴 100% aplicable para Bolivia", value=False)
    with col_f4:
        dup_filter = st.selectbox("Filtro de Duplicados:", ["Todos", "Ocultar Repetidos (Solo Únicos)", "Solo Repetidos"])
        
    # Build Query
    query = """
    SELECT id, title, category, source, author, date_added, date_saved, date_published,
           url, post_url, direct_url, is_duplicate, duplicate_count, duplicate_sources,
           found_by_ai, ai_what_it_does, ai_how_it_helps, has_certification,
           recruiter_weight, employability_score, bolivia_eligible, summary, status
    FROM resources 
    WHERE 1=1
    """
    params = []
    
    if search_query:
        query += " AND (title LIKE ? OR summary LIKE ? OR ai_what_it_does LIKE ? OR ai_how_it_helps LIKE ? OR direct_url LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])
    if cat_filter != "Todas":
        query += " AND category = ?"
        params.append(cat_filter)
    if only_direct:
        query += " AND direct_url IS NOT NULL AND direct_url != post_url AND direct_url != ''"
    if only_cert:
        query += " AND has_certification LIKE '%Sí%'"
    if only_bolivia:
        query += " AND bolivia_eligible LIKE '%✅%'"
    if dup_filter == "Ocultar Repetidos (Solo Únicos)":
        query += " GROUP BY direct_url_clean"
    elif dup_filter == "Solo Repetidos":
        query += " AND is_duplicate = 1"
        
    query += " ORDER BY date_added DESC LIMIT 60"
    
    df_res = pd.read_sql_query(query, conn, params=params)
    st.write(f"Mostrando **{len(df_res)}** recursos encontrados:")
    
    # Display cards
    for idx, row in df_res.iterrows():
        has_direct = row['direct_url'] and row['direct_url'] != row['post_url']
        is_dup = row['is_duplicate'] == 1
        found_ai = row['found_by_ai'] == 1
        
        # Card Header
        with st.expander(f"{row['category']} | {row['title']}"):
            
            # Badges Bar
            badges_html = ""
            if is_dup:
                badges_html += f'<span class="badge-dup">⚠️ RECURSO REPETIDO (Guardado en {row["duplicate_count"]} publicaciones)</span>'
            if found_ai:
                badges_html += '<span class="badge-ai-found">🔍 ENLACE REAL BUSCADO POR IA (No estaba en el post)</span>'
            if "✅" in str(row['bolivia_eligible']):
                badges_html += '<span class="badge-bolivia">🇧🇴 APTO PARA BOLIVIA</span>'
                
            if badges_html:
                st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
                st.markdown("")
                
            # If duplicate, show alert with other posts
            if is_dup and row['duplicate_sources']:
                st.warning(f"ℹ️ **Aviso de Duplicado:** Este mismo recurso ya lo habías guardado en estas otras publicaciones:\n\n{row['duplicate_sources']}")
                
            # 1. AI Value: What it does & How it helps
            st.markdown(f"""
            <div class="ai-what-box">
                <strong>🛠️ ¿Qué te permite hacer este recurso?</strong><br/>
                {row['ai_what_it_does']}
            </div>
            <div class="ai-helps-box">
                <strong>💡 ¿En qué te ayuda a ti (Ingeniería / Carrera / NEXUS)?</strong><br/>
                {row['ai_how_it_helps']}
            </div>
            """, unsafe_allow_html=True)
            
            # 2. Market Value & Employability Table
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown(f"🎓 **Certificación Oficial:** `{row['has_certification']}`")
                st.markdown(f"⭐ **Peso ante Reclutadores:** {row['recruiter_weight']}")
            with col_t2:
                st.markdown(f"📈 **Índice de Empleabilidad:** `{row['employability_score']}`")
                st.markdown(f"🇧🇴 **Disponibilidad para Bolivia:** {row['bolivia_eligible']}")
                
            st.markdown("---")
            
            # 3. Links Section
            st.markdown("#### 🔗 Enlaces de Acceso Rápido:")
            col_link1, col_link2 = st.columns([1, 1])
            with col_link1:
                if has_direct:
                    st.markdown(f"👉 **[🚀 ABRIR RECURSO REAL DIRECTO]({row['direct_url']})**")
                    st.caption(f"Destino real: `{row['direct_url'][:75]}`")
                else:
                    st.markdown(f"👉 **[🚀 ABRIR ENLACE DEL RECURSO]({row['url']})**")
            with col_link2:
                if row['post_url']:
                    st.markdown(f"📱 **[Ver Publicación / Reel Original en Instagram]({row['post_url']})**")
                    st.caption("Video o mensaje del creador")
                    
            st.markdown("---")
            
            # 4. Dates & Author Metadata
            st.caption(f"👤 **Publicado por:** `{row['author'] or row['source']}` | 📅 **Guardado por ti:** {row['date_saved'] or row['date_added']} | ⏱️ **Fecha publicación:** {row['date_published']} | Estado: `{row['status']}`")
            
            # 5. Original caption in collapsible expander
            with st.expander("📝 Ver descripción original del creador (texto del video/post)"):
                st.text(row['summary'] if row['summary'] else "Sin descripción adicional.")
                
    st.markdown("---")
    st.markdown("### ➕ Añadir Nuevo Enlace Manualmente")
    with st.form("add_resource_form"):
        f_url = st.text_input("URL del recurso real / página / video:")
        f_title = st.text_input("Título descriptivo:")
        f_cat = st.selectbox("Categoría:", categories if categories else ["🤖 Inteligencia Artificial & Agentes"])
        f_what = st.text_input("¿Qué permite hacer?")
        f_helps = st.text_area("¿En qué te ayuda a ti?")
        submit_res = st.form_submit_button("Guardar en Segundo Cerebro")
        
        if submit_res and f_url:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            cur.execute("""
            INSERT INTO resources (url, direct_url, post_url, title, summary, ai_what_it_does, ai_how_it_helps, category, date_added, date_saved, date_published, source, author, status, bolivia_eligible)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Entrada Manual', 'Mark Hazard', 'Pendiente', '✅ Disponible online')
            """, (f_url, f_url, f_url, f_title or f_url, f_what, f_what, f_helps, f_cat, now_str, now_str, now_str[:10]))
            conn.commit()
            st.success("¡Recurso añadido exitosamente a tu Segundo Cerebro!")
            st.rerun()

# ------------------------------------------------------------
# TAB 2: MALLA UMSA & MIT
# ------------------------------------------------------------
with tab2:
    st.subheader("🎓 Malla Curricular UMSA (Plan 2015) & Equivalencias MIT / Harvard")
    st.markdown("Tu plan de re-aprendizaje: actualiza el estado de tus materias para proyectar tu avance y desbloquear cursos avanzados de ciencias de la computación.")
    
    df_courses = pd.read_sql_query("SELECT code, name, semester, status, grade, prereq FROM academic_courses ORDER BY semester, code", conn)
    
    sem_selected = st.slider("Filtrar por Semestre:", 1, 9, 3)
    df_sem = df_courses[df_courses['semester'] == sem_selected]
    
    st.dataframe(
        df_sem.rename(columns={
            "code": "Sigla",
            "name": "Materia",
            "semester": "Semestre",
            "status": "Estado Actual",
            "grade": "Nota",
            "prereq": "Requisitos"
        }),
        width="stretch",
        hide_index=True
    )
    
    st.markdown("### 🌟 Equivalencias Abiertas Recomendadas (MIT & Harvard - OSSU)")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.info("""
        **Para 3° Semestre:**
        - 💻 **IND-312 Informática:** [Harvard CS50x - Introduction to Computer Science](https://cs50.harvard.edu/x/) (C, Python, SQL y Algoritmos).
        - 🔹 **IND-311 Probabilidades:** [Harvard Stat 110 - Introduction to Probability](https://projects.iq.harvard.edu/stat110) (Joseph Blitzstein).
        """)
    with col_m2:
        st.info("""
        **Para los siguientes semestres:**
        - 📊 **IND-411 Estadística:** [MIT 6.0002 - Introduction to Computational Thinking and Data Science](https://ocw.mit.edu/courses/6-0002-introduction-to-computational-thinking-and-data-science-fall-2016/).
        - 📈 **IND-521 Econometría:** HarvardX Data Science (Regresión Lineal y Modelado).
        """)

# ------------------------------------------------------------
# TAB 3: HÁBITOS Y ENERGÍA
# ------------------------------------------------------------
with tab3:
    st.subheader("📊 Control Estadístico de Hábitos, Sueño y Energía (Método Shewhart)")
    st.markdown("Registra tus datos diarios para evaluar tu calidad de vida y correlacionar descanso con rendimiento académico.")
    
    with st.form("daily_metric_form"):
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        with col_d1:
            f_date = st.date_input("Fecha:", datetime.now())
        with col_d2:
            f_sleep = st.number_input("Horas de sueño:", min_value=0.0, max_value=16.0, value=7.0, step=0.5)
        with col_d3:
            f_energy = st.slider("Nivel de Energía (1-10):", 1, 10, 7)
        with col_d4:
            f_mood = st.slider("Estado de Ánimo (1-10):", 1, 10, 8)
            
        f_notes = st.text_input("Observaciones del día:")
        submit_metric = st.form_submit_button("Registrar Día")
        
        if submit_metric:
            cur.execute("""
            INSERT OR REPLACE INTO daily_metrics (date, sleep_hours, energy_level, mood, productive_hours, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (str(f_date), f_sleep, f_energy, f_mood, 0.0, f_notes))
            conn.commit()
            st.success("¡Métricas del día registradas!")
            st.rerun()
            
    df_metrics = pd.read_sql_query("SELECT * FROM daily_metrics ORDER BY date", conn)
    if not df_metrics.empty:
        fig = px.line(df_metrics, x="date", y=["sleep_hours", "energy_level", "mood"],
                      labels={"value": "Puntaje / Horas", "date": "Fecha", "variable": "Métrica"},
                      title="Tendencia de Sueño vs Energía y Ánimo")
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Aún no has registrado días. Completa el formulario de arriba para generar tu primer gráfico de control.")

# ------------------------------------------------------------
# TAB 4: FINANZAS PERSONALES
# ------------------------------------------------------------
with tab4:
    st.subheader("💰 Control Financiero (Metodología InvernovAH - Regla 50/30/20)")
    st.markdown("Aplica la filosofía de Álvaro Hernández: **50% Necesidades básicas, 30% Deseos/Estilo de vida, 20% Ahorro e Inversión**.")
    
    col_fin1, col_fin2 = st.columns([1, 2])
    with col_fin1:
        with st.form("finance_form"):
            t_type = st.selectbox("Tipo:", ["Gasto", "Ingreso"])
            t_cat = st.selectbox("Categoría:", ["Necesidades (50%)", "Deseos (30%)", "Ahorro/Inversión (20%)", "Educación/Libros", "Transporte/Universidad"])
            t_amount = st.number_input("Monto (Bs.):", min_value=0.0, value=25.0, step=5.0)
            t_desc = st.text_input("Descripción:")
            submit_fin = st.form_submit_button("Registrar Transacción")
            
            if submit_fin and t_amount > 0:
                cur.execute("""
                INSERT INTO finance_transactions (date, type, category, amount, description)
                VALUES (?, ?, ?, ?, ?)
                """, (datetime.now().strftime("%Y-%m-%d"), t_type, t_cat, t_amount, t_desc))
                conn.commit()
                st.success("Transacción registrada.")
                st.rerun()
                
    with col_fin2:
        df_fin = pd.read_sql_query("SELECT * FROM finance_transactions ORDER BY date DESC", conn)
        if not df_fin.empty:
            expenses = df_fin[df_fin['type'] == 'Gasto']
            if not expenses.empty:
                fig_pie = px.pie(expenses, names="category", values="amount", title="Distribución de Gastos", hole=0.4)
                st.plotly_chart(fig_pie, width="stretch")
            st.dataframe(df_fin, width="stretch", hide_index=True)
        else:
            st.info("No hay transacciones registradas aún. Ingresa tu primer gasto o ingreso.")

conn.close()
