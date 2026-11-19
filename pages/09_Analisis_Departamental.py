import streamlit as st
import plotly.express as px
from utils.conexion import cargar_datos, sidebar_filtros

st.set_page_config(page_title="Análisis Departamental", page_icon="🏛️", layout="wide")
st.title("🏛️ Análisis Departamental")

_, df = cargar_datos()
df_f = sidebar_filtros(df)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Temperatura media por departamento")
    temp_depto = (
        df_f.groupby("departamento")["valorobservado"]
        .mean().reset_index()
        .rename(columns={"valorobservado": "temp_media"})
        .sort_values("temp_media", ascending=False)
    )
    fig_depto = px.bar(
        temp_depto, x="departamento", y="temp_media", color="departamento",
        labels={"temp_media": "Temp. media (°C)", "departamento": "Departamento"},
        title="Temperatura media por departamento",
        text="temp_media",
    )
    fig_depto.update_traces(texttemplate="%{text:.2f}°C", textposition="outside")
    fig_depto.update_layout(showlegend=False)
    st.plotly_chart(fig_depto, use_container_width=True)

with col2:
    st.subheader("Participación de registros por departamento")
    reg_depto = (
        df_f.groupby("departamento").size().reset_index(name="Registros")
        .sort_values("Registros", ascending=False)
    )
    fig_pie = px.pie(
        reg_depto, names="departamento", values="Registros",
        title="Participación de registros por departamento",
        hole=0.4,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
st.subheader("Resumen estadístico por departamento")
resumen = (
    df_f.groupby("departamento")["valorobservado"]
    .agg(Registros="count", Media="mean", Mediana="median",
         Desv_std="std", Minimo="min", Maximo="max")
    .round(2).reset_index()
)
st.dataframe(resumen, use_container_width=True, hide_index=True)
