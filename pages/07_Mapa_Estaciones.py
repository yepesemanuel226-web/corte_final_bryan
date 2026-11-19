import streamlit as st
import plotly.express as px
from utils.conexion import cargar_datos, sidebar_filtros

st.set_page_config(page_title="Mapa de Estaciones", page_icon="🗺️", layout="wide")
st.title("🗺️ Mapa de Estaciones")

_, df = cargar_datos()
df_f = sidebar_filtros(df)

estaciones = (
    df_f.groupby(["codigoestacion", "nombreestacion", "departamento",
                  "municipio", "latitud", "longitud"])["valorobservado"]
    .mean().reset_index()
    .rename(columns={"valorobservado": "temp_media"})
    .dropna(subset=["latitud", "longitud"])
)

if estaciones.empty:
    st.warning("No hay estaciones con coordenadas para los filtros seleccionados.")
else:
    fig_mapa = px.scatter_map(
        estaciones, lat="latitud", lon="longitud",
        color="temp_media", size="temp_media",
        hover_name="nombreestacion",
        hover_data={"departamento": True, "municipio": True,
                    "temp_media": ":.2f", "latitud": False, "longitud": False},
        color_continuous_scale="YlOrRd",
        map_style="carto-positron",
        zoom=5, center={"lat": 9.5, "lon": -74.5},
        title="Temperatura media por estación meteorológica",
        labels={"temp_media": "Temp. media (°C)"},
    )
    st.plotly_chart(fig_mapa, use_container_width=True)
