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

# Clean, accessible styling
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
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-dup {
        background-color: #fef3c7;
        color: #92400e;
        border: 1px solid #f59e0b;
    }
    .badge-ai {
        background-color: #e0f2fe;
        color: #0369a1;
        border: 1px solid #38bdf8;
    }
    .badge-bolivia-ok {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #22c55e;
    }
    .badge-bolivia-warn {
        background-color: #fee2e2;
        color: #991b1b;
        border: 1px solid #ef4444;
    }
    .box-what {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin: 8px 0;
        font-size: 13.5px;
    }
    .box-how {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin: 8px 0;
        font-size: 13.5px;
    }
    .direct-link-btn {
        display: inline-block;
        background-color: #1d4ed8;
        color: #ffffff !important;
        font-weight: 700;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none !important;
        font-size: 13.5px;
        margin-top: 4px;
    }
    .post-link-btn {
        display: inline-block;
        background-color: #f1f5f9;
        color: #475569 !important;
        font-weight: 500;
        padding: 8px 14px;
        border-radius: 6px;
        text-decoration: none !important;
        font-size: 13.5px;
        border: 1px solid #cbd5e1;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🧠 NEXUS Life OS")
    st.markdown("**Usuario:** Mark Hazard (`@Mark020226`)")
    st.markdown("**Ubicación:** 🇧🇴 Bolivia | Ing. Industrial UMSA")
    st.markdown("---")
    
    st.markdown("### 🔍 Filtros Globales de Recursos")
    st.caption("Filtra tu Segundo Cerebro según tus prioridades:")

conn = get_db()
cur = conn.cursor()

# Get metrics
cur.execute("SELECT COUNT(*) FROM resources")
total_res = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM resources WHERE is_duplicate = 1")
dup_res_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM resources WHERE employability_index >= 85")
high_employability_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM resources WHERE has_certification LIKE '%Certificado%'")
cert_count = cur.fetchone()[0]

with st.sidebar:
    filter_dup = st.checkbox("⚠️ Solo recursos repetidos / multi-mencionados", value=False)
    filter_high_emp = st.checkbox("🔥 Solo Alta Empleabilidad (>= 85%)", value=False)
    filter_cert = st.checkbox("📜 Solo con Certificación Oficial", value=False)
    filter_bolivia = st.checkbox("🇧🇴 Solo 100% elegibles en Bolivia", value=False)
    st.markdown("---")
    st.caption("NEXUS v3 - Datos auditados y enriquecidos con IA.")

# Top KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💡 Recursos Catalogados", f"{total_res}", "Con análisis de valor")
with col2:
    st.metric("🔥 Alta Empleabilidad", f"{high_employability_count}", "Reconocidos por BigTech/Mercado")
with col3:
    st.metric("📜 Con Certificación", f"{cert_count}", "Oficiales y verificables")
with col4:
    st.metric("🔁 Menciones Repetidas", f"{dup_res_count}", "Detectados por la IA")

st.markdown("---")

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💡 Segundo Cerebro (Biblioteca Inteligente)",
    "🎓 Malla UMSA & Informática MIT",
    "📊 Hábitos & Energía Diaria",
    "💰 Finanzas (InvernovAH)"
])

# ------------------------------------------------------------
# TAB 1: SEGUNDO CEREBRO INTELIGENTE
# ------------------------------------------------------------
with tab1:
    st.subheader("💡 Tu Biblioteca Inteligente de Recursos & Conocimiento")
    st.markdown("Cada recurso cuenta con su **índice de empleabilidad real**, **disponibilidad para Bolivia 🇧🇴**, **tipo de certificación**, **detección de repetidos** y el **enlace directo al recurso real** sin pasar por publicaciones.")
    
    col_search, col_cat = st.columns([2, 1])
    
    cur.execute("SELECT DISTINCT category FROM resources WHERE category IS NOT NULL AND category != ''")
    categories = [r[0] for r in cur.fetchall()]
    
    with col_search:
        search_query = st.text_input("🔍 Buscar por herramienta, habilidad o palabra clave (ej. CS50, NASA, NVIDIA, Python, n8n, Claude):", "")
    with col_cat:
        cat_filter = st.selectbox("Categoría:", ["Todas"] + categories)
        
    # Build Query
    query = """
    SELECT id, title, category, author, date_added, url, post_url, direct_url_clean,
           ai_what_it_does, ai_how_it_helps, employability_index, employability_details,
           has_certification, recruiter_weight, bolivia_eligible, bolivia_details,
           is_duplicate, duplicate_count, duplicate_sources, found_by_ai, summary
    FROM resources
    WHERE 1=1
    """
    params = []
    
    if search_query:
        query += " AND (title LIKE ? OR summary LIKE ? OR ai_what_it_does LIKE ? OR ai_how_it_helps LIKE ? OR direct_url_clean LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])
    if cat_filter != "Todas":
        query += " AND category = ?"
        params.append(cat_filter)
    if filter_dup:
        query += " AND is_duplicate = 1"
    if filter_high_emp:
        query += " AND employability_index >= 85"
    if filter_cert:
        query += " AND has_certification LIKE '%Certificado%'"
    if filter_bolivia:
        query += " AND bolivia_eligible LIKE '%100% Disponible%'"
        
    query += " ORDER BY employability_index DESC, date_added DESC LIMIT 60"
    
    df_res = pd.read_sql_query(query, conn, params=params)
    st.write(f"Mostrando **{len(df_res)}** recursos encontrados:")
    
    # Render Resources
    for idx, row in df_res.iterrows():
        is_dup = row['is_duplicate'] == 1
        found_by_ai = row['found_by_ai'] == 1
        emp_score = row['employability_index'] or 70
        bolivia_ok = "100%" in (row['bolivia_eligible'] or "")
        
        # Expander Title with Key Badges
        dup_tag = " [⚠️ REPETIDO]" if is_dup else ""
        ai_tag = " [🔍 Link IA]" if found_by_ai else ""
        expander_title = f"{row['category']} | {row['title']}{dup_tag}{ai_tag} — ({emp_score}% Empleabilidad)"
        
        with st.expander(expander_title):
            # 1. BADGES ROW
            badge_html = f"<div style='margin-bottom: 12px;'>"
            badge_html += f"<span class='badge' style='background:#f1f5f9; color:#334155;'>🏷️ {row['category']}</span>"
            
            if is_dup:
                badge_html += f"<span class='badge badge-dup'>⚠️ Repetido ({row['duplicate_count']} publicaciones en tu biblioteca)</span>"
            if found_by_ai:
                badge_html += f"<span class='badge badge-ai'>🔍 Enlace real encontrado por la IA</span>"
                
            if bolivia_ok:
                badge_html += f"<span class='badge badge-bolivia-ok'>{row['bolivia_eligible']}</span>"
            else:
                badge_html += f"<span class='badge badge-bolivia-warn'>{row['bolivia_eligible']}</span>"
                
            badge_html += "</div>"
            st.markdown(badge_html, unsafe_allow_html=True)
            
            # 2. DIRECT ACTION BUTTONS (Clean & Prominent)
            col_act1, col_act2 = st.columns([1, 1])
            with col_act1:
                target_url = row['direct_url_clean'] or row['url']
                st.markdown(f"""
                <a href="{target_url}" target="_blank" class="direct-link-btn">
                    🚀 ABRIR RECURSO REAL DIRECTO
                </a>
                """, unsafe_allow_html=True)
                st.caption(f"Destino directo: `{target_url[:65]}`")
                
            with col_act2:
                if row['post_url'] and "instagram.com" in row['post_url']:
                    st.markdown(f"""
                    <a href="{row['post_url']}" target="_blank" class="post-link-btn">
                        📱 Ver Video/Post Original en Instagram
                    </a>
                    """, unsafe_allow_html=True)
                else:
                    st.caption("Recurso obtenido de chat o enlace directo.")
                    
            st.markdown("---")
            
            # 3. DUAL-MODE PURPOSE & VALUE EXPLANATION
            st.markdown("**🧠 Análisis de Utilidad y Propósito:**")
            st.markdown(f"""
            <div class="box-what">
                <strong>⚙️ ¿Qué es y qué te permite hacer?</strong><br/>
                {row['ai_what_it_does']}
            </div>
            <div class="box-how">
                <strong>🎯 ¿Cómo te ayuda en tu formación (Ing. Industrial + Tech)?</strong><br/>
                {row['ai_how_it_helps']}
            </div>
            """, unsafe_allow_html=True)
            
            # 4. CAREER & EMPLOYABILITY METRICS (GRID)
            st.markdown("**📊 Indicadores de Carrera, Certificación y Mercado:**")
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.markdown(f"**💼 Índice de Empleabilidad:**")
                st.progress(emp_score / 100)
                st.caption(f"**{emp_score}%** | {row['employability_details']}")
            with col_m2:
                st.markdown(f"**📜 Certificación y Peso:**")
                st.markdown(f"• **Tipo:** `{row['has_certification']}`")
                st.markdown(f"• **Peso para Reclutador:** {row['recruiter_weight']}")
            with col_m3:
                st.markdown(f"**🇧🇴 Disponibilidad en Bolivia:**")
                st.markdown(f"• **Estado:** `{row['bolivia_eligible']}`")
                st.caption(f"{row['bolivia_details']}")
                
            st.markdown("---")
            
            # 5. METADATA & REPEATED SOURCES INFO
            col_meta1, col_meta2 = st.columns(2)
            with col_meta1:
                st.caption(f"👤 **Publicado por:** `{row['author']}`")
                st.caption(f"📅 **Fecha de Publicación / Guardado:** `{row['date_added']}`")
            with col_meta2:
                if is_dup and row['duplicate_sources']:
                    with st.expander("🔁 Ver en qué otras publicaciones apareció este recurso:"):
                        sources_list = row['duplicate_sources'].split(" | ")
                        for s in sources_list:
                            st.write(f"• {s}")
                            
            # 6. ORIGINAL TEXT (COLLAPSIBLE)
            with st.expander("📝 Ver pie de foto / texto original del creador"):
                st.text(row['summary'] if row['summary'] else "Sin texto original adicional.")
                
    st.markdown("---")
    st.markdown("### ➕ Añadir Nuevo Enlace o Recurso")
    with st.form("add_new_res_form"):
        f_url = st.text_input("URL del recurso real / página / video:")
        f_title = st.text_input("Título descriptivo:")
        f_cat = st.selectbox("Categoría:", categories if categories else ["🤖 Inteligencia Artificial & Agentes"])
        f_notes = st.text_area("Notas personales:")
        submit_res = st.form_submit_button("Guardar en Segundo Cerebro")
        
        if submit_res and f_url:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            cur.execute("""
            INSERT INTO resources (url, direct_url_clean, post_url, title, summary, ai_what_it_does, ai_how_it_helps,
                                   employability_index, employability_details, has_certification, recruiter_weight,
                                   bolivia_eligible, bolivia_details, category, date_added, source, author, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 80, 'Evaluado manualmente.', 'Por verificar', 'Portafolio',
                    '✅ 100% Disponible en Bolivia', 'Agregado manualmente.', ?, ?, 'Entrada Manual', 'Mark Hazard', 'Pendiente')
            """, (f_url, f_url, f_url, f_title or f_url, f_notes, f"Recurso manual: {f_title}", f_notes, f_cat, now_str))
            conn.commit()
            st.success("¡Recurso añadido exitosamente!")
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
