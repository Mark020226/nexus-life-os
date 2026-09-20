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
    .ai-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin: 8px 0;
        color: #14532d;
    }
    .dup-badge {
        display: inline-block;
        background-color: #fff7ed;
        color: #c2410c;
        border: 1px solid #fdba74;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 6px;
    }
    .emp-badge {
        display: inline-block;
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 6px;
    }
    .cert-badge {
        display: inline-block;
        background-color: #f5f3ff;
        color: #6d28d9;
        border: 1px solid #ddd6fe;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
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
    st.info("Re-aprendizaje activo + Detección de duplicados + Métricas de empleabilidad objetivas.")
    
    st.markdown("---")
    st.markdown("### ⚡ Acceso Rápido")
    st.caption("Base de datos con 269 recursos, índice de empleabilidad y fechas dobles.")

# Top KPIs
conn = get_db()
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM resources")
total_resources = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM resources WHERE duplicate_count > 1")
total_dups = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM resources WHERE direct_url IS NOT NULL AND direct_url != post_url AND direct_url != ''")
direct_links_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM academic_courses WHERE status='Aprobada'")
courses_approved = cur.fetchone()[0]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💡 Recursos en Segundo Cerebro", f"{total_resources}", "Analizados con IA")
with col2:
    st.metric("⚠️ Recursos Repetidos en Posts", f"{total_dups}", "Agrupados automáticamente")
with col3:
    st.metric("🚀 Enlaces Directos al Recurso", f"{direct_links_count}", "Sin pasar por la publicación")
with col4:
    st.metric("🎓 Avance Malla UMSA", f"{courses_approved} / 54", f"{int((courses_approved/54)*100)}% aprobado")

st.markdown("---")

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💡 Segundo Cerebro (Con Detección de Repetidos & Empleabilidad)",
    "🎓 Malla UMSA & Informática MIT",
    "📊 Hábitos & Energía Diaria",
    "💰 Finanzas (InvernovAH)"
])

# ------------------------------------------------------------
# TAB 1: SEGUNDO CEREBRO INTELIGENTE
# ------------------------------------------------------------
with tab1:
    st.subheader("💡 Biblioteca Inteligente con Detección de Duplicados e Índice Laboral")
    st.markdown("""
    Cada recurso ahora incluye:
    - ⚠️ **Detección de duplicados:** Identifica si el recurso real ya te había aparecido en otras publicaciones.
    - 📈 **Índice de Empleabilidad:** Porcentaje estimado con métricas reales de inserción y demanda en el mercado.
    - 📜 **Certificación y Peso ante Reclutadores:** Si tiene validez oficial de Harvard, MIT, NVIDIA, NASA o Anthropic.
    - 📅 **Fechas Dobles:** Fecha exacta en que se publicó el video/post y fecha en que lo guardaste.
    """)
    
    col_search, col_cat, col_filter_dup, col_sort = st.columns([2, 1, 1, 1])
    
    cur.execute("SELECT DISTINCT category FROM resources WHERE category IS NOT NULL AND category != ''")
    categories = [r[0] for r in cur.fetchall()]
    
    with col_search:
        search_query = st.text_input("🔍 Buscar (ej. Claude, NASA, NVIDIA, Python, CS50, Beca):", "")
    with col_cat:
        cat_filter = st.selectbox("Categoría:", ["Todas"] + categories)
    with col_filter_dup:
        dup_filter = st.selectbox("Filtro de Duplicados:", ["Todos", "⚠️ Solo Repetidos", "✨ Solo Únicos", "🚀 Con Enlace Directo"])
    with col_sort:
        sort_by = st.selectbox("Ordenar por:", ["Más Recientes Guardados", "Mayor Empleabilidad", "Más Repetidos (Tendencia)"])
        
    # Build Query
    query = """
    SELECT id, title, category, source, author, date_added, url, post_url, direct_url, 
           summary, ai_summary, status, published_date, saved_date, 
           canonical_key, canonical_name, duplicate_count, 
           employability_index, employability_details, certification_status, recruiter_weight
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
    if dup_filter == "⚠️ Solo Repetidos":
        query += " AND duplicate_count > 1"
    elif dup_filter == "✨ Solo Únicos":
        query += " AND duplicate_count = 1"
    elif dup_filter == "🚀 Con Enlace Directo":
        query += " AND direct_url IS NOT NULL AND direct_url != post_url AND direct_url != ''"
        
    if sort_by == "Mayor Empleabilidad":
        query += " ORDER BY employability_index DESC, date_added DESC LIMIT 60"
    elif sort_by == "Más Repetidos (Tendencia)":
        query += " ORDER BY duplicate_count DESC, date_added DESC LIMIT 60"
    else:
        query += " ORDER BY saved_date DESC LIMIT 60"
        
    df_res = pd.read_sql_query(query, conn, params=params)
    st.write(f"Mostrando **{len(df_res)}** recursos encontrados:")
    
    # Display cards
    for idx, row in df_res.iterrows():
        is_duplicate = row['duplicate_count'] > 1
        has_direct = row['direct_url'] and row['direct_url'] != row['post_url']
        
        # Header title
        header_text = f"{row['category']} | {row['title'][:70]}"
        if is_duplicate:
            header_text = f"⚠️ [Repetido x{row['duplicate_count']}] " + header_text
            
        with st.expander(header_text):
            # 1. Badges Bar
            col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
            with col_b1:
                if is_duplicate:
                    st.markdown(f"⚠️ **Recurso repetido:** Aparece en **{row['duplicate_count']}** publicaciones distintas.")
                else:
                    st.markdown("✨ **Recurso Único:** Guardado 1 sola vez.")
            with col_b2:
                st.markdown(f"📈 **Empleabilidad:** `{row['employability_index']}`")
            with col_b3:
                st.markdown(f"📜 **Certificación:** `{row['certification_status']}`")
                
            st.markdown(f"👔 **Peso ante Reclutadores:** {row['recruiter_weight']}")
            
            # 2. AI Value Summary Box
            if row['ai_summary']:
                st.markdown(f"""
                <div class="ai-box">
                    {row['ai_summary']}
                </div>
                """, unsafe_allow_html=True)
                
            # 3. Employability Evidence Details
            if row['employability_details']:
                st.info(f"📊 **Métricas Reales de Mercado:** {row['employability_details']}")
                
            # 4. Action Buttons / Direct URLs
            st.markdown("#### 🔗 Enlaces de Acceso Rápido:")
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if has_direct:
                    st.markdown(f"👉 **[🚀 ABRIR RECURSO REAL DIRECTO]({row['direct_url']})**")
                    st.caption(f"Destino real: `{row['direct_url'][:75]}`")
                else:
                    st.markdown(f"👉 **[🚀 ABRIR ENLACE DEL RECURSO]({row['url']})**")
            with col_btn2:
                if row['post_url']:
                    st.markdown(f"📱 **[Ver Publicación / Reel Original en Instagram]({row['post_url']})**")
                    
            # 5. Double Dates & Author
            st.markdown("---")
            pub_str = row['published_date'] if row['published_date'] else "No disponible"
            sav_str = row['saved_date'] if row['saved_date'] else row['date_added']
            st.caption(f"📅 **Publicado originalmente:** `{pub_str}` | 💾 **Guardado por ti:** `{sav_str}` | 👤 **Autor:** `{row['author'] or row['source']}`")
            
            # 6. Show other posts referencing the same resource if duplicated
            if is_duplicate and row['canonical_key']:
                with st.expander(f"🔁 Ver las otras publicaciones que hablan de este mismo recurso ({row['canonical_name']})"):
                    cur.execute("""
                    SELECT title, author, published_date, post_url 
                    FROM resources 
                    WHERE canonical_key = ? AND id != ?
                    LIMIT 5
                    """, (row['canonical_key'], row['id']))
                    other_posts = cur.fetchall()
                    for op in other_posts:
                        st.markdown(f"- **{op['title']}** (por `{op['author']}`, publicado: `{op['published_date']}`) → [Ver post]({op['post_url']})")
                        
            # 7. Original caption
            with st.expander("📝 Ver pie de foto / texto original"):
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
            INSERT INTO resources (url, direct_url, post_url, title, summary, ai_summary, category, date_added, saved_date, published_date, source, author, status, duplicate_count, employability_index, certification_status, recruiter_weight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Entrada Manual', 'Mark Hazard', 'Pendiente', 1, '85% (Habilidad Técnica)', 'No especificado', '⭐⭐⭐ Impacto Medio')
            """, (f_url, f_url, f_url, f_title or f_url, f_summary, f"💡 **Nota de Mark:** {f_summary}", f_cat, now_str, now_str, now_str))
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
