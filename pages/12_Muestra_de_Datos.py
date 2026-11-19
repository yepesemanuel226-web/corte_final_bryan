import streamlit as st
from utils.conexion import cargar_datos, sidebar_filtros

st.set_page_config(page_title="Muestra de Datos", page_icon="🗃️", layout="wide")
st.title("🗃️ Muestra de Datos")

_, df = cargar_datos()
df_f = sidebar_filtros(df)

st.markdown(f"Mostrando los primeros 500 registros de **{len(df_f):,}** filtrados.")
st.dataframe(df_f.head(500), use_container_width=True)

csv = df_f.to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ Descargar datos según filtros (CSV)",
                   data=csv, file_name="temperatura_filtrada.csv", mime="text/csv")
