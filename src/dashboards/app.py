import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        padding: 16px;
    }
    .ai-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin: 8px 0;
        color: #14532d;
    }
    .direct-btn {
        display: inline-block;
        background-color: #2563eb;
        color: white !important;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 6px;
        text-decoration: none !important;
        margin-right: 10px;
    }
    .source-btn {
        display: inline-block;
        background-color: #f1f5f9;
        color: #475569 !important;
        font-weight: 500;
        padding: 6px 12px;
        border-radius: 6px;
        text-decoration: none !important;
        border: 1px solid #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🧠 NEXUS Life OS")
    st.markdown("**Usuario:** Mark Hazard (`@Mark020226`)")
    st.markdown("**Carrera:** Ing. Industrial - UMSA (Plan 2015)")
    st.markdown("---")
    
    st.markdown("### 🎯 Enfoque Actual")
    st.info("Re-aprendizaje activo + Ingesta inteligente de recursos + Análisis con IA.")
    
    st.markdown("---")
    st.markdown("### ⚡ Acceso Rápido")
    st.caption("269 recursos analizados y enriquecidos con IA.")

# Top KPIs
conn = get_db()
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM resources")
total_resources = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM resources WHERE direct_url IS NOT NULL AND direct_url != post_url AND direct_url != ''")
direct_links_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM academic_courses WHERE status='Aprobada'")
courses_approved = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM academic_courses")
total_courses = cur.fetchone()[0]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💡 Recursos en Segundo Cerebro", f"{total_resources}", "Analizados con IA")
with col2:
    st.metric("🚀 Enlaces Directos a Recursos", f"{direct_links_count}", "Sitios web / GitHub / Drives")
with col3:
    st.metric("🎓 Materias Aprobadas UMSA", f"{courses_approved} / {total_courses}", f"{int((courses_approved/total_courses)*100)}% avance")
with col4:
    st.metric("🤖 Agentes Activos", "5 Agentes", "Segundo Cerebro, UMSA, Finanzas, Hábitos")

st.markdown("---")

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💡 Segundo Cerebro (Biblioteca de Recursos)",
    "🎓 Malla UMSA & Informática MIT",
    "📊 Hábitos & Energía Diaria",
    "💰 Finanzas (InvernovAH)"
])

# ------------------------------------------------------------
# TAB 1: SEGUNDO CEREBRO (ENRIQUECIDO)
# ------------------------------------------------------------
with tab1:
    st.subheader("💡 Tu Biblioteca Inteligente de Recursos & Enlaces")
    st.markdown("Cada recurso incluye su **síntesis de valor generada por IA**, su **enlace directo al recurso real** (GitHub, Drive, sitio web) y el enlace original.")
    
    col_search, col_cat, col_filter_direct = st.columns([2, 1, 1])
    
    cur.execute("SELECT DISTINCT category FROM resources WHERE category IS NOT NULL AND category != ''")
    categories = [r[0] for r in cur.fetchall()]
    
    with col_search:
        search_query = st.text_input("🔍 Buscar por palabra clave (Claude, NASA, NVIDIA, Python, Beca, Prompt, etc.):", "")
    with col_cat:
        cat_filter = st.selectbox("Categoría:", ["Todas"] + categories)
    with col_filter_direct:
        only_direct = st.checkbox("🚀 Solo con enlace directo al recurso real", value=False)
        
    # Query resources
    query = """
    SELECT id, title, category, source, author, date_added, url, post_url, direct_url, summary, ai_summary, status 
    FROM resources 
    WHERE 1=1
    """
    params = []
    
    if search_query:
        query += " AND (title LIKE ? OR summary LIKE ? OR ai_summary LIKE ? OR url LIKE ? OR direct_url LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])
    if cat_filter != "Todas":
        query += " AND category = ?"
        params.append(cat_filter)
    if only_direct:
        query += " AND direct_url IS NOT NULL AND direct_url != post_url AND direct_url != ''"
        
    query += " ORDER BY date_added DESC LIMIT 60"
    
    df_res = pd.read_sql_query(query, conn, params=params)
    st.write(f"Mostrando **{len(df_res)}** recursos encontrados:")
    
    # Display cards
    for idx, row in df_res.iterrows():
        has_direct = row['direct_url'] and row['direct_url'] != row['post_url']
        
        with st.expander(f"{row['category']} | {row['title']}"):
            # 1. AI Value Summary Box
            if row['ai_summary']:
                st.markdown(f"""
                <div class="ai-box">
                    {row['ai_summary']}
                </div>
                """, unsafe_allow_html=True)
                
            # 2. Action Buttons / Direct URLs
            st.markdown("#### 🔗 Enlaces de Acceso:")
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                if has_direct:
                    st.markdown(f"👉 **[🚀 ABRIR RECURSO REAL DIRECTO]({row['direct_url']})**")
                    st.caption(f"Destino: `{row['direct_url'][:70]}`")
                else:
                    st.markdown(f"👉 **[🚀 ABRIR ENLACE DEL RECURSO]({row['url']})**")
            with col_b2:
                if row['post_url']:
                    st.markdown(f"📱 **[Ver Publicación / Reel Original en Instagram]({row['post_url']})**")
            
            st.markdown("---")
            st.markdown(f"**👤 Publicado por:** `{row['author'] or row['source']}` | **📅 Fecha:** {row['date_added']} | **Estado:** `{row['status']}`")
            
            # 3. Original Caption in Collapsible Expander
            with st.expander("📝 Ver descripción original del creador"):
                st.text(row['summary'] if row['summary'] else "Sin descripción adicional.")
                
    st.markdown("---")
    st.markdown("### ➕ Añadir Nuevo Enlace Manualmente")
    with st.form("add_resource_form"):
        f_url = st.text_input("URL del recurso real / página / video:")
        f_title = st.text_input("Título descriptivo:")
        f_cat = st.selectbox("Categoría:", categories if categories else ["🤖 Inteligencia Artificial & Agentes"])
        f_summary = st.text_area("Notas / Lo que te aporta:")
        submit_res = st.form_submit_button("Guardar en Segundo Cerebro")
        
        if submit_res and f_url:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            cur.execute("""
            INSERT INTO resources (url, direct_url, post_url, title, summary, ai_summary, category, date_added, source, author, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Entrada Manual', 'Mark Hazard', 'Pendiente')
            """, (f_url, f_url, f_url, f_title or f_url, f_summary, f"💡 **Nota de Mark:** {f_summary}", f_cat, now_str))
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
