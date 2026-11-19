import streamlit as st
import plotly.express as px
from utils.conexion import cargar_datos, sidebar_filtros

st.set_page_config(page_title="Valores Atípicos", page_icon="⚠️", layout="wide")
st.title("⚠️ Valores Atípicos")

_, df = cargar_datos()
df_f = sidebar_filtros(df)

Q1  = df_f["valorobservado"].quantile(0.25)
Q3  = df_f["valorobservado"].quantile(0.75)
IQR = Q3 - Q1
lim_inf  = Q1 - 1.5 * IQR
lim_sup  = Q3 + 1.5 * IQR
atipicos = df_f[(df_f["valorobservado"] < lim_inf) | (df_f["valorobservado"] > lim_sup)]

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Total valores atípicos", f"{len(atipicos):,}")
    st.metric("% del dataset", f"{len(atipicos)/len(df_f)*100:.2f}%" if len(df_f) > 0 else "N/A")
    st.metric("Límite inferior (IQR)", f"{lim_inf:.2f} °C")
    st.metric("Límite superior (IQR)", f"{lim_sup:.2f} °C")

with col2:
    if atipicos.empty:
        st.info("No se detectaron valores atípicos con los filtros actuales.")
    else:
        atip_depto = atipicos.groupby("departamento").size().reset_index(name="Atípicos")
        fig_atip = px.bar(
            atip_depto, x="departamento", y="Atípicos", color="departamento",
            title="Valores atípicos por departamento",
            labels={"departamento": "Departamento"},
        )
        fig_atip.update_layout(showlegend=False)
        st.plotly_chart(fig_atip, use_container_width=True)
