import streamlit as st
from utils.conexion import cargar_datos, sidebar_filtros

st.set_page_config(page_title="Resumen General", page_icon="📊", layout="wide")
st.title("📊 Resumen General")

_, df = cargar_datos()
df_f = sidebar_filtros(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total registros",    f"{len(df_f):,}")
col2.metric("Temperatura media",  f"{df_f['valorobservado'].mean():.2f} °C")
col3.metric("Temperatura máxima", f"{df_f['valorobservado'].max():.2f} °C")
col4.metric("Temperatura mínima", f"{df_f['valorobservado'].min():.2f} °C")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Departamentos", f"{df_f['departamento'].nunique()}")
col6.metric("Estaciones",    f"{df_f['codigoestacion'].nunique()}")
col7.metric("Municipios",    f"{df_f['municipio'].nunique()}")
col8.metric("Rango temporal",
            f"{df_f['fechaobservacion'].min().year} – {df_f['fechaobservacion'].max().year}")
