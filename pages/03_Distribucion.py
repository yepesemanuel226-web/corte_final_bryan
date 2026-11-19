import streamlit as st
import plotly.express as px
from utils.conexion import cargar_datos, sidebar_filtros

st.set_page_config(page_title="Distribución de Temperaturas", page_icon="📈", layout="wide")
st.title("📈 Distribución de Temperaturas")

_, df = cargar_datos()
df_f = sidebar_filtros(df)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Histograma por departamento")
    fig_hist = px.histogram(
        df_f, x="valorobservado", color="departamento",
        nbins=60, barmode="overlay", opacity=0.7,
        labels={"valorobservado": "Temperatura (°C)", "count": "Frecuencia"},
        title="Distribución de temperatura por departamento",
    )
    fig_hist.update_layout(legend_title="Departamento")
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.subheader("Diagrama de caja por departamento")
    fig_box = px.box(
        df_f, x="departamento", y="valorobservado", color="departamento",
        labels={"valorobservado": "Temperatura (°C)", "departamento": "Departamento"},
        title="Boxplot de temperatura por departamento",
    )
    fig_box.update_layout(showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig_box, use_container_width=True)
