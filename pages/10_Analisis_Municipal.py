import streamlit as st
import plotly.express as px
from utils.conexion import cargar_datos, sidebar_filtros

st.set_page_config(page_title="Análisis Municipal", page_icon="🏘️", layout="wide")
st.title("🏘️ Análisis Municipal")

_, df = cargar_datos()
df_f = sidebar_filtros(df)

top_n = st.slider("Cantidad de municipios a visualizar", min_value=5, max_value=30, value=15)

muni_resumen = (
    df_f.groupby(["departamento", "municipio"])["valorobservado"]
    .agg(Registros="count", temp_media="mean", temp_max="max", temp_min="min")
    .round(2).reset_index()
    .sort_values("temp_media", ascending=False)
)

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Top {top_n} municipios por temperatura media")
    top_temp = muni_resumen.head(top_n)
    fig_temp = px.bar(
        top_temp, x="temp_media", y="municipio", color="departamento",
        orientation="h",
        labels={"temp_media": "Temp. media (°C)", "municipio": "Municipio"},
        title=f"Top {top_n} municipios con mayor temperatura media",
        text="temp_media",
    )
    fig_temp.update_traces(texttemplate="%{text:.1f}°C", textposition="outside")
    fig_temp.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    st.subheader(f"Top {top_n} municipios con más registros")
    top_reg = muni_resumen.sort_values("Registros", ascending=False).head(top_n)
    fig_reg = px.bar(
        top_reg, x="Registros", y="municipio", color="departamento",
        orientation="h",
        labels={"Registros": "Cantidad de registros", "municipio": "Municipio"},
        title=f"Top {top_n} municipios con más registros",
        text="Registros",
    )
    fig_reg.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig_reg.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_reg, use_container_width=True)

st.markdown("---")
st.subheader("Todos los municipios analizados")
st.dataframe(
    muni_resumen.rename(columns={
        "departamento": "Departamento", "municipio": "Municipio",
        "temp_media": "Temp. media (°C)", "temp_max": "Temp. máx (°C)",
        "temp_min": "Temp. mín (°C)"
    }),
    use_container_width=True, hide_index=True
)
