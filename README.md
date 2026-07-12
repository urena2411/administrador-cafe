# Administrador Café ☕
### Sistema de gestión agrícola desarrollado con IA

Proyecto de portfolio desarrollado por **Cristhofer Ureña** como parte de su transición hacia **data analytics e IA aplicada**. Demuestra el uso de inteligencia artificial como copiloto de desarrollo para construir herramientas reales de gestión de datos.

---

## 🤖 IA como herramienta de desarrollo

Este proyecto fue construido utilizando **Claude (Anthropic)** como asistente principal de desarrollo — no como generador de código genérico, sino como copiloto técnico que ayudó a:

- Diseñar la arquitectura de datos y el flujo de la aplicación
- Resolver problemas de integración con Google Sheets API
- Optimizar el procesamiento de datos con pandas
- Generar análisis automáticos del rendimiento de las fincas
- Iterar sobre el diseño UI/UX de forma eficiente

El resultado es una herramienta **real y funcional** que una familia cafetalera en Pérez Zeledón, Costa Rica usa para gestionar sus operaciones diarias.

---

## 📊 Stack de datos

| Capa | Tecnología |
|---|---|
| Frontend | Streamlit |
| Procesamiento | Python + pandas |
| Base de datos | Google Sheets via gspread |
| IA / Análisis | Claude API (Anthropic) |
| Exportación | ReportLab (PDF) |
| Deploy | Streamlit Community Cloud |
| Control de versiones | GitHub |

---

## 🌿 Funcionalidades

- **Gestión por finca** — registro de jornales, insumos y cosecha filtrado por finca
- **Cierre semanal automático** — resumen de horas y cajuelas por peón de domingo a sábado
- **Historial** — consulta de registros por período, finca y tipo
- **Cierre anual** — análisis de inversión vs cosecha por ciclo productivo con exportación a PDF
- **Análisis con IA** — observaciones y recomendaciones generadas automáticamente por Claude
- **Panel de control** — gestión de personal, fincas y precios sin tocar código
- **Precios fijos** — precio por hora y cajuela configurables desde el sistema

---

## ⚙️ Configuración

1. Cloná el repositorio
2. Instalá las dependencias: