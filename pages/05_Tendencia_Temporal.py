import pandas as pd
import streamlit as st
import plotly.express as px
from utils.conexion import cargar_datos, sidebar_filtros

st.set_page_config(page_title="Tendencia Temporal", page_icon="📅", layout="wide")
st.title("📅 Tendencia Temporal")

_, df = cargar_datos()
df_f = sidebar_filtros(df)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Temperatura media mensual por departamento")
    temp_mensual = (
        df_f.groupby(["anio", "mes", "departamento"])["valorobservado"]
        .mean().reset_index()
    )
    temp_mensual["fecha"] = pd.to_datetime(
        temp_mensual["anio"].astype(str) + "-" +
        temp_mensual["mes"].astype(str).str.zfill(2) + "-01"
    )
    fig_line = px.line(
        temp_mensual, x="fecha", y="valorobservado", color="departamento",
        labels={"valorobservado": "Temp. media (°C)", "fecha": "Fecha"},
        title="Evolución mensual de temperatura",
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.subheader("Temperatura media por hora del día")
    temp_hora = (
        df_f.groupby(["hora", "departamento"])["valorobservado"]
        .mean().reset_index()
    )
    fig_hora = px.line(
        temp_hora, x="hora", y="valorobservado", color="departamento",
        labels={"valorobservado": "Temp. media (°C)", "hora": "Hora del día"},
        title="Patrón diario de temperatura",
        markers=True,
    )
    fig_hora.update_xaxes(dtick=2)
    st.plotly_chart(fig_hora, use_container_width=True)
