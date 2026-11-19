import streamlit as st
import plotly.graph_objects as go
from utils.conexion import cargar_datos, sidebar_filtros

st.set_page_config(page_title="Correlaciones", page_icon="🔗", layout="wide")
st.title("🔗 Mapa de Calor de Correlaciones")

_, df = cargar_datos()
df_f = sidebar_filtros(df)

cols_num = ["valorobservado", "latitud", "longitud", "anio", "mes", "hora"]
corr = df_f[cols_num].corr().round(2)

fig_corr = go.Figure(data=go.Heatmap(
    z=corr.values,
    x=corr.columns.tolist(),
    y=corr.index.tolist(),
    colorscale="RdBu", zmid=0,
    text=corr.values, texttemplate="%{text}",
))
fig_corr.update_layout(title="Correlación entre variables numéricas", height=500)
st.plotly_chart(fig_corr, use_container_width=True)
