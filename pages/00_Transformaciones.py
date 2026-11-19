import streamlit as st
from utils.conexion import cargar_datos

st.set_page_config(page_title="Datos y Transformaciones", page_icon="🔄", layout="wide")
st.title("🔄 Datos y Transformaciones")

df_orig, df = cargar_datos()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Información del conjunto de datos")
    st.markdown(f"""
| | |
|---|---|
| **Registros originales (tabla)** | {len(df_orig):,} |
| **Registros depurados (vista)** | {len(df):,} |
| **Eliminados por errores de sensor** | {len(df_orig) - len(df):,} ({(len(df_orig) - len(df)) / len(df_orig) * 100:.1f}%) |
| **Departamentos** | {df["departamento"].nunique()} |
| **Municipios** | {df["municipio"].nunique()} |
| **Estaciones** | {df["codigoestacion"].nunique()} |
| **Período** | {df["anio"].min()} – {df["anio"].max()} |
""")

with col2:
    st.subheader("Descripción de las transformaciones")
    import pandas as pd
    transformaciones = pd.DataFrame([
        {
            "Técnica": "Conservación de datos originales",
            "Aplicación": "Los 350,000 registros se almacenan intactos en la tabla temperatura_aire.",
            "Justificación": "Garantizar trazabilidad y no eliminación del dato original."
        },
        {
            "Técnica": "Depuración mediante vista SQL",
            "Aplicación": "La vista temperatura_aire_limpia filtra valorobservado > 1 y <= 50 °C, y coordenadas no nulas.",
            "Justificación": "Excluir errores de sensor sin borrar los registros originales."
        },
        {
            "Técnica": "Conversión de tipos",
            "Aplicación": "fechaobservacion a datetime y valorobservado a numérico.",
            "Justificación": "Permitir operaciones temporales y estadísticas."
        },
        {
            "Técnica": "Extracción de variables temporales",
            "Aplicación": "Se derivan anio, mes y hora desde fechaobservacion.",
            "Justificación": "Facilitar el análisis estacional y el patrón diario."
        },
        {
            "Técnica": "Filtro geográfico interactivo",
            "Aplicación": "El usuario filtra por departamento, municipio y año desde el sidebar.",
            "Justificación": "Permitir análisis focalizados sin modificar los datos en BD."
        },
    ])
    st.dataframe(transformaciones, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("Vista de datos originales vs depurados")
col1, col2 = st.columns(2)
with col1:
    st.caption(f"Datos originales — {len(df_orig):,} registros")
    st.dataframe(df_orig.head(10), use_container_width=True)
with col2:
    st.caption(f"Datos depurados — {len(df):,} registros")
    st.dataframe(df.head(10), use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    csv_orig = df_orig.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Descargar datos originales (CSV)",
                       data=csv_orig, file_name="temperatura_original.csv", mime="text/csv")
with col2:
    csv_dep = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Descargar datos depurados (CSV)",
                       data=csv_dep, file_name="temperatura_depurada.csv", mime="text/csv")
