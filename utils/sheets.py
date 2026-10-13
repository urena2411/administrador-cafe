# utils/sheets.py
# Conexión a Google Sheets y funciones de lectura/escritura
# Este archivo es el puente entre la app y la base de datos

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

# ── Configuración ──────────────────────────────────────────
# ID del Google Sheet (el que copiaste de la URL)
SHEET_ID = "10JrXrIY-xr1VPDiD5igG5WcphBX1YFRRNc_OQ0o8BE0"

# Permisos que necesitamos para leer y escribir
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── Conexión ───────────────────────────────────────────────
@st.cache_resource
def get_client():
    """
    Crea la conexión con Google Sheets.
    Se ejecuta una sola vez y se reutiliza (cache).
    """
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def get_sheet(nombre_hoja: str):
    """
    Retorna una hoja específica del libro.
    Ejemplo: get_sheet("Jornales")
    """
    client = get_client()
    libro = client.open_by_key(SHEET_ID)
    return libro.worksheet(nombre_hoja)

# ── Lectura ────────────────────────────────────────────────
def leer_hoja(nombre_hoja: str) -> pd.DataFrame:
    hoja = get_sheet(nombre_hoja)
    datos = hoja.get_all_records()
    df = pd.DataFrame(datos)
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        try:
            df[col] = df[col].astype(str).str.strip()
        except Exception:
            pass
    return df
# ── Escritura ──────────────────────────────────────────────
def agregar_fila(nombre_hoja: str, fila: list):
    """
    Agrega una fila nueva al final de la hoja.
    Ejemplo: agregar_fila("Jornales", ["2026-06-24", "JC", "La Casa", ...])
    """
    hoja = get_sheet(nombre_hoja)
    hoja.append_row(fila)

def leer_precios() -> dict:
    """
    Lee los precios desde la hoja Precios.
    Retorna un diccionario con todos los precios disponibles.
    Ejemplo: {'precio_hora_1': 1300, 'precio_hora_2': 1500, ...}
    """
    try:
        hoja  = get_sheet("Precios")
        datos = hoja.get_all_records()
        precios = {}
        for fila in datos:
            precios[str(fila["concepto"]).strip()] = float(fila["precio"])
        return precios
    except Exception:
        # Valores por defecto si falla la conexión
        return {
            "precio_hora_1": 1300,
            "precio_hora_2": 1500,
            "precio_hora_3": 1700,
            "precio_cajuela_1": 1200,
            "precio_cajuela_2": 1300,
            "precio_cajuela_3": 1400,
        }


def actualizar_precio(concepto: str, nuevo_precio: float):
    """
    Actualiza el precio de un concepto en la hoja Precios.
    concepto: 'precio_hora' o 'precio_cajuela'
    nuevo_precio: el nuevo valor a guardar
    """
    hoja        = get_sheet("Precios")
    encabezados = hoja.row_values(1)
    datos       = hoja.get_all_records()

    col_precio = encabezados.index("precio") + 1
    for i, fila in enumerate(datos, start=2):
        if str(fila.get("concepto", "")).strip() == concepto:
            hoja.update_cell(i, col_precio, nuevo_precio)
            return True
    return False