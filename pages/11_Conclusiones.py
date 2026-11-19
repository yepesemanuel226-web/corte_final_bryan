import streamlit as st
from utils.conexion import cargar_datos, sidebar_filtros

st.set_page_config(page_title="Conclusiones", page_icon="✅", layout="wide")
st.title("✅ Conclusiones del Análisis Exploratorio")

_, df = cargar_datos()
df_f = sidebar_filtros(df)

# Calcular métricas para las conclusiones dinámicas
Q1       = df_f["valorobservado"].quantile(0.25)
Q3       = df_f["valorobservado"].quantile(0.75)
IQR      = Q3 - Q1
atipicos = df_f[(df_f["valorobservado"] < Q1 - 1.5 * IQR) | (df_f["valorobservado"] > Q3 + 1.5 * IQR)]

temp_media      = df_f["valorobservado"].mean()
depto_calido    = df_f.groupby("departamento")["valorobservado"].mean().idxmax()
depto_frio      = df_f.groupby("departamento")["valorobservado"].mean().idxmin()
muni_calido     = df_f.groupby("municipio")["valorobservado"].mean().idxmax()
hora_pico       = df_f.groupby("hora")["valorobservado"].mean().idxmax()
mes_calido      = df_f.groupby("mes")["valorobservado"].mean().idxmax()
n_atipicos      = len(atipicos)
pct_atipicos    = n_atipicos / len(df_f) * 100 if len(df_f) > 0 else 0

col1, col2 = st.columns(2)

with col1:
    st.subheader("Resumen del conjunto analizado")
    st.markdown(f"""
El análisis abarca **{len(df_f):,} registros** de la Región Caribe colombiana
con los filtros seleccionados actualmente.

- La temperatura media del período es **{temp_media:.2f} °C**.
- El departamento más cálido es **{depto_calido}** y el más frío es **{depto_frio}**.
- El municipio con mayor temperatura media es **{muni_calido}**.
- La temperatura alcanza su pico alrededor de las **{hora_pico}:00 h**.
- El mes con mayor temperatura promedio es el **mes {mes_calido}**.
- Se identificaron **{n_atipicos:,} valores atípicos** ({pct_atipicos:.2f}%) mediante el método IQR.
""")

with col2:
    st.subheader("Conclusiones metodológicas")
    st.markdown("""
1. Se conservó el conjunto de datos original sin eliminar ningún registro de la tabla `temperatura_aire`.
2. La depuración se realizó mediante la vista SQL `temperatura_aire_limpia`, sin modificar los datos originales.
3. Se convirtieron las variables temporales (año, mes, hora) para el análisis estacional y diario.
4. Se revisaron valores faltantes y registros atípicos sin eliminarlos automáticamente.
5. Se identificaron posibles valores atípicos mediante el método IQR.
6. El análisis departamental y municipal revela la distribución espacial de la temperatura en la Región Caribe.
7. El patrón horario muestra un ciclo térmico consistente con el comportamiento esperado para una región tropical.
8. Los filtros interactivos permiten focalizar el análisis sin modificar los datos almacenados en la base de datos.
""")
