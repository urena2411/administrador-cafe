# utils/claude_api.py
# Conexión con Claude API para generar el dato curioso y recomendación del mes
# Solo se usa en el panel principal para controlar costos

import anthropic
import streamlit as st
from datetime import date

def get_contenido_panel() -> dict:
    """
    Llama a Claude API y retorna un dato curioso del café costarricense
    y una recomendación técnica según el mes actual.
    Retorna un diccionario con 'dato_curioso', 'recomendacion' y 'fuente'.
    Si falla, retorna contenido de respaldo para no romper la app.
    """

    # Mes actual en español para el prompt
    meses = ["enero","febrero","marzo","abril","mayo","junio",
             "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    mes_actual = meses[date.today().month - 1]

    # Contenido de respaldo si la API falla
    respaldo = {
        "dato_curioso": "Costa Rica fue el primer país centroamericano en cultivar café comercialmente, iniciando exportaciones en 1820.",
        "recomendacion": f"En {mes_actual} es importante monitorear la humedad del suelo y mantener el control de malezas.",
        "fuente": "ICAFÉ"
    }

    try:
        # Inicializar cliente con la key guardada en secrets
        cliente = anthropic.Anthropic(
            api_key=st.secrets["ANTHROPIC_API_KEY"]
        )

        # Prompt para Claude
        prompt = f"""Eres un agrónomo experto en café costarricense. 
Responde ÚNICAMENTE en formato JSON con esta estructura exacta, sin texto adicional ni backticks:
{{
    "dato_curioso": "Una oración interesante sobre el café costarricense o de Pérez Zeledón",
    "recomendacion": "Una recomendación técnica específica para fincas cafetaleras en el mes de {mes_actual} en Costa Rica",
    "fuente": "La fuente de la recomendación (ICAFÉ, PROCOMER, MAG, etc)"
}}"""

        # Llamada a la API
        respuesta = cliente.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        # Extraer y parsear el JSON de la respuesta
        import json
        texto = respuesta.content[0].text.strip()
        datos = json.loads(texto)

        return datos

    except Exception as e:
        # Si algo falla, retornar contenido de respaldo
        return respaldo