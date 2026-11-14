import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import psycopg
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Temperatura Caribe Colombiano",
    page_icon="🌡️",
    layout="wide",
)

st.title("🌡️ Análisis Exploratorio de Datos")
st.subheader("Temperatura Ambiente del Aire – Región Caribe Colombiana")
st.markdown("**Fuente:** IDEAM · datos.gov.co · 350,000 registros (50,000 por departamento)")


@st.cache_data(show_spinner="Cargando datos desde Neon...")
def cargar_datos():
    query = """
        SELECT codigoestacion, fechaobservacion, valorobservado,
               nombreestacion, departamento, municipio,
               zonahidrografica, latitud, longitud
        FROM temperatura_aire_limpia
        ORDER BY fechaobservacion;
    """
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=cols)
    df["fechaobservacion"] = pd.to_datetime(df["fechaobservacion"])
    df["valorobservado"]   = pd.to_numeric(df["valorobservado"], errors="coerce")
    df["anio"] = df["fechaobservacion"].dt.year
    df["mes"]  = df["fechaobservacion"].dt.month
    df["hora"] = df["fechaobservacion"].dt.hour
    return df


df = cargar_datos()

st.sidebar.header("Filtros")
deptos    = sorted(df["departamento"].dropna().unique())
deptos_sel = st.sidebar.multiselect("Departamento", deptos, default=list(deptos))
anios     = sorted(df["anio"].dropna().unique())
anio_sel  = st.sidebar.multiselect("Año", anios, default=[a for a in anios if a <= 2019])

df_f = df[df["departamento"].isin(deptos_sel) & df["anio"].isin(anio_sel)]
st.sidebar.markdown(f"**Registros filtrados:** {len(df_f):,}")


st.markdown("---")
st.header("1. Resumen General")

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


st.markdown("---")
st.header("2. Calidad de Datos")

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


st.markdown("---")
st.header("3. Distribución de Temperaturas")

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


st.markdown("---")
st.header("4. Valores Atípicos")

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


st.markdown("---")
st.header("5. Tendencia Temporal")

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


st.markdown("---")
st.header("6. Mapa de Calor de Correlaciones")

cols_num = ["valorobservado", "latitud", "longitud", "anio", "mes", "hora"]
corr = df_f[cols_num].corr().round(2)

fig_corr = go.Figure(data=go.Heatmap(
    z=corr.values,
    x=corr.columns.tolist(),
    y=corr.index.tolist(),
    colorscale="RdBu", zmid=0,
    text=corr.values, texttemplate="%{text}",
))
fig_corr.update_layout(title="Correlación entre variables numéricas", height=450)
st.plotly_chart(fig_corr, use_container_width=True)


st.markdown("---")
st.header("7. Mapa de Estaciones")

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


st.markdown("---")
st.header("8. Gráficos de Dispersión")

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


st.markdown("---")
st.header("9. Muestra de Datos")
st.dataframe(df_f.head(500), use_container_width=True)
