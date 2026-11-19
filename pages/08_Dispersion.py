import streamlit as st
import plotly.express as px
from utils.conexion import cargar_datos, sidebar_filtros

st.set_page_config(page_title="Gráficos de Dispersión", page_icon="🔵", layout="wide")
st.title("🔵 Gráficos de Dispersión")

_, df = cargar_datos()
df_f = sidebar_filtros(df)

muestra = df_f.sample(min(5000, len(df_f)), random_state=42)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Temperatura vs Hora del día")
    fig_sc1 = px.scatter(
        muestra, x="hora", y="valorobservado", color="departamento", opacity=0.5,
        labels={"hora": "Hora del día", "valorobservado": "Temperatura (°C)"},
        title="Relación entre hora del día y temperatura",
    )
    fig_sc1.update_traces(marker=dict(size=4))
    st.plotly_chart(fig_sc1, use_container_width=True)

with col2:
    st.subheader("Temperatura vs Latitud")
    fig_sc2 = px.scatter(
        muestra, x="latitud", y="valorobservado", color="departamento",
        opacity=0.5, trendline="ols",
        labels={"latitud": "Latitud", "valorobservado": "Temperatura (°C)"},
        title="Relación entre latitud y temperatura",
    )
    fig_sc2.update_traces(marker=dict(size=4), selector=dict(mode="markers"))
    st.plotly_chart(fig_sc2, use_container_width=True)
