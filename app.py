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
    # Carga datos originales (tabla completa, sin filtrar)
    query_orig = """
        SELECT codigoestacion, fechaobservacion, valorobservado,
               nombreestacion, departamento, municipio,
               zonahidrografica, latitud, longitud
        FROM temperatura_aire
        ORDER BY fechaobservacion;
    """
    # Carga datos limpios (vista con filtros aplicados)
    query_limpia = """
        SELECT codigoestacion, fechaobservacion, valorobservado,
               nombreestacion, departamento, municipio,
               zonahidrografica, latitud, longitud
        FROM temperatura_aire_limpia
        ORDER BY fechaobservacion;
    """
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute(query_orig)
            cols = [desc[0] for desc in cur.description]
            df_orig = pd.DataFrame(cur.fetchall(), columns=cols)

            cur.execute(query_limpia)
            cols = [desc[0] for desc in cur.description]
            df_limpia = pd.DataFrame(cur.fetchall(), columns=cols)

    for df in [df_orig, df_limpia]:
        df["fechaobservacion"] = pd.to_datetime(df["fechaobservacion"])
        df["valorobservado"]   = pd.to_numeric(df["valorobservado"], errors="coerce")
        df["anio"] = df["fechaobservacion"].dt.year
        df["mes"]  = df["fechaobservacion"].dt.month
        df["hora"] = df["fechaobservacion"].dt.hour

    return df_orig, df_limpia


df_orig, df = cargar_datos()

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.header("Filtros")

deptos     = sorted(df["departamento"].dropna().unique())
deptos_sel = st.sidebar.multiselect("Departamento", deptos, default=list(deptos))

munis_disp = sorted(df[df["departamento"].isin(deptos_sel)]["municipio"].dropna().unique())
munis_sel  = st.sidebar.multiselect("Municipio", munis_disp, default=list(munis_disp))

anios     = sorted(df["anio"].dropna().unique())
anio_sel  = st.sidebar.multiselect("Año", anios, default=[a for a in anios if a <= 2019])

df_f = df[
    df["departamento"].isin(deptos_sel) &
    df["municipio"].isin(munis_sel) &
    df["anio"].isin(anio_sel)
]
st.sidebar.markdown(f"**Registros filtrados:** {len(df_f):,}")


# ── 0. Datos y transformaciones ───────────────────────────────────────────────
st.markdown("---")
st.header("0. Datos y Transformaciones")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Información del conjunto de datos")
    st.markdown(f"""
    | | |
    |---|---|
    | **Registros originales (tabla)** | {len(df_orig):,} |
    | **Registros después de depuración (vista)** | {len(df):,} |
    | **Registros eliminados por errores de sensor** | {len(df_orig) - len(df):,} ({(len(df_orig) - len(df)) / len(df_orig) * 100:.1f}%) |
    | **Departamentos** | {df["departamento"].nunique()} |
    | **Municipios** | {df["municipio"].nunique()} |
    | **Estaciones** | {df["codigoestacion"].nunique()} |
    | **Período** | {df["anio"].min()} – {df["anio"].max()} |
    """)

with col2:
    st.subheader("Descripción de las transformaciones")
    transformaciones = pd.DataFrame([
        {
            "Técnica": "Conservación de datos originales",
            "Aplicación": "Los 350,000 registros originales se almacenan intactos en la tabla temperatura_aire.",
            "Justificación": "Garantizar trazabilidad y cumplir el principio de no eliminación de datos."
        },
        {
            "Técnica": "Depuración mediante vista SQL",
            "Aplicación": "Se crea la vista temperatura_aire_limpia filtrando valorobservado > 1 y <= 50 °C, y coordenadas no nulas.",
            "Justificación": "Excluir errores de sensor sin borrar los registros originales."
        },
        {
            "Técnica": "Conversión de tipos",
            "Aplicación": "fechaobservacion se convierte a datetime y valorobservado a numérico.",
            "Justificación": "Permitir operaciones temporales y estadísticas sobre los datos."
        },
        {
            "Técnica": "Extracción de variables temporales",
            "Aplicación": "Se derivan las columnas anio, mes y hora desde fechaobservacion.",
            "Justificación": "Facilitar el análisis estacional y el patrón diario de temperatura."
        },
        {
            "Técnica": "Filtro geográfico interactivo",
            "Aplicación": "El usuario puede filtrar por departamento, municipio y año desde el sidebar.",
            "Justificación": "Permitir análisis focalizados sin modificar los datos almacenados."
        },
    ])
    st.dataframe(transformaciones, use_container_width=True, hide_index=True)

st.subheader("Vista de datos originales vs depurados")
col1, col2 = st.columns(2)
with col1:
    st.caption(f"Datos originales — {len(df_orig):,} registros")
    st.dataframe(df_orig.head(10), use_container_width=True)
with col2:
    st.caption(f"Datos depurados — {len(df):,} registros")
    st.dataframe(df.head(10), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    csv_orig = df_orig.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Descargar datos originales (CSV)",
                       data=csv_orig, file_name="temperatura_original.csv", mime="text/csv")
with col2:
    csv_limpio = df_f.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Descargar datos según filtros (CSV)",
                       data=csv_limpio, file_name="temperatura_filtrada.csv", mime="text/csv")


# ── 1. Resumen General ────────────────────────────────────────────────────────
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


# ── 2. Calidad de Datos ───────────────────────────────────────────────────────
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


# ── 3. Distribución de Temperaturas ──────────────────────────────────────────
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


# ── 4. Valores Atípicos ───────────────────────────────────────────────────────
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


# ── 5. Tendencia Temporal ─────────────────────────────────────────────────────
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


# ── 6. Mapa de Calor de Correlaciones ────────────────────────────────────────
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


# ── 7. Mapa de Estaciones ─────────────────────────────────────────────────────
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


# ── 8. Gráficos de Dispersión ─────────────────────────────────────────────────
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


# ── 9. Análisis Departamental ─────────────────────────────────────────────────
st.markdown("---")
st.header("9. Análisis Departamental")

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
    st.subheader("Registros por departamento")
    reg_depto = (
        df_f.groupby("departamento").size().reset_index(name="Registros")
        .sort_values("Registros", ascending=False)
    )
    fig_reg = px.pie(
        reg_depto, names="departamento", values="Registros",
        title="Participación de registros por departamento",
        hole=0.4,
    )
    st.plotly_chart(fig_reg, use_container_width=True)

st.subheader("Resumen estadístico por departamento")
resumen_depto = (
    df_f.groupby("departamento")["valorobservado"]
    .agg(Registros="count", Media="mean", Mediana="median",
         Desv_std="std", Minimo="min", Maximo="max")
    .round(2).reset_index()
)
st.dataframe(resumen_depto, use_container_width=True, hide_index=True)


# ── 10. Análisis Municipal ────────────────────────────────────────────────────
st.markdown("---")
st.header("10. Análisis Municipal")

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
    top_muni = muni_resumen.head(top_n)
    fig_muni = px.bar(
        top_muni, x="temp_media", y="municipio", color="departamento",
        orientation="h",
        labels={"temp_media": "Temp. media (°C)", "municipio": "Municipio"},
        title=f"Top {top_n} municipios con mayor temperatura media",
        text="temp_media",
    )
    fig_muni.update_traces(texttemplate="%{text:.1f}°C", textposition="outside")
    fig_muni.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_muni, use_container_width=True)

with col2:
    st.subheader(f"Top {top_n} municipios con más registros")
    top_reg_muni = muni_resumen.sort_values("Registros", ascending=False).head(top_n)
    fig_reg_muni = px.bar(
        top_reg_muni, x="Registros", y="municipio", color="departamento",
        orientation="h",
        labels={"Registros": "Cantidad de registros", "municipio": "Municipio"},
        title=f"Top {top_n} municipios con más registros",
        text="Registros",
    )
    fig_reg_muni.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig_reg_muni.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_reg_muni, use_container_width=True)

st.subheader("Todos los municipios analizados")
st.dataframe(
    muni_resumen.rename(columns={
        "departamento": "Departamento", "municipio": "Municipio",
        "temp_media": "Temp. media (°C)", "temp_max": "Temp. máx (°C)",
        "temp_min": "Temp. mín (°C)"
    }),
    use_container_width=True, hide_index=True
)


# ── 11. Muestra de Datos ──────────────────────────────────────────────────────
st.markdown("---")
st.header("11. Muestra de Datos")
st.dataframe(df_f.head(500), use_container_width=True)


# ── 12. Conclusiones ──────────────────────────────────────────────────────────
st.markdown("---")
st.header("12. Conclusiones")

temp_media_gral = df_f["valorobservado"].mean()
depto_mas_calido = df_f.groupby("departamento")["valorobservado"].mean().idxmax()
depto_mas_frio   = df_f.groupby("departamento")["valorobservado"].mean().idxmin()
muni_mas_calido  = df_f.groupby("municipio")["valorobservado"].mean().idxmax()
hora_pico        = df_f.groupby("hora")["valorobservado"].mean().idxmax()
mes_mas_calido   = df_f.groupby("mes")["valorobservado"].mean().idxmax()
n_atipicos       = len(atipicos)
pct_atipicos     = n_atipicos / len(df_f) * 100 if len(df_f) > 0 else 0

col1, col2 = st.columns(2)

with col1:
    st.subheader("Resumen del conjunto analizado")
    st.markdown(f"""
    El análisis abarca **{len(df_f):,} registros** de la Región Caribe colombiana,
    con los filtros seleccionados actualmente.

    - La temperatura media del período es de **{temp_media_gral:.2f} °C**.
    - El departamento más cálido es **{depto_mas_calido}** y el más frío es **{depto_mas_frio}**.
    - El municipio con mayor temperatura media es **{muni_mas_calido}**.
    - La temperatura alcanza su pico alrededor de las **{hora_pico}:00 h**.
    - El mes con mayor temperatura promedio es el **mes {mes_mas_calido}**.
    - Se identificaron **{n_atipicos:,} valores atípicos** ({pct_atipicos:.2f}% del dataset) mediante el método IQR.
    """)

with col2:
    st.subheader("Conclusiones metodológicas")
    st.markdown("""
    1. Se conservó el conjunto de datos original sin eliminar ningún registro de la tabla `temperatura_aire`.
    2. La depuración se realizó mediante una vista SQL (`temperatura_aire_limpia`) que excluye errores de sensor, sin modificar los datos originales.
    3. Se convirtieron las variables temporales (año, mes, hora) para facilitar el análisis estacional y diario.
    4. Se revisaron valores faltantes y registros atípicos sin eliminarlos automáticamente.
    5. Se identificaron posibles valores atípicos mediante el método IQR.
    6. El análisis departamental y municipal permite observar la distribución espacial de la temperatura en la Región Caribe.
    7. El patrón horario muestra un ciclo térmico consistente con el comportamiento esperado para una región tropical.
    8. Los filtros interactivos permiten focalizar el análisis sin modificar los datos almacenados en la base de datos.
    """)
