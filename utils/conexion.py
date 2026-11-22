import os
import pandas as pd
import psycopg
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


@st.cache_data(show_spinner="Cargando datos desde Neon...")
def cargar_datos():
    query_orig = """
        SELECT codigoestacion, fechaobservacion, valorobservado,
               nombreestacion, departamento, municipio,
               zonahidrografica, latitud, longitud
        FROM temperatura_aire
        ORDER BY fechaobservacion;
    """
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
            cols = [d[0] for d in cur.description]
            df_orig = pd.DataFrame(cur.fetchall(), columns=cols)

            cur.execute(query_limpia)
            cols = [d[0] for d in cur.description]
            df = pd.DataFrame(cur.fetchall(), columns=cols)

    for frame in [df_orig, df]:
        frame["fechaobservacion"] = pd.to_datetime(frame["fechaobservacion"])
        frame["valorobservado"]   = pd.to_numeric(frame["valorobservado"], errors="coerce")
        frame["anio"] = frame["fechaobservacion"].dt.year
        frame["mes"]  = frame["fechaobservacion"].dt.month
        frame["hora"] = frame["fechaobservacion"].dt.hour

    return df_orig, df


def aplicar_filtros(df, deptos_sel, munis_sel, anio_sel):
    return df[
        df["departamento"].isin(deptos_sel) &
        df["municipio"].isin(munis_sel) &
        df["anio"].isin(anio_sel)
    ]


def sidebar_filtros(df):
    st.sidebar.header("Filtros")

    deptos     = sorted(df["departamento"].dropna().unique())
    deptos_sel = st.sidebar.multiselect("Departamento", deptos, default=list(deptos))

    munis_disp = sorted(df[df["departamento"].isin(deptos_sel)]["municipio"].dropna().unique())
    munis_sel  = st.sidebar.multiselect("Municipio", munis_disp, default=list(munis_disp))

    anios     = sorted(df["anio"].dropna().unique())
    anio_sel  = st.sidebar.multiselect("Año", anios, default=[a for a in anios if a <= 2019])

    df_f = aplicar_filtros(df, deptos_sel, munis_sel, anio_sel)
    st.sidebar.markdown(f"**Registros filtrados:** {len(df_f):,}")

    return df_f
