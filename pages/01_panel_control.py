# pages/01_panel_control.py
# Panel de Control — gestión de Personal y Fincas
# Permite agregar y desactivar peones y fincas
# No borra registros — usa estado 1=activo, 0=inactivo

import streamlit as st
import pandas as pd
from utils.sheets import leer_hoja, get_sheet
from utils.sheets import leer_hoja, get_sheet, leer_precios, actualizar_precio

st.set_page_config(
    page_title="Panel de Control · Fincas Ureña",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={}
)

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
.subtitulo { font-size:13px; color:#BFC9C4; margin-top:4px; margin-bottom:28px; }
.seccion { font-family:'Fraunces',serif; font-size:18px; font-weight:600; color:#F5EFE3; margin:24px 0 12px 0; }

.card {
    background: #16454B;
    border: 1px solid rgba(217,164,65,0.12);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 12px;
}

/* Botón de módulo grande */
.modulo-card {
    background: #16454B;
    border: 1px solid rgba(217,164,65,0.12);
    border-radius: 16px;
    padding: 28px 24px;
    text-align: center;
    margin-bottom: 8px;
}
.modulo-icon { font-size: 36px; margin-bottom: 10px; }
.modulo-nombre { font-family:'Fraunces',serif; font-size:20px; font-weight:600; color:#F5EFE3; }
.modulo-sub { font-size:12px; color:#BFC9C4; margin-top:4px; }

/* Fila de persona/finca */
.fila {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.fila:last-child { border-bottom: none; }
.fila-nombre { font-weight: 600; font-size: 14px; color: #F5EFE3; }
.fila-sub { font-size: 12px; color: #BFC9C4; font-style: italic; }

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

# Botones de navegación
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 3])
with col1:
    if st.button("🏠 Inicio", use_container_width=True, key="nav_inicio"):
        st.switch_page("app.py")
with col2:
    if st.button("⚙️ Panel de Control", use_container_width=True, type="primary", key="nav_panel"):
        st.switch_page("pages/01_panel_control.py")
with col3:
    if st.button("📋 Historial", use_container_width=True, key="nav_historial"):
        st.switch_page("pages/02_historial.py")
with col4:
    if st.button("📊 Cierre Anual", use_container_width=True, key="nav_cierre"):
        st.switch_page("pages/03_cierre_anual.py")

# ── Encabezado ─────────────────────────────────────────────
st.markdown("""
<div class="titulo">⚙️ Panel de Control</div>
<div class="subtitulo">Administración de personal y fincas</div>
""", unsafe_allow_html=True)

# ── Selector de módulo ─────────────────────────────────────
# Guardamos en session_state cuál módulo está abierto
if "modulo_control" not in st.session_state:
    st.session_state["modulo_control"] = None

# Botones grandes para elegir módulo
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="modulo-card">
        <div class="modulo-icon">👥</div>
        <div class="modulo-nombre">Personal</div>
        <div class="modulo-sub">Agregar y desactivar peones</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Entrar a Personal", use_container_width=True,
                 type="primary" if st.session_state["modulo_control"] == "personal" else "secondary",
                 key="btn_personal"):
        st.session_state["modulo_control"] = "personal"
        st.rerun()

with col2:
    st.markdown("""
    <div class="modulo-card">
        <div class="modulo-icon">🌿</div>
        <div class="modulo-nombre">Fincas</div>
        <div class="modulo-sub">Agregar y desactivar fincas</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Entrar a Fincas", use_container_width=True,
                 type="primary" if st.session_state["modulo_control"] == "fincas" else "secondary",
                 key="btn_fincas"):
        st.session_state["modulo_control"] = "fincas"
        st.rerun()

with col3:
    st.markdown("""
    <div class="modulo-card">
        <div class="modulo-icon">💰</div>
        <div class="modulo-nombre">Precios</div>
        <div class="modulo-sub">Editar precio hora y cajuela</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Entrar a Precios", use_container_width=True,
                 type="primary" if st.session_state["modulo_control"] == "precios" else "secondary",
                 key="btn_precios"):
        st.session_state["modulo_control"] = "precios"
        st.rerun()

# ── Funciones de Sheets ────────────────────────────────────

def desactivar_fila(nombre_hoja: str, col_busqueda: str, valor: str, col_estado: str = "estado"):
    """
    Cambia el estado de un registro de 1 a 0.
    Busca la fila donde col_busqueda == valor y actualiza col_estado = 0.
    No elimina el registro — solo lo desactiva.
    """
    hoja       = get_sheet(nombre_hoja)
    datos      = hoja.get_all_records()
    encabezados = hoja.row_values(1)

    # Índice de columnas en Sheets (base 1)
    col_busqueda_idx = encabezados.index(col_busqueda) + 1
    col_estado_idx   = encabezados.index(col_estado) + 1

    # Buscar la fila y actualizar
    for i, fila in enumerate(datos, start=2):
        if str(fila.get(col_busqueda, "")).strip() == str(valor).strip():
            hoja.update_cell(i, col_estado_idx, 0)
            return True
    return False


def agregar_personal(nombre: str, tipo: str):
    """Agrega un peón nuevo con estado=1 (activo)."""
    hoja = get_sheet("Personal")
    hoja.append_row([nombre, tipo, 1])


def agregar_finca(codigo: str, nombre: str, hectareas: float, estado_produccion: str):
    """Agrega una finca nueva con estado=1 (activo)."""
    hoja = get_sheet("Lotes")
    hoja.append_row([codigo, nombre, hectareas, estado_produccion, 1])


# ══════════════════════════════════════════
# MÓDULO PERSONAL
# ══════════════════════════════════════════
if st.session_state["modulo_control"] == "personal":

    st.markdown('<div class="seccion">👥 Personal</div>', unsafe_allow_html=True)

    # Cargar solo peones activos
    try:
        df_personal = leer_hoja("Personal")
        df_personal["estado"] = pd.to_numeric(df_personal["estado"], errors="coerce").fillna(1)
        df_activos = df_personal[df_personal["estado"] == 1].reset_index(drop=True)
    except Exception as e:
        st.error(f"Error cargando personal: {e}")
        st.stop()

    col_tabla, col_form = st.columns([3, 2])

    # ── Lista de peones activos ────────────────────────────
    with col_tabla:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if df_activos.empty:
            st.info("No hay peones activos registrados.")
        else:
            for _, fila in df_activos.iterrows():
                # Fila con nombre, tipo y botón X
                col_n, col_t, col_x = st.columns([3, 2, 1])
                with col_n:
                    st.markdown(f'<div class="fila-nombre">{fila["nombre"]}</div>', unsafe_allow_html=True)
                with col_t:
                    st.markdown(f'<div class="fila-sub">{fila["tipo_peon"]}</div>', unsafe_allow_html=True)
                with col_x:
                    # Botón X para iniciar desactivación
                    if st.button("✕", key=f"des_{fila['nombre']}", help=f"Desactivar {fila['nombre']}"):
                        st.session_state[f"confirmar_{fila['nombre']}"] = True

                # Confirmación de desactivación
                if st.session_state.get(f"confirmar_{fila['nombre']}", False):
                    st.warning(f"¿Desactivar a **{fila['nombre']}**? Se puede reactivar luego.")
                    col_si, col_no = st.columns(2)
                    with col_si:
                        if st.button("✅ Confirmar", key=f"si_{fila['nombre']}"):
                            desactivar_fila("Personal", "nombre", fila["nombre"])
                            st.success(f"{fila['nombre']} desactivado.")
                            st.session_state[f"confirmar_{fila['nombre']}"] = False
                            st.cache_data.clear()
                            st.rerun()
                    with col_no:
                        if st.button("❌ Cancelar", key=f"no_{fila['nombre']}"):
                            st.session_state[f"confirmar_{fila['nombre']}"] = False
                            st.rerun()

                st.divider()

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Formulario agregar peón ────────────────────────────
    with col_form:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="seccion" style="margin-top:0">Agregar peón</div>', unsafe_allow_html=True)

        # Contador para limpiar el form
        if "p_counter" not in st.session_state:
            st.session_state["p_counter"] = 0
        cp = st.session_state["p_counter"]

        p_nombre = st.text_input("Nombre o código", placeholder="Ej: JC, MARIA...", key=f"p_nombre_{cp}")
        p_tipo   = st.selectbox("Tipo", ["Seleccioná el tipo", "dia", "fijo", "familiar"], key=f"p_tipo_{cp}")

        if st.button("➕ Agregar peón", type="primary", use_container_width=True, key=f"btn_agregar_p_{cp}"):
            if not p_nombre:
                st.warning("Escribí el nombre o código del peón.")
            elif p_tipo == "Seleccioná el tipo":
                st.warning("Seleccioná el tipo de peón.")
            else:
                agregar_personal(p_nombre.upper(), p_tipo)
                st.success(f"✅ {p_nombre.upper()} agregado.")
                st.session_state["p_counter"] += 1
                st.cache_data.clear()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# MÓDULO FINCAS
# ══════════════════════════════════════════
elif st.session_state["modulo_control"] == "fincas":

    st.markdown('<div class="seccion">🌿 Fincas</div>', unsafe_allow_html=True)

    # Cargar solo fincas activas
    try:
        df_lotes = leer_hoja("Lotes")
        df_lotes["estado"] = pd.to_numeric(df_lotes["estado"], errors="coerce").fillna(1)
        df_fincas_activas = df_lotes[df_lotes["estado"] == 1].reset_index(drop=True)
    except Exception as e:
        st.error(f"Error cargando fincas: {e}")
        st.stop()

    col_tabla, col_form = st.columns([3, 2])

    # ── Lista de fincas activas ────────────────────────────
    with col_tabla:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if df_fincas_activas.empty:
            st.info("No hay fincas activas registradas.")
        else:
            for _, fila in df_fincas_activas.iterrows():
                col_n, col_h, col_e, col_x = st.columns([3, 1, 2, 1])
                with col_n:
                    st.markdown(f'<div class="fila-nombre">{fila["finca"]}</div>', unsafe_allow_html=True)
                with col_h:
                    st.markdown(f'<div class="fila-sub">{fila["hectareas"]} ha</div>', unsafe_allow_html=True)
                with col_e:
                    st.markdown(f'<div class="fila-sub">{fila["estado_produccion"]}</div>', unsafe_allow_html=True)
                with col_x:
                    if st.button("✕", key=f"des_f_{fila['finca']}", help=f"Desactivar {fila['finca']}"):
                        st.session_state[f"confirmar_f_{fila['finca']}"] = True

                if st.session_state.get(f"confirmar_f_{fila['finca']}", False):
                    st.warning(f"¿Desactivar **{fila['finca']}**?")
                    col_si, col_no = st.columns(2)
                    with col_si:
                        if st.button("✅ Confirmar", key=f"si_f_{fila['finca']}"):
                            desactivar_fila("Lotes", "finca", fila["finca"])
                            st.success(f"{fila['finca']} desactivada.")
                            st.session_state[f"confirmar_f_{fila['finca']}"] = False
                            st.cache_data.clear()
                            st.rerun()
                    with col_no:
                        if st.button("❌ Cancelar", key=f"no_f_{fila['finca']}"):
                            st.session_state[f"confirmar_f_{fila['finca']}"] = False
                            st.rerun()

                st.divider()

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Formulario agregar finca ───────────────────────────
    with col_form:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="seccion" style="margin-top:0">Agregar finca</div>', unsafe_allow_html=True)

        if "f_counter" not in st.session_state:
            st.session_state["f_counter"] = 0
        cf = st.session_state["f_counter"]

        f_codigo    = st.text_input("Código", placeholder="Ej: LC, EL...", key=f"f_codigo_{cf}")
        f_nombre    = st.text_input("Nombre", placeholder="Ej: La Casa", key=f"f_nombre_{cf}")
        f_hectareas = st.number_input("Hectáreas", min_value=0.1, step=0.1, value=1.0, key=f"f_ha_{cf}")
        f_estado    = st.selectbox("Estado", ["produccion", "formacion"], key=f"f_estado_{cf}")

        if st.button("➕ Agregar finca", type="primary", use_container_width=True, key=f"btn_agregar_f_{cf}"):
            if not f_codigo or not f_nombre:
                st.warning("Completá el código y nombre de la finca.")
            else:
                agregar_finca(f_codigo.upper(), f_nombre, f_hectareas, f_estado)
                st.success(f"✅ {f_nombre} agregada.")
                st.session_state["f_counter"] += 1
                st.cache_data.clear()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════
# MÓDULO PRECIOS
# ══════════════════════════════════════════
elif st.session_state["modulo_control"] == "precios":

    st.markdown('<div class="seccion">💰 Precios actuales</div>', unsafe_allow_html=True)

    # Leer precios actuales del Sheet
    try:
        precios = leer_precios()
    except Exception as e:
        st.error(f"Error cargando precios: {e}")
        st.stop()

    precio_hora    = precios.get("precio_hora", 1330)
    precio_cajuela = precios.get("precio_cajuela", 1200)

    col_tabla, col_form = st.columns([3, 2])

    # ── Precios actuales ───────────────────────────────────
    with col_tabla:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        # Precio hora
        col_n, col_v, col_x = st.columns([3, 2, 1])
        with col_n:
            st.markdown('<div class="fila-nombre">Precio por hora</div>', unsafe_allow_html=True)
        with col_v:
            st.markdown(f'<div class="fila-sub">CR{int(precio_hora):,}</div>', unsafe_allow_html=True)
        with col_x:
            if st.button("✏️", key="edit_hora", help="Editar precio hora"):
                st.session_state["editando"] = "precio_hora"

        st.divider()

        # Precio cajuela
        col_n, col_v, col_x = st.columns([3, 2, 1])
        with col_n:
            st.markdown('<div class="fila-nombre">Precio por cajuela</div>', unsafe_allow_html=True)
        with col_v:
            st.markdown(f'<div class="fila-sub">CR{int(precio_cajuela):,}</div>', unsafe_allow_html=True)
        with col_x:
            if st.button("✏️", key="edit_cajuela", help="Editar precio cajuela"):
                st.session_state["editando"] = "precio_cajuela"

        st.divider()
        st.caption(f"Estos precios se aplican automáticamente en los formularios de jornales y cosecha.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Formulario de edición ──────────────────────────────
    with col_form:
        editando = st.session_state.get("editando", None)

        if editando:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            if editando == "precio_hora":
                st.markdown('<div class="seccion" style="margin-top:0">Editar precio hora</div>', unsafe_allow_html=True)
                nuevo_precio = st.number_input(
                    "Nuevo precio por hora (CR)",
                    min_value=0, step=10,
                    value=int(precio_hora),
                    key="nuevo_precio_hora"
                )
            else:
                st.markdown('<div class="seccion" style="margin-top:0">Editar precio cajuela</div>', unsafe_allow_html=True)
                nuevo_precio = st.number_input(
                    "Nuevo precio por cajuela (CR)",
                    min_value=0, step=10,
                    value=int(precio_cajuela),
                    key="nuevo_precio_cajuela"
                )

            col_g, col_c = st.columns(2)
            with col_g:
                if st.button("💾 Guardar", type="primary", use_container_width=True, key="guardar_precio"):
                    actualizar_precio(editando, nuevo_precio)
                    st.success("✅ Precio actualizado.")
                    st.session_state["editando"] = None
                    st.cache_data.clear()
                    st.rerun()
            with col_c:
                if st.button("Cancelar", use_container_width=True, key="cancelar_precio"):
                    st.session_state["editando"] = None
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="text-align:center; padding:40px;">
                <div style="font-size:32px; margin-bottom:12px;">✏️</div>
                <div style="color:#BFC9C4; font-size:13px;">Presioná el botón de editar<br>junto al precio que querés cambiar</div>
            </div>
            """, unsafe_allow_html=True)