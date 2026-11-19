import streamlit as st
from utils.conexion import cargar_datos

st.set_page_config(
    page_title="Temperatura Caribe Colombiano",
    page_icon="🌡️",
    layout="wide",
)

st.title("🌡️ Temperatura Ambiente del Aire")
st.subheader("Región Caribe Colombiana – Análisis Exploratorio de Datos")

st.markdown("""
Esta aplicación presenta un análisis exploratorio de los registros de temperatura del aire
en los 7 departamentos de la región Caribe colombiana, usando datos abiertos del IDEAM
disponibles en el portal datos.gov.co.
""")

st.markdown("---")

col1, col2, col3 = st.columns(3)
col1.info("**Fuente:** IDEAM – datos.gov.co")
col2.info("**Período:** 2005 – 2019")
col3.info("**Registros originales:** 350,000")

col4, col5, col6 = st.columns(3)
col4.info("**Registros depurados:** 332,063")
col5.info("**Departamentos:** 7")
col6.info("**Base de datos:** PostgreSQL (Neon)")

st.markdown("---")
st.subheader("📋 Secciones del análisis")

secciones = [
    ("0️⃣", "Datos y Transformaciones",    "Datos originales vs depurados, tabla de transformaciones y descarga."),
    ("1️⃣", "Resumen General",             "KPIs principales: temperatura media, máxima, mínima y cobertura."),
    ("2️⃣", "Calidad de Datos",            "Valores faltantes y estadísticas descriptivas por departamento."),
    ("3️⃣", "Distribución de Temperaturas","Histograma y diagrama de caja por departamento."),
    ("4️⃣", "Valores Atípicos",            "Detección de outliers mediante el método IQR."),
    ("5️⃣", "Tendencia Temporal",          "Evolución mensual 2005–2019 y patrón horario diario."),
    ("6️⃣", "Correlaciones",               "Mapa de calor de correlaciones entre variables numéricas."),
    ("7️⃣", "Mapa de Estaciones",          "Ubicación geográfica de las 59 estaciones meteorológicas."),
    ("8️⃣", "Dispersión",                  "Temperatura vs hora del día y vs latitud con tendencia OLS."),
    ("9️⃣", "Análisis Departamental",      "Temperatura media, registros y estadísticas por departamento."),
    ("🔟", "Análisis Municipal",           "Ranking de municipios por temperatura y cantidad de registros."),
    ("🔚", "Conclusiones",                 "Hallazgos del análisis y conclusiones metodológicas."),
]

for icono, titulo, desc in secciones:
    st.markdown(f"**{icono} {titulo}** — {desc}")

st.markdown("---")
st.caption("Asignatura: Minería de Datos · Usa el menú lateral para navegar entre secciones.")

# Pre-carga los datos en caché para que las páginas respondan rápido
with st.spinner("Precargando datos..."):
    cargar_datos()

st.success("✅ Datos cargados. Selecciona una sección en el menú lateral izquierdo.")
