import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
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
    .ai-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin: 8px 0;
        color: #14532d;
    }
    .dup-box {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin: 8px 0;
        color: #92400e;
    }
    .tech-pill {
        display: inline-block;
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: 600;
        margin-right: 6px;
    }
    .bolivia-pill {
        display: inline-block;
        background-color: #fef2f2;
        color: #b91c1c;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: 600;
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
    st.info("Re-aprendizaje activo + Ingesta inteligente de recursos + Validación de Empleabilidad & Bolivia.")
    
    st.markdown("---")
    st.markdown("### ⚡ Acceso Rápido")
    st.caption("269 recursos analizados con detección de duplicados.")

# Top KPIs
conn = get_db()
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM resources")
total_resources = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM resources WHERE duplicate_count > 1")
repeated_items = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM resources WHERE has_certificate LIKE '%Certificado%'")
cert_items = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM academic_courses WHERE status='Aprobada'")
courses_approved = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM academic_courses")
total_courses = cur.fetchone()[0]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💡 Recursos en Biblioteca", f"{total_resources}", "Total en Segundo Cerebro")
with col2:
    st.metric("🔁 Recursos Repetidos", f"{repeated_items}", "Menciones cruzadas detectadas")
with col3:
    st.metric("🎓 Con Certificación", f"{cert_items}", "Validados ante reclutadores")
with col4:
    st.metric("📚 Avance Malla UMSA", f"{courses_approved}/{total_courses}", f"{int((courses_approved/total_courses)*100)}% de carrera")

st.markdown("---")

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💡 Segundo Cerebro (Biblioteca de Recursos)",
    "🎓 Malla UMSA & Informática MIT",
    "📊 Hábitos & Energía Diaria",
    "💰 Finanzas (InvernovAH)"
])

# ------------------------------------------------------------
# TAB 1: SEGUNDO CEREBRO (SÚPER ENRIQUECIDO)
# ------------------------------------------------------------
with tab1:
    st.subheader("💡 Tu Biblioteca Inteligente de Recursos & Enlaces")
    st.markdown("Con **detección automática de recursos repetidos**, **índice de empleabilidad real**, **acreditación para reclutadores** y **validación para Bolivia 🇧🇴**.")
    
    col_search, col_cat, col_filter_dup, col_filter_cert = st.columns([2, 1, 1, 1])
    
    cur.execute("SELECT DISTINCT category FROM resources WHERE category IS NOT NULL AND category != ''")
    categories = [r[0] for r in cur.fetchall()]
    
    with col_search:
        search_query = st.text_input("🔍 Buscar (ej. Claude, CS50, NASA, NVIDIA, Python, Beca):", "")
    with col_cat:
        cat_filter = st.selectbox("Categoría:", ["Todas"] + categories)
    with col_filter_dup:
        only_duplicates = st.checkbox("🔁 Solo recursos repetidos", value=False)
    with col_filter_cert:
        only_cert = st.checkbox("🎓 Solo con certificado", value=False)
        
    # Query resources
    query = """
    SELECT id, title, category, source, author, date_added, url, post_url, direct_url, summary, ai_summary,
           canonical_name, duplicate_count, duplicate_mentions, employability_score, employability_analysis,
           has_certificate, recruiter_weight, bolivia_status, bolivia_details, published_date, saved_date, status
    FROM resources 
    WHERE 1=1
    """
    params = []
    
    if search_query:
        query += " AND (title LIKE ? OR summary LIKE ? OR ai_summary LIKE ? OR canonical_name LIKE ? OR direct_url LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])
    if cat_filter != "Todas":
        query += " AND category = ?"
        params.append(cat_filter)
    if only_duplicates:
        query += " AND duplicate_count > 1"
    if only_cert:
        query += " AND has_certificate LIKE '%Certificado%'"
        
    query += " ORDER BY employability_score DESC, date_added DESC LIMIT 60"
    
    df_res = pd.read_sql_query(query, conn, params=params)
    st.write(f"Mostrando **{len(df_res)}** recursos encontrados (ordenados por mayor empleabilidad y fecha):")
    
    # Display cards
    for idx, row in df_res.iterrows():
        dup_count = row['duplicate_count']
        has_direct = row['direct_url'] and row['direct_url'] != row['post_url']
        
        with st.expander(f"[{row['category']}] {row['canonical_name'] or row['title']} (Empleabilidad: {row['employability_score']}%)"):
            
            # 1. Duplicate Warning Banner
            if dup_count > 1:
                st.markdown(f"""
                <div class="dup-box">
                    <strong>🔁 RECURSO REPETIDO / YA VISTO EN OTRA PUBLICACIÓN:</strong><br>
                    Este recurso real (<em>{row['canonical_name']}</em>) ya lo tienes guardado en un total de <strong>{dup_count} publicaciones</strong> diferentes.
                </div>
                """, unsafe_allow_html=True)
                
                # Show other mentions expander
                if row['duplicate_mentions']:
                    try:
                        other_list = json.loads(row['duplicate_mentions'])
                        with st.expander(f"👁️ Ver las otras {len(other_list)} publicaciones donde también guardaste esto"):
                            for o in other_list[:5]:
                                st.markdown(f"• **{o.get('title')}** — por `{o.get('author')}` (Guardado: {o.get('saved_date')}) | [Ver post]({o.get('post_url')})")
                    except Exception:
                        pass
                        
            # 2. AI Value Summary Box
            if row['ai_summary']:
                st.markdown(f"""
                <div class="ai-box">
                    <strong>💡 Lo que te aporta este recurso:</strong><br>
                    {row['ai_summary']}
                </div>
                """, unsafe_allow_html=True)
                
            # 3. Employability & Recruiter Weight Section
            st.markdown("#### 🎯 Índice de Empleabilidad & Mercado Laboral:")
            col_emp1, col_emp2 = st.columns([1, 2])
            with col_emp1:
                st.progress(row['employability_score'] / 100.0)
                st.caption(f"Score de Retorno/Empleabilidad: **{row['employability_score']}%**")
                st.markdown(f"**Certificación:** `{row['has_certificate']}`")
                st.markdown(f"**Peso en CV/ATS:** {row['recruiter_weight']}")
            with col_emp2:
                st.markdown(row['employability_analysis'])
                
            # 4. Bolivia Availability Section
            st.markdown("---")
            st.markdown("#### 🇧🇴 Disponibilidad para Bolivia:")
            col_bol1, col_bol2 = st.columns([1, 2])
            with col_bol1:
                st.markdown(f"**Estado:** `{row['bolivia_status']}`")
            with col_bol2:
                st.markdown(f"ℹ️ {row['bolivia_details']}")
                
            # 5. Direct Action Links
            st.markdown("---")
            st.markdown("#### 🔗 Enlaces de Acceso:")
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                if row['direct_url']:
                    st.markdown(f"👉 **[🚀 ABRIR RECURSO REAL DIRECTO]({row['direct_url']})**")
                    st.caption(f"URL de destino: `{row['direct_url'][:75]}`")
            with col_b2:
                if row['post_url']:
                    st.markdown(f"📱 **[Ver Publicación / Reel Original en Instagram]({row['post_url']})**")
            
            # 6. Double Date & Metadata
            st.markdown("---")
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                st.markdown(f"**👤 Creador / Cuenta:** `{row['author'] or row['source']}`")
            with col_meta2:
                st.markdown(f"**📅 Guardado el:** `{row['saved_date'] or row['date_added']}`")
            with col_meta3:
                st.markdown(f"**📢 Publicación:** `{row['published_date']}`")
                
            # 7. Original Caption
            with st.expander("📝 Ver descripción original completa del creador"):
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
            INSERT INTO resources (url, direct_url, post_url, title, summary, ai_summary, category, date_added, saved_date, published_date, source, author, canonical_name, duplicate_count, employability_score, employability_analysis, has_certificate, recruiter_weight, bolivia_status, bolivia_details, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Entrada Manual', 'Mark Hazard', ?, 1, 75, 'Añadido por Mark para estudio personal.', '🛠️ Habilidad Práctica', '🟡 Medio', '🇧🇴 100% Accesible desde Bolivia', 'Acceso directo guardado por el usuario.', 'Pendiente')
            """, (f_url, f_url, f_url, f_title or f_url, f_summary, f"💡 **Nota de Mark:** {f_summary}", f_cat, now_str, now_str, now_str, f_title or f_url))
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
