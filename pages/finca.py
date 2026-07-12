# pages/finca.py
# Página dinámica por finca — resumen del mes + registro de jornales, insumos, cosecha y suelo
# Se accede desde el panel principal al presionar una finca
# La finca activa se pasa via st.session_state["finca_activa"]

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.sheets import leer_hoja, agregar_fila
from utils.calculos import cajuelas_a_texto, cajuelas_a_fanegas
from utils.sheets import leer_hoja, agregar_fila, leer_precios

st.set_page_config(
    page_title="Finca · Fincas Ureña",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={}
)

# Intentar recuperar la finca desde query params si session_state se perdió
params = st.query_params
if "finca_activa" not in st.session_state and "finca" in params:
    st.session_state["finca_activa"] = params["finca"]

if "finca_activa" not in st.session_state:
    st.warning("Seleccioná una finca desde el panel principal.")
    if st.button("← Volver al panel"):
        st.switch_page("app.py")
    st.stop()

finca = st.session_state["finca_activa"]

# Guardar finca en URL para que sobreviva recargas
st.query_params["finca"] = finca

# ── Estilos ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap');

.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 1280px; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

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
.card-label { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#BFC9C4; margin-bottom:8px; }
.card-valor { font-family:'Fraunces',serif; font-size:26px; font-weight:700; color:#F5EFE3; }
.card-sub { font-size:12px; color:#BFC9C4; margin-top:4px; }

.total-box {
    background: #0B2A2E;
    border: 1px solid rgba(217,164,65,0.2);
    border-radius: 12px;
    padding: 14px 16px;
    margin-top: 6px;
}
.total-label { font-size:11px; color:#BFC9C4; text-transform:uppercase; letter-spacing:0.05em; }
.total-val { font-family:'Fraunces',serif; font-size:24px; font-weight:700; color:#F0C36B; margin-top:4px; }

/* Inputs */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] select {
    background-color: #0E3338 !important;
    border: 1px solid rgba(217,164,65,0.18) !important;
    border-radius: 10px !important;
    color: #F5EFE3 !important;
}

/* Botón primario */
.stButton button[kind="primary"] {
    background-color: #D9A441 !important;
    color: #0B2A2E !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
}
.stButton button[kind="primary"]:hover { background-color: #F0C36B !important; }

/* Botón secundario */
.stButton button[kind="secondary"] {
    background-color: transparent !important;
    border: 1.5px solid #D9A441 !important;
    color: #F0C36B !important;
    border-radius: 10px !important;
}

/* Botón peligro (X) */
.stButton button[kind="tertiary"] {
    background-color: transparent !important;
    border: 1.5px solid #E8896B !important;
    color: #E8896B !important;
    border-radius: 10px !important;
    padding: 4px 10px !important;
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
    if st.button("📋 Historial", use_container_width=True, key="nav_historial"):
        st.switch_page("pages/02_historial.py")
with col4:
    if st.button("📊 Cierre Anual", use_container_width=True, key="nav_cierre"):
        st.switch_page("pages/03_cierre_anual.py")

# ── Encabezado de finca ────────────────────────────────────
iconos = {"La Casa": "☕", "El Llano": "🌱", "El Jocote": "🤝"}
icono  = iconos.get(finca, "🌿")

hoy    = date.today()
meses  = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
          "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

st.markdown(f"""
<div class="titulo">{icono} {finca}</div>
<div class="subtitulo">Registros y resumen · {meses[hoy.month-1]} {hoy.year}</div>
""", unsafe_allow_html=True)

# ── Cargar datos desde Google Sheets ──────────────────────
@st.cache_data(ttl=30)
def cargar_datos():
    # Lee todas las hojas necesarias y las devuelve en un diccionario
    return {
        "personal": leer_hoja("Personal"),
        "jornales": leer_hoja("Jornales"),
        "insumos":  leer_hoja("Insumos"),
        "cosecha":  leer_hoja("Cosecha"),
        "suelos":   leer_hoja("Suelos"),
    }
@st.cache_data(ttl=60)
def cargar_precios():
    """Lee los precios fijos desde Google Sheets."""
    return leer_precios()

precios_actuales    = cargar_precios()
precio_hora_fijo    = int(precios_actuales.get("precio_hora", 1330))
precio_cajuela_fijo = int(precios_actuales.get("precio_cajuela", 1200))

try:
    datos = cargar_datos()
except Exception as e:
    st.error(f"Error conectando con Google Sheets: {e}")
    st.stop()

df_personal = datos["personal"]
df_jornales = datos["jornales"]
df_insumos  = datos["insumos"]
df_cosecha  = datos["cosecha"]
df_suelos   = datos["suelos"]

# ── Filtrar datos del mes actual para esta finca ───────────
def filtrar_mes(df, col_fecha="fecha"):
    """
    Filtra datos por finca y por el mes/año seleccionado en el selector.
    Si el DataFrame está vacío o no tiene las columnas necesarias retorna vacío.
    """
    if df.empty or col_fecha not in df.columns or "finca" not in df.columns:
        return pd.DataFrame()
    df = df.copy()
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")
    return df[
        (df[col_fecha].dt.month == hoy.month) &
        (df[col_fecha].dt.year  == hoy.year) &
        (df["finca"] == finca)
    ]

def filtrar_finca(df, col_fecha="fecha"):
    """
    Filtra datos solo por finca, sin restricción de mes.
    Usado para jornales y cosecha donde el selector de semana maneja el período.
    """
    if df.empty or col_fecha not in df.columns or "finca" not in df.columns:
        return pd.DataFrame()
    df = df.copy()
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")
    return df[df["finca"] == finca]

# filtrar_finca trae todos los datos de la finca sin restricción de mes
# filtrar_mes solo para insumos que sí van por mes actual
j_finca = filtrar_finca(df_jornales)
i_finca = filtrar_finca(df_insumos)
c_finca = filtrar_finca(df_cosecha)

# Para las tarjetas de resumen usamos el mes actual
j_mes = filtrar_mes(df_jornales)
i_mes = filtrar_mes(df_insumos)
c_mes = filtrar_mes(df_cosecha)

# Lista de peones activos para los selectbox
peones = df_personal[
    pd.to_numeric(df_personal["estado"], errors="coerce") == 1
]["nombre"].tolist() if not df_personal.empty else []

# ── Cards de resumen del mes ───────────────────────────────
st.markdown('<div class="seccion">Resumen del mes</div>', unsafe_allow_html=True)

# Calcular totales
gasto_total_insumos = pd.to_numeric(i_finca["costo_total"], errors="coerce").sum() if not i_finca.empty else 0
horas_total   = pd.to_numeric(j_finca["horas"], errors="coerce").sum() if not j_finca.empty else 0
pago_jornales = (pd.to_numeric(j_finca["horas"], errors="coerce") * pd.to_numeric(j_finca["precio_hora"], errors="coerce")).sum() if not j_finca.empty else 0
gasto_insumos = pd.to_numeric(i_mes["costo_total"], errors="coerce").sum() if not i_mes.empty else 0
cajuelas      = round(pd.to_numeric(c_finca["cajuelas"], errors="coerce").sum() * 4) / 4 if not c_finca.empty else 0
fanegas_enteras    = int(cajuelas // 20)
cajuelas_restantes = round(cajuelas % 20 * 4) / 4

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="card" style="border-top:3px solid #D9A441;">
        <div class="card-label">👥 Jornales</div>
        <div class="card-valor">{horas_total:.1f} horas</div>
        <div class="card-sub">Total de horas trabajadas</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card" style="border-top:3px solid #5FAE7A;">
        <div class="card-label">🌿 Insumos</div>
        <div class="card-valor">₡{int(gasto_total_insumos):,}</div>
        <div class="card-sub">Este mes: ₡{int(gasto_insumos):,}</div>
    </div>""", unsafe_allow_html=True)

with col3:
    if finca == "El Jocote":
        st.markdown(f"""
        <div class="card" style="border-top:3px solid #B79CE8;">
            <div class="card-label">🍒 Cosecha</div>
            <div class="card-valor">{cajuelas:.2f} cajuelas</div>
            <div class="card-sub">
                {fanegas_enteras} fan y {cajuelas_restantes:.2f} caj<br>
                Adolfo: {cajuelas/2:.2f} caj · Marvin: {cajuelas/2:.2f} caj
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card" style="border-top:3px solid #D9A441;">
            <div class="card-label">🍒 Cosecha</div>
            <div class="card-valor">{cajuelas:.2f} cajuelas</div>
            <div class="card-sub">{fanegas_enteras} fan y {cajuelas_restantes:.2f} caj</div>
        </div>""", unsafe_allow_html=True)

# ── Tabs de registro ───────────────────────────────────────
st.markdown('<div class="seccion">Registrar</div>', unsafe_allow_html=True)
tab_list = st.tabs(["👥 Jornal", "🌿 Insumo", "🍒 Cosecha", "🧪 Suelo"])

# ════════════════════════════════════════
# TAB JORNAL
# ════════════════════════════════════════
with tab_list[0]:
    # Contador para limpiar el form después de guardar
    if "j_counter" not in st.session_state:
        st.session_state["j_counter"] = 0
    c = st.session_state["j_counter"]

    col1, col2 = st.columns(2)
    with col1:
        j_fecha  = st.date_input("Fecha", value=hoy, key=f"j_fecha_{c}")
        j_peon   = st.selectbox("Peón", ["Seleccioná el peón"] + peones, key=f"j_peon_{c}")
        j_tarea  = st.text_input("Tarea", placeholder="Ej: Fertilización, Chapea...", key=f"j_tarea_{c}")
    with col2:
        j_horas = st.number_input("¿Cuántas horas?", min_value=0.0, max_value=12.0, step=0.5, value=None, placeholder=" ", key=f"j_horas_{c}")
        # Precio fijo desde Panel de Control
        st.markdown(f"""
        <div style="background:#0E3338; border:1px solid rgba(217,164,65,0.18); border-radius:10px; padding:11px 14px; margin-top:4px;">
            <div style="font-size:11px; color:#BFC9C4; margin-bottom:4px;">Precio por hora</div>
            <div style="font-size:16px; font-weight:600; color:#F0C36B;">₡{precio_hora_fijo:,}</div>
            <div style="font-size:10px; color:#6B5040; margin-top:2px;">Editá en Panel de Control → Precios</div>
        </div>
        """, unsafe_allow_html=True)
        j_precio = precio_hora_fijo
        j_total  = (j_horas or 0) * j_precio

    if st.button("💾 Guardar jornal", type="primary", key=f"btn_jornal_{c}"):
        if j_peon == "Seleccioná el peón":
            st.warning("Seleccioná un peón.")
        elif not j_tarea:
            st.warning("Escribí la tarea realizada.")
        elif not j_horas or j_horas == 0:
            st.warning("Ingresá las horas trabajadas.")
        elif not j_precio or j_precio == 0:
            st.warning("Ingresá el precio por hora.")
        else:
            agregar_fila("Jornales", [str(j_fecha), j_peon, finca, j_tarea, j_horas, j_precio])
            st.success(f"✅ Jornal guardado — {j_peon} · {j_horas}h · ₡{int(j_total):,}")
            st.session_state["j_counter"] += 1
            st.cache_data.clear()
            st.rerun()

    # Resumen semanal y tabla del mes
    if not j_finca.empty:
        # Semana actual: domingo a sábado
        # Si hoy es domingo (weekday=6), la semana empieza hoy
        # Si no, retrocedemos al domingo anterior
        dias_desde_domingo = (hoy.weekday() + 1) % 7
        inicio_semana = hoy - timedelta(days=dias_desde_domingo)
        fin_semana    = inicio_semana + timedelta(days=6)  # domingo a sábado

        j_finca["fecha_dt"] = pd.to_datetime(j_finca["fecha"], errors="coerce")
        j_semana = j_finca[
            (j_finca["fecha_dt"] >= pd.Timestamp(inicio_semana)) &
            (j_finca["fecha_dt"] <= pd.Timestamp(fin_semana))
        ]

        if not j_semana.empty:
            st.markdown('<div class="seccion">Cierre semanal</div>', unsafe_allow_html=True)
            resumen = j_semana.copy()
            resumen["total"] = pd.to_numeric(resumen["horas"], errors="coerce") * pd.to_numeric(resumen["precio_hora"], errors="coerce")
            por_peon = resumen.groupby("peon").agg(
                Horas=("horas", lambda x: pd.to_numeric(x, errors="coerce").sum()),
                Total=("total", "sum")
            ).reset_index()
            por_peon["Total"] = por_peon["Total"].apply(lambda x: f"₡{int(x):,}")
            por_peon.columns = ["Peón","Horas semana","Total a pagar"]
            st.dataframe(por_peon, use_container_width=True, hide_index=True)

        st.markdown('<div class="seccion">Jornales Registrados</div>', unsafe_allow_html=True)
        df_j = j_finca[["fecha","peon","tarea","horas","precio_hora"]].copy()
        df_j["total"] = pd.to_numeric(df_j["horas"], errors="coerce") * pd.to_numeric(df_j["precio_hora"], errors="coerce")
        df_j["fecha"] = pd.to_datetime(df_j["fecha"]).dt.strftime("%d/%m/%Y")
        df_j["precio_hora"] = pd.to_numeric(df_j["precio_hora"], errors="coerce").fillna(0).apply(lambda x: f"₡{int(x):,}")
        df_j["total"] = pd.to_numeric(df_j["total"], errors="coerce").fillna(0).apply(lambda x: f"₡{int(x):,}")
        df_j.columns = ["Fecha","Peón","Tarea","Horas","₡/hora","Total"]
        st.dataframe(df_j, use_container_width=True, hide_index=True)

# ════════════════════════════════════════
# TAB INSUMO
# ════════════════════════════════════════
with tab_list[1]:
    if "i_counter" not in st.session_state:
        st.session_state["i_counter"] = 0
    ci = st.session_state["i_counter"]

    col1, col2 = st.columns(2)
    with col1:
        i_fecha    = st.date_input("Fecha", value=hoy, key=f"i_fecha_{ci}")
        i_producto = st.text_input("Producto", placeholder="Ej: Urea 46%, Herbicida...", key=f"i_producto_{ci}")
    with col2:
        i_cantidad = st.number_input("¿Cuánta cantidad?", min_value=0.0, step=0.5, value=None, placeholder=" ", key=f"i_cantidad_{ci}")
        i_costo    = st.number_input("Costo total (₡)", min_value=0, step=1000, value=None, placeholder=" ", key=f"i_costo_{ci}")

    if st.button("💾 Guardar insumo", type="primary", key=f"btn_insumo_{ci}"):
        if not i_producto:
            st.warning("Escribí el nombre del producto.")
        elif not i_cantidad or i_cantidad == 0:
            st.warning("Ingresá la cantidad.")
        elif not i_costo or i_costo == 0:
            st.warning("Ingresá el costo total.")
        else:
            costo_val = int(i_costo or 0)
            cant_val  = float(i_cantidad or 0)
            agregar_fila("Insumos", [str(i_fecha), i_producto, finca, cant_val, costo_val])
            st.success(f"✅ Insumo guardado — {i_producto} · ₡{costo_val:,}")

            st.session_state["i_counter"] += 1
            st.cache_data.clear()
            st.rerun()

    if not i_finca.empty:
        st.markdown('<div class="seccion">Insumos Registrados</div>', unsafe_allow_html=True)
        df_i = i_finca[["fecha","producto","cantidad","costo_total"]].copy()
        df_i["fecha"] = pd.to_datetime(df_i["fecha"]).dt.strftime("%d/%m/%Y")
        df_i["costo_total"] = pd.to_numeric(df_i["costo_total"], errors="coerce").fillna(0).apply(lambda x: f"₡{int(x):,}")
        df_i.columns = ["Fecha","Producto","Cantidad","Costo total"]
        st.dataframe(df_i, use_container_width=True, hide_index=True)

# ════════════════════════════════════════
# TAB COSECHA
# ════════════════════════════════════════
with tab_list[2]:
    if "co_counter" not in st.session_state:
        st.session_state["co_counter"] = 0
    cco = st.session_state["co_counter"]

    col1, col2 = st.columns(2)
    with col1:
        co_fecha      = st.date_input("Fecha", value=hoy, key=f"co_fecha_{cco}")
        co_recolector = st.selectbox("Seleccioná el recolector", ["Seleccioná el recolector"] + peones, key=f"co_recolector_{cco}")
    with col2:
        co_cajuelas = st.number_input("¿Cuántas cajuelas?", min_value=0.0, step=0.25, value=None, placeholder=" ", key=f"co_cajuelas_{cco}")
        # Precio fijo desde Panel de Control
        st.markdown(f"""
        <div style="background:#0E3338; border:1px solid rgba(217,164,65,0.18); border-radius:10px; padding:11px 14px; margin-top:4px;">
            <div style="font-size:11px; color:#BFC9C4; margin-bottom:4px;">Precio por cajuela</div>
            <div style="font-size:16px; font-weight:600; color:#F0C36B;">₡{precio_cajuela_fijo:,}</div>
            <div style="font-size:10px; color:#6B5040; margin-top:2px;">Editá en Panel de Control → Precios</div>
        </div>
        """, unsafe_allow_html=True)
        co_precio = precio_cajuela_fijo
        co_total  = (co_cajuelas or 0) * co_precio

    if finca == "El Jocote" and (co_cajuelas or 0) > 0:
        mitad = (co_cajuelas or 0) / 2
        st.markdown(f"""
        <div class="card" style="border-top:3px solid #B79CE8; margin-top:12px;">
            <div class="card-label">🤝 Sociedad 50/50</div>
            <div class="card-valor">{co_cajuelas:.2f} cajuelas totales</div>
            <div class="card-sub">Adolfo: {mitad:.2f} caj · Marvin: {mitad:.2f} caj</div>
        </div>""", unsafe_allow_html=True)

    if st.button("💾 Guardar cosecha", type="primary", key=f"btn_cosecha_{cco}"):
        if co_recolector == "Seleccioná el recolector":
            st.warning("Seleccioná un recolector.")
        elif not co_cajuelas or co_cajuelas == 0:
            st.warning("Ingresá las cajuelas recolectadas.")
        elif not co_precio or co_precio == 0:
            st.warning("Ingresá el precio por cajuela.")
        else:
            caj_val    = float(co_cajuelas or 0)
            precio_val = int(co_precio or 0)
            total_val  = int(caj_val * precio_val)
            agregar_fila("Cosecha", [str(co_fecha), co_recolector, finca, caj_val, precio_val])
            st.success(f"✅ Cosecha guardada — {caj_val} cajuelas · ₡{total_val:,}")
            st.session_state["co_counter"] += 1
            st.cache_data.clear()
            st.rerun()

    # ── Visualización — siempre visible, fuera del botón ──
    if not c_finca.empty:
        # Crear columna datetime para filtros
        c_finca = c_finca.copy()
        c_finca["fecha_dt"] = pd.to_datetime(c_finca["fecha"], errors="coerce")

        # Cajuelas de hoy
        c_hoy = c_finca[c_finca["fecha_dt"].dt.date == hoy]
        if not c_hoy.empty:
            cajuelas_hoy = round(pd.to_numeric(c_hoy["cajuelas"], errors="coerce").sum() * 4) / 4
            fan_hoy      = int(cajuelas_hoy // 20)
            caj_rest_hoy = round(cajuelas_hoy % 20 * 4) / 4
            st.markdown(f"""
            <div class="card" style="border-top:3px solid #D9A441; margin-top:16px;">
                <div class="card-label">🍒 Cajuelas de hoy</div>
                <div class="card-valor">{cajuelas_hoy:.2f} cajuelas</div>
                <div class="card-sub">{fan_hoy} fan y {caj_rest_hoy:.2f} caj · {hoy.strftime("%d/%m/%Y")}</div>
            </div>""", unsafe_allow_html=True)

        # Semana de domingo a sábado
        # Si hoy es domingo (weekday=6), la semana empieza hoy
        # Si no, retrocedemos al domingo anterior
        dias_desde_domingo = (hoy.weekday() + 1) % 7
        inicio_semana = hoy - timedelta(days=dias_desde_domingo)
        fin_semana    = inicio_semana + timedelta(days=6)  # domingo a sábado
        c_semana = c_finca[
            (c_finca["fecha_dt"] >= pd.Timestamp(inicio_semana)) &
            (c_finca["fecha_dt"] <= pd.Timestamp(fin_semana))
        ]

        if not c_semana.empty:
            st.markdown('<div class="seccion">Cierre semanal</div>', unsafe_allow_html=True)
            c_semana = c_semana.copy()
            c_semana["cajuelas_n"] = pd.to_numeric(c_semana["cajuelas"], errors="coerce").fillna(0)
            c_semana["precio_n"]   = pd.to_numeric(c_semana["precio_cajuela"], errors="coerce").fillna(0)
            c_semana["total"]      = c_semana["cajuelas_n"] * c_semana["precio_n"]
            por_recolector = c_semana.groupby("recolector").agg(
                Cajuelas=("cajuelas_n","sum"),
                Total=("total","sum")
            ).reset_index()
            por_recolector["Total"] = por_recolector["Total"].apply(lambda x: f"₡{int(x):,}")
            por_recolector.columns  = ["Recolector","Cajuelas","Total a pagar"]
            st.dataframe(por_recolector, use_container_width=True, hide_index=True)

            total_semana = round(c_semana["cajuelas_n"].sum() * 4) / 4
            fan_sem      = int(total_semana // 20)
            caj_rest_sem = round(total_semana % 20 * 4) / 4
            st.markdown(f"""
            <div class="card" style="border-top:3px solid #B79CE8;">
                <div class="card-label">Total semana · todas las personas</div>
                <div class="card-valor">{total_semana:.2f} cajuelas</div>
                <div class="card-sub">{fan_sem} fan y {caj_rest_sem:.2f} caj</div>
            </div>""", unsafe_allow_html=True)

        # Tabla completa de cosecha de esta finca
        st.markdown('<div class="seccion">Cosecha registrada</div>', unsafe_allow_html=True)
        df_c = c_finca[["fecha","recolector","cajuelas","precio_cajuela"]].copy()
        df_c["total"] = pd.to_numeric(df_c["cajuelas"], errors="coerce").fillna(0) * pd.to_numeric(df_c["precio_cajuela"], errors="coerce").fillna(0)
        df_c["fecha"] = pd.to_datetime(df_c["fecha"]).dt.strftime("%d/%m/%Y")
        df_c["total"] = df_c["total"].apply(lambda x: f"₡{int(x):,}")
        df_c = df_c[["fecha","recolector","cajuelas","precio_cajuela","total"]]
        df_c.columns = ["Fecha","Recolector","Cajuelas","₡/cajuela","Total"]
        st.dataframe(df_c, use_container_width=True, hide_index=True)
    else:
        st.info("No hay registros de cosecha para esta finca.")

# ════════════════════════════════════════
# TAB SUELO
# ════════════════════════════════════════
with tab_list[3]:
    if "s_counter" not in st.session_state:
        st.session_state["s_counter"] = 0
    cs = st.session_state["s_counter"]

    col1, col2 = st.columns(2)
    with col1:
        s_fecha       = st.date_input("Fecha del análisis", value=hoy, key=f"s_fecha_{cs}")
        s_descripcion = st.text_input("Descripción del análisis de suelo",
                                      placeholder="Ej: Análisis ciclo 2026, pH bajo",
                                      key=f"s_desc_{cs}")
    with col2:
        s_recomend = st.text_area("Recomendaciones del ingeniero",
                                   placeholder="Ej: Encalar 2 sacos por hectárea...",
                                   key=f"s_recom_{cs}")
        s_link     = st.text_input("Link del documento (opcional)",
                                   placeholder="https://drive.google.com/...",
                                   key=f"s_link_{cs}")

    if st.button("💾 Guardar análisis", type="primary", key=f"btn_suelo_{cs}"):
        if not s_descripcion:
            st.warning("Escribí una descripción del análisis.")
        else:
            agregar_fila("Suelos", [str(s_fecha), finca, s_descripcion, s_recomend, s_link])
            st.success("✅ Análisis guardado.")
            st.session_state["s_counter"] += 1
            st.cache_data.clear()
            st.rerun()

    # Historial de análisis de esta finca
    if not df_suelos.empty and "finca" in df_suelos.columns:
        df_s_finca = df_suelos[df_suelos["finca"] == finca]
        if not df_s_finca.empty:
            st.markdown('<div class="seccion">Análisis registrados</div>', unsafe_allow_html=True)
            for _, fila in df_s_finca.iterrows():
                with st.expander(f"📋 {fila['fecha']} — {fila['descripcion']}"):
                    st.markdown(f"**Recomendaciones:** {fila['recomendaciones']}")
                    if fila.get('link_drive') and str(fila.get('link_drive')).startswith("http"):
                        st.markdown(f"[📄 Ver documento]({fila['link_drive']})")
                    else:
                        st.caption("Sin documento adjunto")