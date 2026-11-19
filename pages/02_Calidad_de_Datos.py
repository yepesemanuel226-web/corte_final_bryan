import streamlit as st
from utils.conexion import cargar_datos, sidebar_filtros

st.set_page_config(page_title="Calidad de Datos", page_icon="🔍", layout="wide")
st.title("🔍 Calidad de Datos")

_, df = cargar_datos()
df_f = sidebar_filtros(df)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Valores faltantes")
    nulos = df_f.isnull().sum().reset_index()
    nulos.columns = ["Columna", "Valores nulos"]
    nulos["% del total"] = (nulos["Valores nulos"] / len(df_f) * 100).round(2)
    st.dataframe(nulos, use_container_width=True)

with col2:
    st.subheader("Estadísticas descriptivas – Temperatura (°C)")
    desc = df_f.groupby("departamento")["valorobservado"].describe().round(2)
    st.dataframe(desc, use_container_width=True)
