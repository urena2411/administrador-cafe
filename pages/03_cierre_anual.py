# pages/03_cierre_anual.py
# Módulo de cierre anual — reporte por ciclo de café
# Ciclo = inversión enero-diciembre + cosecha octubre-febrero siguiente año
# Exportable a PDF con estándares profesionales

import streamlit as st
import pandas as pd
from datetime import date, datetime
from utils.sheets import leer_hoja

st.set_page_config(
    page_title="Cierre Anual · Administrador Café",
    page_icon="📊",
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
    if st.button("📋 Historial", use_container_width=True, key="nav_historial"):
        st.switch_page("pages/02_historial.py")
with col4:
    if st.button("📊 Cierre Anual", use_container_width=True, type="primary", key="nav_cierre"):
        st.switch_page("pages/03_cierre_anual.py")

# ── Encabezado ─────────────────────────────────────────────
st.markdown("""
<div class="titulo">📊 Cierre Anual</div>
<div class="subtitulo">Análisis de inversión y cosecha por ciclo productivo</div>
""", unsafe_allow_html=True)

# ── Selector de ciclo ──────────────────────────────────────
st.markdown('<div class="seccion">Seleccioná el ciclo</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    # Generar años dinámicamente — desde 2024 hasta el año actual + 1
    anio_actual = date.today().year
    anios_disponibles = list(range(2024, anio_actual + 2))

    ciclo = st.selectbox(
        "Ciclo",
        anios_disponibles,
        index=len(anios_disponibles) - 2,  # selecciona el año actual por defecto
        key="ciclo_sel"
    )
with col2:
    # Leer fincas activas desde el Sheet
    try:
        df_lotes = leer_hoja("Lotes")
        df_lotes["estado"] = pd.to_numeric(df_lotes["estado"], errors="coerce").fillna(1)
        fincas_lista = df_lotes[df_lotes["estado"] == 1]["finca"].tolist()
    except Exception:
        fincas_lista = ["La Casa", "El Llano", "El Jocote"]

    finca_sel = st.selectbox(
        "Finca",
        ["Todas"] + fincas_lista,
        key="finca_sel"
    )
    
# ── Cargar datos ───────────────────────────────────────────
@st.cache_data(ttl=60)
def cargar_datos():
    return {
        "jornales": leer_hoja("Jornales"),
        "insumos":  leer_hoja("Insumos"),
        "cosecha":  leer_hoja("Cosecha"),
    }

try:
    datos = cargar_datos()
except Exception as e:
    st.error(f"Error conectando con Google Sheets: {e}")
    st.stop()

# ── Procesar datos del ciclo ───────────────────────────────
def preparar_df(df, col_fecha="fecha"):
    """Convierte fechas y retorna DataFrame limpio."""
    if df.empty or col_fecha not in df.columns:
        return pd.DataFrame()
    df = df.copy()
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")
    return df

df_j = preparar_df(datos["jornales"])
df_i = preparar_df(datos["insumos"])
df_c = preparar_df(datos["cosecha"])

def filtrar_ciclo(df, tipo="inversion"):
    """
    Filtra por ciclo y finca.
    tipo='inversion': enero a diciembre del ciclo
    tipo='cosecha': octubre del ciclo a febrero del ciclo+1
    """
    if df.empty:
        return pd.DataFrame()
    df = df.copy()

    if tipo == "inversion":
        # Inversión: todo el año del ciclo
        df = df[df["fecha"].dt.year == ciclo]
    else:
        # Cosecha: oct-dic del ciclo + ene-feb del siguiente
        df = df[
            ((df["fecha"].dt.year == ciclo) & (df["fecha"].dt.month >= 10)) |
            ((df["fecha"].dt.year == ciclo + 1) & (df["fecha"].dt.month <= 2))
        ]

    # Filtro por finca
    if finca_sel != "Todas" and "finca" in df.columns:
        df = df[df["finca"] == finca_sel]

    return df

j_ciclo = filtrar_ciclo(df_j, "inversion")
i_ciclo = filtrar_ciclo(df_i, "inversion")
c_ciclo = filtrar_ciclo(df_c, "cosecha")

# ── Calcular totales ───────────────────────────────────────
# Jornales
if not j_ciclo.empty:
    j_ciclo["horas"]       = pd.to_numeric(j_ciclo["horas"], errors="coerce").fillna(0)
    j_ciclo["precio_hora"] = pd.to_numeric(j_ciclo["precio_hora"], errors="coerce").fillna(0)
    j_ciclo["pago"]        = j_ciclo["horas"] * j_ciclo["precio_hora"]
    total_jornales = j_ciclo["pago"].sum()
    total_horas    = j_ciclo["horas"].sum()
else:
    total_jornales = total_horas = 0

# Insumos
if not i_ciclo.empty:
    i_ciclo["costo_total"] = pd.to_numeric(i_ciclo["costo_total"], errors="coerce").fillna(0)
    total_insumos = i_ciclo["costo_total"].sum()
else:
    total_insumos = 0

# Cosecha y pago de recolección
if not c_ciclo.empty:
    c_ciclo["cajuelas"]       = pd.to_numeric(c_ciclo["cajuelas"], errors="coerce").fillna(0)
    c_ciclo["precio_cajuela"] = pd.to_numeric(c_ciclo["precio_cajuela"], errors="coerce").fillna(0)
    c_ciclo["pago"]           = c_ciclo["cajuelas"] * c_ciclo["precio_cajuela"]
    total_cajuelas      = round(c_ciclo["cajuelas"].sum() * 4) / 4
    total_recoleccion   = c_ciclo["pago"].sum()
    fanegas_enteras     = int(total_cajuelas // 20)
    cajuelas_restantes  = round(total_cajuelas % 20 * 4) / 4
else:
    total_cajuelas = total_recoleccion = fanegas_enteras = cajuelas_restantes = 0

# Totales consolidados
total_gastos  = total_jornales + total_insumos + total_recoleccion
registros_tot = len(j_ciclo) + len(i_ciclo) + len(c_ciclo)

# ── Resumen ejecutivo ──────────────────────────────────────
st.markdown(f'<div class="seccion">Resumen ejecutivo — Ciclo {ciclo}</div>', unsafe_allow_html=True)
st.caption(f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')} · {registros_tot} registros analizados · Temporada cosecha: oct {ciclo} — feb {ciclo+1}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">💰 Total gastos</div>
        <div class="stat-val">CRC{int(total_gastos):,}</div>
        <div class="stat-sub">inversión + recolección</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="stat-card" style="border-top-color:#5FAE7A;">
        <div class="stat-label">🍒 Cosecha total</div>
        <div class="stat-val">{total_cajuelas:.2f} caj</div>
        <div class="stat-sub">{fanegas_enteras} fan y {cajuelas_restantes:.2f} caj</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="stat-card" style="border-top-color:#B79CE8;">
        <div class="stat-label">👥 Horas trabajadas</div>
        <div class="stat-val">{total_horas:.1f} h</div>
        <div class="stat-sub">jornales del ciclo</div>
    </div>""", unsafe_allow_html=True)
with col4:
    promedio_mensual = total_gastos / 12 if total_gastos > 0 else 0
    st.markdown(f"""
    <div class="stat-card" style="border-top-color:#D9A441;">
        <div class="stat-label">📅 Promedio mensual</div>
        <div class="stat-val">CRC{int(promedio_mensual):,}</div>
        <div class="stat-sub">gasto promedio por mes</div>
    </div>""", unsafe_allow_html=True)

# ── Desglose de gastos ─────────────────────────────────────
st.markdown('<div class="seccion">Desglose de gastos</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    pct_jornales = (total_jornales / total_gastos * 100) if total_gastos > 0 else 0
    st.markdown(f"""
    <div class="card">
        <div class="stat-label">👥 Jornales</div>
        <div class="stat-val">CRC{int(total_jornales):,}</div>
        <div class="stat-sub">{pct_jornales:.1f}% del gasto total</div>
    </div>""", unsafe_allow_html=True)
with col2:
    pct_insumos = (total_insumos / total_gastos * 100) if total_gastos > 0 else 0
    st.markdown(f"""
    <div class="card">
        <div class="stat-label">🌿 Insumos</div>
        <div class="stat-val">CRC{int(total_insumos):,}</div>
        <div class="stat-sub">{pct_insumos:.1f}% del gasto total</div>
    </div>""", unsafe_allow_html=True)
with col3:
    pct_recoleccion = (total_recoleccion / total_gastos * 100) if total_gastos > 0 else 0
    st.markdown(f"""
    <div class="card">
        <div class="stat-label">🍒 Pago recolección</div>
        <div class="stat-val">CRC{int(total_recoleccion):,}</div>
        <div class="stat-sub">{pct_recoleccion:.1f}% del gasto total</div>
    </div>""", unsafe_allow_html=True)

# ── Desglose por finca ─────────────────────────────────────
if finca_sel == "Todas":
    st.markdown('<div class="seccion">Desglose por finca</div>', unsafe_allow_html=True)
    fincas = ["La Casa", "El Llano", "El Jocote"]
    filas_finca = []
    for f in fincas:
        j_f = j_ciclo[j_ciclo["finca"] == f]["pago"].sum() if not j_ciclo.empty and "finca" in j_ciclo.columns else 0
        i_f = i_ciclo[i_ciclo["finca"] == f]["costo_total"].sum() if not i_ciclo.empty and "finca" in i_ciclo.columns else 0
        c_f = c_ciclo[c_ciclo["finca"] == f]["cajuelas"].sum() if not c_ciclo.empty and "finca" in c_ciclo.columns else 0
        r_f = c_ciclo[c_ciclo["finca"] == f]["pago"].sum() if not c_ciclo.empty and "finca" in c_ciclo.columns else 0
        filas_finca.append({
            "Finca": f,
            "Jornales": f"CRC{int(j_f):,}",
            "Insumos": f"CRC{int(i_f):,}",
            "Recolección": f"CRC{int(r_f):,}",
            "Total gastos": f"CRC{int(j_f + i_f + r_f):,}",
            "Cajuelas": f"{round(c_f * 4) / 4:.2f}"
        })
    st.dataframe(pd.DataFrame(filas_finca), use_container_width=True, hide_index=True)

# ── Inversión mensual ──────────────────────────────────────
st.markdown('<div class="seccion">Inversión mensual</div>', unsafe_allow_html=True)

meses_nombres = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
filas_meses = []

for m in range(1, 13):
    j_mes = j_ciclo[j_ciclo["fecha"].dt.month == m]["pago"].sum() if not j_ciclo.empty else 0
    i_mes = i_ciclo[i_ciclo["fecha"].dt.month == m]["costo_total"].sum() if not i_ciclo.empty else 0
    total_mes = j_mes + i_mes
    filas_meses.append({
        "Mes": meses_nombres[m-1],
        "Jornales": f"CRC{int(j_mes):,}",
        "Insumos": f"CRC{int(i_mes):,}",
        "Total": f"CRC{int(total_mes):,}"
    })

st.dataframe(pd.DataFrame(filas_meses), use_container_width=True, hide_index=True)

# ── Detalle cosecha ────────────────────────────────────────
if not c_ciclo.empty:
    st.markdown('<div class="seccion">Detalle de cosecha</div>', unsafe_allow_html=True)
    df_c_mostrar = c_ciclo[["fecha","recolector","finca","cajuelas","precio_cajuela","pago"]].copy()
    df_c_mostrar["fecha"] = df_c_mostrar["fecha"].dt.strftime("%d/%m/%Y")
    df_c_mostrar["pago"]  = df_c_mostrar["pago"].fillna(0).apply(lambda x: f"CRC{int(x):,}")
    df_c_mostrar.columns  = ["Fecha","Recolector","Finca","Cajuelas","CRC/cajuela","Pago"]
    st.dataframe(df_c_mostrar, use_container_width=True, hide_index=True)

# ── Observaciones IA ──────────────────────────────────────
st.markdown('<div class="seccion">🤖 Observaciones automáticas</div>', unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def generar_observaciones(ciclo, finca_sel, total_gastos, total_cajuelas, total_jornales, total_insumos, total_recoleccion, registros):
    """
    Llama a Claude API para generar observaciones del cierre anual.
    Se cachea 1 hora para no gastar tokens innecesariamente.
    """
    import anthropic, json

    import os
    api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")
    cliente = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Sos un agrónomo y asesor financiero experto en fincas cafetaleras de Costa Rica.
Analizá estos datos del ciclo {ciclo} de Fincas Ureña en Pérez Zeledón y generá observaciones útiles.

Datos del ciclo:
- Finca analizada: {finca_sel}
- Total gastos: CRC{int(total_gastos):,}
- Jornales: CRC{int(total_jornales):,} ({(total_jornales/total_gastos*100 if total_gastos > 0 else 0):.1f}%)
- Insumos: CRC{int(total_insumos):,} ({(total_insumos/total_gastos*100 if total_gastos > 0 else 0):.1f}%)
- Pago recolección: CRC{int(total_recoleccion):,} ({(total_recoleccion/total_gastos*100 if total_gastos > 0 else 0):.1f}%)
- Cajuelas cosechadas: {total_cajuelas:.2f}
- Registros totales: {registros}

Respondé SOLO en JSON con esta estructura exacta sin backticks:
{{
    "observaciones": [
        "observación 1 concreta y útil",
        "observación 2 concreta y útil",
        "observación 3 concreta y útil"
    ],
    "recomendacion_principal": "Una recomendación clave para el próximo ciclo"
}}"""

    try:
        respuesta = cliente.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(respuesta.content[0].text.strip())
    except Exception:
        return {
            "observaciones": [
                "Los datos registrados permiten hacer un seguimiento claro de la inversión mensual.",
                "El desglose por tipo de gasto ayuda a identificar dónde se concentra el mayor costo.",
                "Se recomienda mantener el registro continuo para tener comparativas entre ciclos."
            ],
            "recomendacion_principal": "Continuar registrando todos los movimientos para obtener análisis más precisos en el próximo ciclo."
        }

if registros_tot > 0:
    with st.spinner("Generando observaciones..."):
        obs = generar_observaciones(
            ciclo, finca_sel, total_gastos, total_cajuelas,
            total_jornales, total_insumos, total_recoleccion, registros_tot
        )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    for i, o in enumerate(obs["observaciones"], 1):
        st.markdown(f"**{i}.** {o}")
    st.markdown(f"\n**💡 Recomendación principal:** {obs['recomendacion_principal']}")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No hay suficientes datos para generar observaciones en este ciclo.")

# ── Exportar PDF ───────────────────────────────────────────
st.markdown('<div class="seccion">Exportar reporte</div>', unsafe_allow_html=True)

if st.button("📥 Descargar PDF", type="primary"):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.units import inch
    import io

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=letter,
                               topMargin=0.75*inch, bottomMargin=0.75*inch,
                               leftMargin=0.75*inch, rightMargin=0.75*inch)

    # Colores
    VERDE_OSCURO = colors.HexColor("#0B2A2E")
    DORADO       = colors.HexColor("#D9A441")
    CREMA        = colors.HexColor("#F5EFE3")
    GRIS         = colors.HexColor("#6B7280")
    BLANCO       = colors.white

    # Estilos
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle("titulo",
        fontSize=20, fontName="Helvetica-Bold",
        textColor=VERDE_OSCURO, spaceAfter=4)
    estilo_subtitulo = ParagraphStyle("subtitulo",
        fontSize=10, fontName="Helvetica",
        textColor=GRIS, spaceAfter=16, leading=16)
    estilo_seccion = ParagraphStyle("seccion",
        fontSize=13, fontName="Helvetica-Bold",
        textColor=VERDE_OSCURO, spaceBefore=16, spaceAfter=8)
    estilo_normal = ParagraphStyle("normal",
        fontSize=10, fontName="Helvetica",
        textColor=VERDE_OSCURO, spaceAfter=4)
    estilo_obs = ParagraphStyle("obs",
        fontSize=10, fontName="Helvetica",
        textColor=VERDE_OSCURO, spaceAfter=6, leftIndent=12)

    contenido = []

    # Encabezado
    contenido.append(Paragraph(f"Fincas Ureña · Pérez Zeledón · Finca: {finca_sel}", estilo_subtitulo))
    contenido.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", estilo_subtitulo))
    contenido.append(HRFlowable(width="100%", thickness=1.5, color=DORADO, spaceAfter=16))

    # Resumen ejecutivo
    contenido.append(Paragraph("Resumen Ejecutivo", estilo_seccion))
    contenido.append(Paragraph(
        f"Temporada evaluada: Inversión enero–diciembre {ciclo} · "
        f"Cosecha octubre {ciclo} – febrero {ciclo+1}", estilo_normal))
    contenido.append(Paragraph(f"Total de registros analizados: {registros_tot}", estilo_normal))
    contenido.append(Spacer(1, 8))

    datos_resumen = [
        ["Concepto", "Monto", "% del total"],
        ["Total gastos del ciclo", f"CRC{int(total_gastos):,}", "100%"],
        ["  Jornales", f"CRC{int(total_jornales):,}", f"{pct_jornales:.1f}%"],
        ["  Insumos", f"CRC{int(total_insumos):,}", f"{pct_insumos:.1f}%"],
        ["  Pago recolección", f"CRC{int(total_recoleccion):,}", f"{pct_recoleccion:.1f}%"],
        ["Cajuelas cosechadas", f"{total_cajuelas:.2f}", "—"],
        ["Fanegas", f"{fanegas_enteras} fan y {cajuelas_restantes:.2f} caj", "—"],
        ["Promedio mensual gastos", f"CRC{int(promedio_mensual):,}", "—"],
    ]

    tabla_resumen = Table(datos_resumen, colWidths=[3*inch, 2*inch, 1.5*inch])
    tabla_resumen.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), VERDE_OSCURO),
        ("TEXTCOLOR", (0,0), (-1,0), BLANCO),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [CREMA, BLANCO]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("FONTNAME", (0,1), (0,1), "Helvetica-Bold"),
    ]))
    contenido.append(tabla_resumen)

    # Desglose por finca
    if finca_sel == "Todas":
        contenido.append(Paragraph("Desglose por Finca", estilo_seccion))
        datos_finca_pdf = [["Finca","Jornales","Insumos","Recolección","Total","Cajuelas"]]
        for f in fincas:
            j_f = j_ciclo[j_ciclo["finca"] == f]["pago"].sum() if not j_ciclo.empty and "finca" in j_ciclo.columns else 0
            i_f = i_ciclo[i_ciclo["finca"] == f]["costo_total"].sum() if not i_ciclo.empty and "finca" in i_ciclo.columns else 0
            c_f = c_ciclo[c_ciclo["finca"] == f]["cajuelas"].sum() if not c_ciclo.empty and "finca" in c_ciclo.columns else 0
            r_f = c_ciclo[c_ciclo["finca"] == f]["pago"].sum() if not c_ciclo.empty and "finca" in c_ciclo.columns else 0
            datos_finca_pdf.append([f, f"CRC{int(j_f):,}", f"CRC{int(i_f):,}", f"CRC{int(r_f):,}", f"CRC{int(j_f+i_f+r_f):,}", f"{round(c_f*4)/4:.2f}"])

        tabla_finca = Table(datos_finca_pdf, colWidths=[1.2*inch,1.1*inch,1.1*inch,1.1*inch,1.1*inch,0.9*inch])
        tabla_finca.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), VERDE_OSCURO),
            ("TEXTCOLOR", (0,0), (-1,0), BLANCO),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [CREMA, BLANCO]),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
        ]))
        contenido.append(tabla_finca)

    # Inversión mensual
    contenido.append(Paragraph("Inversión Mensual", estilo_seccion))
    datos_meses_pdf = [["Mes","Jornales","Insumos","Total"]]
    for fila in filas_meses:
        datos_meses_pdf.append([fila["Mes"], fila["Jornales"], fila["Insumos"], fila["Total"]])

    tabla_meses = Table(datos_meses_pdf, colWidths=[1.5*inch, 1.8*inch, 1.8*inch, 1.8*inch])
    tabla_meses.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), VERDE_OSCURO),
        ("TEXTCOLOR", (0,0), (-1,0), BLANCO),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [CREMA, BLANCO]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    contenido.append(tabla_meses)

    # Observaciones IA
    if registros_tot > 0:
        contenido.append(Paragraph("Observaciones Automáticas (IA)", estilo_seccion))
        contenido.append(HRFlowable(width="100%", thickness=0.5, color=DORADO, spaceAfter=8))
        for i, o in enumerate(obs["observaciones"], 1):
            contenido.append(Paragraph(f"{i}. {o}", estilo_obs))
        contenido.append(Spacer(1, 6))
        contenido.append(Paragraph(f"Recomendación principal: {obs['recomendacion_principal']}", 
                                   ParagraphStyle("rec", fontSize=10, fontName="Helvetica-Bold",
                                                  textColor=VERDE_OSCURO, leftIndent=12)))

    # Pie de página
    contenido.append(Spacer(1, 20))
    contenido.append(HRFlowable(width="100%", thickness=0.5, color=GRIS, spaceAfter=6))
    contenido.append(Paragraph(
        f"Fincas Ureña · Administrador Café · {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        ParagraphStyle("pie", fontSize=8, fontName="Helvetica", textColor=GRIS, alignment=1)))

    doc.build(contenido)
    buffer.seek(0)

    st.download_button(
        label="📄 Descargar reporte PDF",
        data=buffer,
        file_name=f"cierre_anual_{ciclo}_{finca_sel.replace(' ','_')}.pdf",
        mime="application/pdf"
    )