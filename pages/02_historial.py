# pages/02_historial.py
# Módulo de historial — consulta de registros por período, finca y tipo
# Permite ver jornales, cosecha e insumos de cualquier mes y año

import streamlit as st
import pandas as pd
from utils.sheets import leer_hoja

st.set_page_config(
    page_title="Historial · Fincas Ureña",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={}
)

# ── Estilos ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap');

[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 1280px; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.navbar {
    background: #123B40;
    border: 1px solid rgba(217,164,65,0.15);
    border-radius: 14px;
    padding: 20px 26px;
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    width: 100%;
}
.navbar-brand .text {
    font-family: 'Fraunces', serif;
    font-size: 22px;
    font-weight: 700;
    color: #F0C36B;
}

.titulo { font-family:'Fraunces',serif; font-size:28px; font-weight:700; color:#F5EFE3; }
.subtitulo { font-size:13px; color:#BFC9C4; margin-top:4px; margin-bottom:24px; }
.seccion { font-family:'Fraunces',serif; font-size:18px; font-weight:600; color:#F5EFE3; margin:24px 0 12px 0; }

.card {
    background: #16454B;
    border: 1px solid rgba(217,164,65,0.12);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 12px;
}

.stat-card {
    background: #16454B;
    border: 1px solid rgba(217,164,65,0.12);
    border-top: 3px solid #D9A441;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 12px;
}
.stat-label { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#BFC9C4; margin-bottom:6px; }
.stat-val { font-family:'Fraunces',serif; font-size:24px; font-weight:700; color:#F5EFE3; }
.stat-sub { font-size:12px; color:#BFC9C4; margin-top:4px; }

.stButton button[kind="primary"] {
    background-color: #D9A441 !important;
    color: #0B2A2E !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
}
.stButton button[kind="secondary"] {
    background-color: transparent !important;
    border: 1.5px solid #D9A441 !important;
    color: #F0C36B !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Navbar ─────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div class="navbar-brand">
        <span style="font-size:20px;">☕</span>
        <span class="text">Fincas Ureña</span>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 3])
with col1:
    if st.button("🏠 Inicio", use_container_width=True, key="nav_inicio"):
        st.switch_page("app.py")
with col2:
    if st.button("⚙️ Panel de Control", use_container_width=True, key="nav_panel"):
        st.switch_page("pages/01_panel_control.py")
with col3:
    if st.button("📋 Historial", use_container_width=True, type="primary", key="nav_historial"):
        st.switch_page("pages/02_historial.py")
with col4:
    if st.button("📊 Cierre Anual", use_container_width=True, key="nav_cierre"):
        st.switch_page("pages/03_cierre_anual.py")

# ── Encabezado ─────────────────────────────────────────────
st.markdown("""
<div class="titulo">📋 Historial de registros</div>
<div class="subtitulo">Consultá jornales, cosecha e insumos por finca y período</div>
""", unsafe_allow_html=True)

# ── Cargar datos ───────────────────────────────────────────
@st.cache_data(ttl=30)
def cargar_todo():
    """Carga todas las hojas necesarias para el historial."""
    return {
        "jornales": leer_hoja("Jornales"),
        "cosecha":  leer_hoja("Cosecha"),
        "insumos":  leer_hoja("Insumos"),
        "lotes":    leer_hoja("Lotes"),
    }

try:
    datos = cargar_todo()
except Exception as e:
    st.error(f"Error conectando con Google Sheets: {e}")
    st.stop()

# ── Selectores de filtro ───────────────────────────────────
st.markdown('<div class="seccion">Filtros</div>', unsafe_allow_html=True)

meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

# Obtener fincas activas
df_lotes = datos["lotes"]
if not df_lotes.empty and "estado" in df_lotes.columns:
    df_lotes["estado"] = pd.to_numeric(df_lotes["estado"], errors="coerce").fillna(1)
    fincas_activas = df_lotes[df_lotes["estado"] == 1]["finca"].tolist()
else:
    fincas_activas = ["La Casa", "El Llano", "El Jocote"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Selector de tipo de registro
    tipo = st.selectbox(
        "Tipo de registro",
        ["Jornales", "Cosecha", "Insumos"],
        key="hist_tipo"
    )

with col2:
    # Selector de finca
    finca_sel = st.selectbox(
        "Finca",
        ["Todas"] + fincas_activas,
        key="hist_finca"
    )

with col3:
    # Selector de mes
    mes_sel = st.selectbox(
        "Mes",
        ["Todos"] + meses,
        key="hist_mes"
    )

with col4:
    # Selector de año
    anio_sel = st.selectbox(
        "Año",
        [2024, 2025, 2026, 2027],
        index=2,
        key="hist_anio"
    )

# ── Aplicar filtros ────────────────────────────────────────
def aplicar_filtros(df, col_fecha="fecha"):
    """
    Filtra el DataFrame según finca, mes y año seleccionados.
    Si se seleccionó 'Todas' o 'Todos' no aplica ese filtro.
    """
    if df.empty or col_fecha not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")

    # Filtro por año siempre activo
    df = df[df[col_fecha].dt.year == anio_sel]

    # Filtro por mes solo si no es "Todos"
    if mes_sel != "Todos":
        num_mes = meses.index(mes_sel) + 1
        df = df[df[col_fecha].dt.month == num_mes]

    # Filtro por finca solo si no es "Todas"
    if finca_sel != "Todas" and "finca" in df.columns:
        df = df[df["finca"] == finca_sel]

    return df

# ── Mostrar resultados ─────────────────────────────────────
st.markdown('<div class="seccion">Resultados</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# JORNALES
# ══════════════════════════════════════════
if tipo == "Jornales":
    df = aplicar_filtros(datos["jornales"])

    if df.empty:
        st.info("No hay jornales para el período seleccionado.")
    else:
        # Calcular totales
        df["horas"]       = pd.to_numeric(df["horas"], errors="coerce")
        df["precio_hora"] = pd.to_numeric(df["precio_hora"], errors="coerce")
        df["pago"]        = df["horas"] * df["precio_hora"]

        # Cards de resumen
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">👥 Total horas</div>
                <div class="stat-val">{df["horas"].sum():.1f} h</div>
                <div class="stat-sub">{len(df)} registros</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card" style="border-top-color:#5FAE7A;">
                <div class="stat-label">💰 Total pagado</div>
                <div class="stat-val">₡{int(df["pago"].sum()):,}</div>
                <div class="stat-sub">en el período</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-card" style="border-top-color:#B79CE8;">
                <div class="stat-label">👤 Peones</div>
                <div class="stat-val">{df["peon"].nunique()}</div>
                <div class="stat-sub">distintos en el período</div>
            </div>""", unsafe_allow_html=True)

        # Tabla detalle
        df_mostrar = df[["fecha","peon","finca","tarea","horas","precio_hora","pago"]].copy()
        df_mostrar["fecha"]       = pd.to_datetime(df_mostrar["fecha"]).dt.strftime("%d/%m/%Y")
        df_mostrar["precio_hora"] = df_mostrar["precio_hora"].apply(lambda x: f"₡{int(x):,}")
        df_mostrar["pago"]        = df_mostrar["pago"].apply(lambda x: f"₡{int(x):,}")
        df_mostrar.columns        = ["Fecha","Peón","Finca","Tarea","Horas","₡/hora","Pago"]
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

        # Resumen por peón
        st.markdown('<div class="seccion">Por peón</div>', unsafe_allow_html=True)
        por_peon = df.groupby("peon").agg(
            Horas=("horas","sum"),
            Pago=("pago","sum")
        ).reset_index()
        por_peon["Pago"] = por_peon["Pago"].apply(lambda x: f"₡{int(x):,}")
        por_peon.columns = ["Peón","Horas","Total pagado"]
        st.dataframe(por_peon, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════
# COSECHA
# ══════════════════════════════════════════
elif tipo == "Cosecha":
    df = aplicar_filtros(datos["cosecha"])

    if df.empty:
        st.info("No hay registros de cosecha para el período seleccionado.")
    else:
        df["cajuelas"]       = pd.to_numeric(df["cajuelas"], errors="coerce")
        df["precio_cajuela"] = pd.to_numeric(df["precio_cajuela"], errors="coerce")
        df["pago"]           = df["cajuelas"] * df["precio_cajuela"]

        total_cajuelas  = round(df["cajuelas"].sum() * 4) / 4
        fanegas_enteras = int(total_cajuelas // 20)
        caj_restantes   = round(total_cajuelas % 20 * 4) / 4

        # Cards de resumen
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">🍒 Total cajuelas</div>
                <div class="stat-val">{total_cajuelas:.2f}</div>
                <div class="stat-sub">{fanegas_enteras} fan y {caj_restantes:.2f} caj</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card" style="border-top-color:#5FAE7A;">
                <div class="stat-label">💰 Total pagado</div>
                <div class="stat-val">₡{int(df["pago"].sum()):,}</div>
                <div class="stat-sub">en el período</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-card" style="border-top-color:#B79CE8;">
                <div class="stat-label">👤 Recolectores</div>
                <div class="stat-val">{df["recolector"].nunique()}</div>
                <div class="stat-sub">distintos en el período</div>
            </div>""", unsafe_allow_html=True)

        # Tabla detalle
        df_mostrar = df[["fecha","recolector","finca","cajuelas","precio_cajuela","pago"]].copy()
        df_mostrar["fecha"]          = pd.to_datetime(df_mostrar["fecha"]).dt.strftime("%d/%m/%Y")
        df_mostrar["precio_cajuela"] = df_mostrar["precio_cajuela"].apply(lambda x: f"₡{int(x):,}")
        df_mostrar["pago"]           = df_mostrar["pago"].apply(lambda x: f"₡{int(x):,}")
        df_mostrar.columns           = ["Fecha","Recolector","Finca","Cajuelas","₡/cajuela","Pago"]
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

        # Resumen por recolector
        st.markdown('<div class="seccion">Por recolector</div>', unsafe_allow_html=True)
        por_rec = df.groupby("recolector").agg(
            Cajuelas=("cajuelas","sum"),
            Pago=("pago","sum")
        ).reset_index()
        por_rec["Cajuelas"] = por_rec["Cajuelas"].apply(lambda x: f"{x:.2f}")
        por_rec["Pago"]     = por_rec["Pago"].apply(lambda x: f"₡{int(x):,}")
        por_rec.columns     = ["Recolector","Cajuelas","Total pagado"]
        st.dataframe(por_rec, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════
# INSUMOS
# ══════════════════════════════════════════
elif tipo == "Insumos":
    df = aplicar_filtros(datos["insumos"])

    if df.empty:
        st.info("No hay registros de insumos para el período seleccionado.")
    else:
        df["costo_total"] = pd.to_numeric(df["costo_total"], errors="coerce")

        # Cards de resumen
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">🌿 Total invertido</div>
                <div class="stat-val">₡{int(df["costo_total"].sum()):,}</div>
                <div class="stat-sub">{len(df)} registros</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card" style="border-top-color:#5FAE7A;">
                <div class="stat-label">📦 Productos</div>
                <div class="stat-val">{df["producto"].nunique()}</div>
                <div class="stat-sub">distintos aplicados</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-card" style="border-top-color:#B79CE8;">
                <div class="stat-label">🌿 Fincas</div>
                <div class="stat-val">{df["finca"].nunique()}</div>
                <div class="stat-sub">con registros</div>
            </div>""", unsafe_allow_html=True)

        # Tabla detalle
        df_mostrar = df[["fecha","producto","finca","cantidad","costo_total"]].copy()
        df_mostrar["fecha"]       = pd.to_datetime(df_mostrar["fecha"]).dt.strftime("%d/%m/%Y")
        df_mostrar["costo_total"] = df_mostrar["costo_total"].apply(lambda x: f"₡{int(x):,}")
        df_mostrar.columns        = ["Fecha","Producto","Finca","Cantidad","Costo total"]
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

        # Resumen por producto
        st.markdown('<div class="seccion">Por producto</div>', unsafe_allow_html=True)
        por_prod = df.groupby("producto").agg(
            Veces=("producto","count"),
            Total=("costo_total","sum")
        ).reset_index()
        por_prod["Total"]  = por_prod["Total"].apply(lambda x: f"₡{int(x):,}")
        por_prod.columns   = ["Producto","Veces aplicado","Total invertido"]
        st.dataframe(por_prod, use_container_width=True, hide_index=True)