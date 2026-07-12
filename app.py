# app.py
# Panel principal — entrada a la app por finca
# Nuevo diseño: navbar arriba en vez de sidebar, paleta azul/dorado

import streamlit as st
from datetime import date
from utils.sheets import leer_hoja
import pandas as pd

st.set_page_config(
    page_title="Fincas Ureña",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={}
)

# ── Estilos generales ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap');

.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 1280px; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Navbar */
.navbar {
    background: #123B40;
    border: 1px solid rgba(217,164,65,0.15);
    border-radius: 14px;
    padding: 20px 26px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    width: 100%;
}
.navbar-brand .text {
    font-family: 'Fraunces', serif;
    font-size: 22px;
    font-weight: 700;
    color: #F0C36B;
}
.navbar-brand { display:flex; align-items:center; gap:10px; }
.navbar-brand .text {
    font-family: 'Fraunces', serif;
    font-size: 17px;
    font-weight: 700;
    color: #F0C36B;
}

.titulo {
    font-family: 'Fraunces', serif;
    font-size: 30px;
    font-weight: 700;
    color: #F5EFE3;
}
.subtitulo { font-size: 13px; color: #BFC9C4; margin-top: 4px; margin-bottom: 24px; }

.tip-card {
    background: linear-gradient(120deg, #16454B 0%, #1C5158 100%);
    border: 1px solid rgba(217,164,65,0.2);
    border-radius: 16px;
    padding: 22px 26px;
    margin-bottom: 28px;
    display: flex;
    gap: 16px;
}
.tip-icon {
    font-size: 20px;
    background: rgba(217,164,65,0.15);
    width: 40px; height: 40px;
    border-radius: 10px;
    display:flex; align-items:center; justify-content:center;
    flex-shrink: 0;
}
.tip-titulo { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:#F0C36B; margin-bottom:6px; }
.tip-texto { font-size:14px; line-height:1.6; color:#F5EFE3; }
.tip-fuente { font-size:11px; color:#BFC9C4; margin-top:8px; }

.seccion { font-family:'Fraunces', serif; font-size:19px; font-weight:600; color:#F5EFE3; margin:24px 0 16px 0; }

.finca-card {
    background: #16454B;
    border: 1px solid rgba(217,164,65,0.12);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 8px;
}
.finca-top { display:flex; align-items:center; gap:10px; margin-bottom:12px; }
.finca-icono {
    font-size: 22px;
    background: rgba(217,164,65,0.12);
    width: 42px; height: 42px;
    border-radius: 12px;
    display:flex; align-items:center; justify-content:center;
}
.finca-nombre { font-family:'Fraunces', serif; font-size:18px; font-weight:700; color:#F5EFE3; }

.badge { display:inline-block; font-size:10px; font-weight:700; padding:4px 11px; border-radius:20px; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:16px; }
.badge-prod { background:#173A2C; color:#5FAE7A; }
.badge-form { background:#3A2E12; color:#F0C36B; }
.badge-soc  { background:#2A2440; color:#B79CE8; }

.finca-area { font-size:11px; color:#BFC9C4; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:2px; }
.finca-area-val { font-size:16px; font-weight:700; color:#F5EFE3; }

/* Botones primarios dorados */
.stButton button[kind="primary"] {
    background-color: #D9A441 !important;
    color: #0B2A2E !important;
    border: none !important;
    font-weight: 600 !important;
}
.stButton button[kind="primary"]:hover { background-color: #F0C36B !important; }

/* Botones secundarios */
.stButton button[kind="secondary"] {
    background-color: transparent !important;
    border: 1.5px solid #D9A441 !important;
    color: #F0C36B !important;
}
.stButton button[kind="secondary"]:hover { background-color: rgba(217,164,65,0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ── Navbar ─────────────────────────────────────────────────
# Navbar completo con marca y botones de navegación integrados
st.markdown("""
<div class="navbar">
    <div class="navbar-brand">
        <span style="font-size:20px;">☕</span>
        <span class="text">Fincas Ureña</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Botones de navegación debajo del navbar
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 3])
with col1:
    if st.button("🏠 Inicio", use_container_width=True, key="nav_inicio"):
        st.switch_page("app.py")
with col2:
    if st.button("⚙️ Panel de Control", use_container_width=True, key="nav_panel"):
        st.switch_page("pages/01_panel_control.py")
with col3:
    if st.button("📋 Historial", use_container_width=True, key="nav_historial"):
        st.switch_page("pages/02_historial.py")
with col4:
    if st.button("📊 Cierre Anual", use_container_width=True, key="nav_cierre"):
        st.switch_page("pages/03_cierre_anual.py")

# ── Encabezado ─────────────────────────────────────────────
hoy = date.today()
meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

# Saludo según la hora del día
from datetime import datetime
hora = datetime.now().hour

if hora < 12:
    saludo = "Buenos días ☀️"
elif hora < 19:
    saludo = "Buenas tardes 🌤️"
else:
    saludo = "Buenas noches 🌙"

# Día en español
dias = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
dia_texto = dias[hoy.weekday()]

st.markdown(f"""
<div class="titulo">{saludo}</div>
<div class="subtitulo">{dia_texto} {hoy.day} de {meses[hoy.month-1]} de {hoy.year} · Fincas Ureña · Páramo Pérez Zeledón</div>
""", unsafe_allow_html=True)

# ── Tip del mes ────────────────────────────────────────────
# Cargar contenido desde Claude API — se cachea 12 horas para no gastar tokens
@st.cache_data(ttl=43200)
def cargar_contenido_panel():
    """
    Llama a Claude API una vez cada 12 horas.
    El cache evita llamadas repetidas cada vez que alguien recarga la página.
    """
    from utils.claude_api import get_contenido_panel
    return get_contenido_panel()

contenido = cargar_contenido_panel()

st.markdown(f"""
<div class="tip-card">
    <div class="tip-icon">🤖</div>
    <div>
        <div class="tip-titulo">💡 Dato curioso</div>
        <div class="tip-texto">{contenido['dato_curioso']}</div>
        <div style="margin-top:12px;">
            <div class="tip-titulo">📅 Recomendación de {meses[hoy.month-1]}</div>
            <div class="tip-texto">{contenido['recomendacion']}</div>
        </div>
        <div class="tip-fuente">Fuente: {contenido['fuente']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Fincas ─────────────────────────────────────────────────
st.markdown('<div class="seccion">Seleccioná una finca</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

# Leer fincas activas desde Google Sheets
@st.cache_data(ttl=60)
def cargar_fincas():
    # Solo fincas con estado=1 (activas)
    df = leer_hoja("Lotes")
    if df.empty or "estado" not in df.columns:
        return []
    df["estado"] = pd.to_numeric(df["estado"], errors="coerce").fillna(1)
    return df[df["estado"] == 1].to_dict("records")

# Importar lo necesario
from utils.sheets import leer_hoja
import pandas as pd

# Configuración visual por finca
config_fincas = {
    "La Casa":   ("☕", "badge-prod", "Producción"),
    "El Llano":  ("🌱", "badge-form", "En formación"),
    "El Jocote": ("🤝", "badge-soc",  "Sociedad 50/50"),
}

try:
    fincas_data = cargar_fincas()
except Exception:
    fincas_data = []

# Mostrar tarjetas
cols = st.columns(len(fincas_data) if fincas_data else 3)

for i, finca_row in enumerate(fincas_data):
    nombre = finca_row.get("finca", "")
    area   = finca_row.get("hectareas", "—")
    icono, badge_class, badge_text = config_fincas.get(nombre, ("🌿", "badge-prod", "Activa"))

    with cols[i]:
        st.markdown(f"""
        <div class="finca-card">
            <div class="finca-top">
                <div class="finca-icono">{icono}</div>
                <div class="finca-nombre">{nombre}</div>
            </div>
            <span class="badge {badge_class}">{badge_text}</span>
            <div class="finca-area">Área</div>
            <div class="finca-area-val">{area} ha</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Entrar a {nombre} →", key=f"btn_{nombre}", use_container_width=True, type="secondary"):
            st.session_state["finca_activa"] = nombre
            st.query_params["finca"] = nombre
            st.switch_page("pages/finca.py")