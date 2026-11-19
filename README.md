# 🌡️ Temperatura Ambiente del Aire – Región Caribe Colombiana

Análisis exploratorio de datos sobre registros de temperatura del aire en los 7 departamentos de la región Caribe colombiana, usando datos abiertos del IDEAM a través del portal datos.gov.co.

| | |
|---|---|
| **Asignatura** | Minería de Datos |
| **Fuente de datos** | [IDEAM – datos.gov.co](https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Temperatura-Ambiente-del-Aire/sbwg-7ju4/about_data) |
| **Período analizado** | 2005 – 2019 |
| **Registros originales** | 350,000 (50,000 por departamento) |
| **Registros limpios** | 332,063 (tras filtrar errores de sensor) |

---

## Tabla de contenidos

1. [Estructura del proyecto](#estructura-del-proyecto)
2. [Instalación](#instalación)
3. [Configuración](#configuración)
4. [Uso paso a paso](#uso-paso-a-paso)
5. [Base de datos en Neon](#base-de-datos-en-neon)
6. [Aplicación Streamlit](#aplicación-streamlit)
7. [Power BI](#power-bi)
8. [Notas sobre los datos](#notas-sobre-los-datos)

---

## Estructura del proyecto

```
corte_final/
│
├── app.py                      # Aplicación Streamlit (EDA interactivo)
├── cargar_datos.py             # Script de carga de datos a PostgreSQL Neon
├── exportar_csv.py             # Script para exportar los datos a CSV
├── check.py                    # Script de verificación de conexión a la BD
├── requirements.txt            # Dependencias del proyecto
├── temperatura_caribe.csv      # Datos exportados
├── .env                        # Variables de entorno (no compartir públicamente)
├── screenshots/                # Capturas de pantalla de la app y Power BI
└── capturas_originales/        # Capturas originales sin renombrar
```

---

## Instalación

**1. Crear el entorno virtual**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**2. Instalar dependencias**

```powershell
pip install -r requirements.txt
```

| Librería | Uso |
|---|---|
| `psycopg[binary]` | Conexión a PostgreSQL Neon |
| `python-dotenv` | Lectura de variables de entorno |
| `requests` | Descarga de datos desde la API de Socrata |
| `pandas` | Manipulación y análisis de datos |
| `streamlit` | Aplicación web interactiva para el EDA |
| `plotly` | Visualizaciones interactivas |
| `statsmodels` | Línea de tendencia OLS en gráficos de dispersión |
| `numpy` | Cálculos numéricos |

---

## Configuración

Crea un archivo `.env` en la raíz del proyecto:

```
DATABASE_URL=postgresql://usuario:contraseña@host/neondb?sslmode=require&channel_binding=require
```

Reemplaza con los datos de conexión de tu proyecto en Neon. Nunca compartas este archivo públicamente.

---

## Uso paso a paso

### Paso 1 — Cargar los datos

Descarga los datos del IDEAM desde datos.gov.co y los carga en la base de datos, departamento por departamento (7 departamentos × 50,000 registros). Todos los registros originales se conservan intactos.

```powershell
python cargar_datos.py
```

Tarda aproximadamente 10–15 minutos. Al finalizar muestra el desglose por departamento.

### Paso 2 — Crear la vista de depuración

Ejecuta este SQL en el editor de Neon para crear la vista que excluye errores de sensor, sin eliminar ningún registro de la tabla original:

```sql
CREATE VIEW temperatura_aire_limpia AS
SELECT
    id, codigoestacion, codigosensor, fechaobservacion,
    valorobservado, nombreestacion, departamento, municipio,
    zonahidrografica, latitud, longitud, descripcionsensor, unidadmedida
FROM temperatura_aire
WHERE
    valorobservado > 1
    AND valorobservado <= 50
    AND latitud IS NOT NULL
    AND longitud IS NOT NULL;
```

Esta vista filtra 17,937 registros con errores de sensor (5.1% del total), dejando la tabla original intacta con sus 350,000 registros.

### Paso 3 — Verificar la carga *(opcional)*

```powershell
python check.py
```

Muestra el conteo de registros por año para confirmar que los datos están correctos.

### Paso 4 — Ejecutar la aplicación

```powershell
streamlit run app.py
```

La aplicación se abre en `http://localhost:8501`.

---

## Base de datos en Neon

| Objeto | Tipo | Registros | Descripción |
|---|---|---|---|
| `temperatura_aire` | Tabla | 350,000 | Datos originales sin modificar |
| `temperatura_aire_limpia` | Vista | 332,063 | Datos depurados sin errores de sensor |

Los registros originales se conservan intactos en la tabla `temperatura_aire`. La depuración se aplica mediante una vista SQL que excluye los errores de sensor sin eliminar ningún registro del conjunto original, cumpliendo el principio de trazabilidad del dato.

---

## Aplicación Streamlit

La app tiene 9 secciones. A continuación se muestra cada una con su captura, una descripción y el código que la construye.

---

### 1. Resumen General

![Resumen General](screenshots/01_resumen_general.png)

Muestra los KPIs principales del dataset filtrado: total de registros, temperatura media, máxima y mínima, número de departamentos, estaciones, municipios y el rango temporal. Los filtros laterales por departamento y año controlan todo el análisis de forma dinámica.

```python
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
```

---

### 2. Calidad de Datos

![Calidad de Datos](screenshots/02_calidad_datos.png)

Dos tablas lado a lado: conteo de valores nulos por columna con su porcentaje sobre el total, y estadísticas descriptivas (count, mean, std, min, percentiles, max) agrupadas por departamento.

```python
col1, col2 = st.columns(2)

with col1:
    nulos = df_f.isnull().sum().reset_index()
    nulos.columns = ["Columna", "Valores nulos"]
    nulos["% del total"] = (nulos["Valores nulos"] / len(df_f) * 100).round(2)
    st.dataframe(nulos, use_container_width=True)

with col2:
    desc = df_f.groupby("departamento")["valorobservado"].describe().round(2)
    st.dataframe(desc, use_container_width=True)
```

---

### 3. Distribución de Temperaturas

![Distribución de Temperaturas](screenshots/03_distribucion_temperaturas.png)

Histograma superpuesto con 60 bins por departamento y diagrama de caja. Permite comparar la forma de la distribución y la dispersión entre los 7 departamentos.

```python
col1, col2 = st.columns(2)

with col1:
    fig_hist = px.histogram(
        df_f, x="valorobservado", color="departamento",
        nbins=60, barmode="overlay", opacity=0.7,
        labels={"valorobservado": "Temperatura (°C)"},
        title="Distribución de temperatura por departamento",
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    fig_box = px.box(
        df_f, x="departamento", y="valorobservado", color="departamento",
        labels={"valorobservado": "Temperatura (°C)"},
        title="Boxplot de temperatura por departamento",
    )
    fig_box.update_layout(showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig_box, use_container_width=True)
```

---

### 4. Valores Atípicos

![Valores Atípicos](screenshots/04_valores_atipicos.png)

Detecta outliers con el método IQR. Los límites se calculan como Q1 − 1.5×IQR y Q3 + 1.5×IQR. Las métricas aparecen a la izquierda y el conteo de atípicos por departamento como gráfico de barras a la derecha.

```python
Q1  = df_f["valorobservado"].quantile(0.25)
Q3  = df_f["valorobservado"].quantile(0.75)
IQR = Q3 - Q1
lim_inf  = Q1 - 1.5 * IQR
lim_sup  = Q3 + 1.5 * IQR
atipicos = df_f[(df_f["valorobservado"] < lim_inf) | (df_f["valorobservado"] > lim_sup)]

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Total valores atípicos", f"{len(atipicos):,}")
    st.metric("% del dataset", f"{len(atipicos)/len(df_f)*100:.2f}%")
    st.metric("Límite inferior (IQR)", f"{lim_inf:.2f} °C")
    st.metric("Límite superior (IQR)", f"{lim_sup:.2f} °C")

with col2:
    atip_depto = atipicos.groupby("departamento").size().reset_index(name="Atípicos")
    fig_atip = px.bar(
        atip_depto, x="departamento", y="Atípicos", color="departamento",
        title="Valores atípicos por departamento",
    )
    st.plotly_chart(fig_atip, use_container_width=True)
```

---

### 5. Tendencia Temporal

![Tendencia Temporal](screenshots/05_tendencia_temporal.png)

Dos gráficos de línea: evolución de la temperatura media mensual por departamento (2005–2019) y el patrón promedio a lo largo de las 24 horas del día, que revela el ciclo térmico diario de cada departamento.

```python
col1, col2 = st.columns(2)

with col1:
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
        title="Evolución mensual de temperatura",
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    temp_hora = (
        df_f.groupby(["hora", "departamento"])["valorobservado"]
        .mean().reset_index()
    )
    fig_hora = px.line(
        temp_hora, x="hora", y="valorobservado", color="departamento",
        title="Patrón diario de temperatura", markers=True,
    )
    fig_hora.update_xaxes(dtick=2)
    st.plotly_chart(fig_hora, use_container_width=True)
```

---

### 6. Mapa de Calor de Correlaciones

![Mapa de Calor de Correlaciones](screenshots/06_mapa_calor_correlaciones.png)

Heatmap con los coeficientes de correlación de Pearson entre las variables numéricas: temperatura, latitud, longitud, año, mes y hora. Escala RdBu centrada en 0 — azul para correlaciones positivas, rojo para negativas.

```python
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
```

---

### 7. Mapa de Estaciones

![Mapa de Estaciones](screenshots/07_mapa_estaciones.png)

Mapa interactivo con las 59 estaciones meteorológicas. Cada punto está coloreado y dimensionado según la temperatura media registrada. Al pasar el cursor se muestra nombre, departamento, municipio y temperatura media.

```python
estaciones = (
    df_f.groupby(["codigoestacion", "nombreestacion", "departamento",
                  "municipio", "latitud", "longitud"])["valorobservado"]
    .mean().reset_index()
    .rename(columns={"valorobservado": "temp_media"})
    .dropna(subset=["latitud", "longitud"])
)

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
)
st.plotly_chart(fig_mapa, use_container_width=True)
```

---

### 8. Gráficos de Dispersión

![Gráficos de Dispersión](screenshots/08_graficos_dispersion.png)

Dos scatter plots sobre una muestra de 5,000 registros: temperatura vs hora del día (izquierda) y temperatura vs latitud con línea de tendencia OLS por departamento calculada con `statsmodels` (derecha).

```python
muestra = df_f.sample(min(5000, len(df_f)), random_state=42)

col1, col2 = st.columns(2)

with col1:
    fig_sc1 = px.scatter(
        muestra, x="hora", y="valorobservado", color="departamento", opacity=0.5,
        title="Relación entre hora del día y temperatura",
    )
    fig_sc1.update_traces(marker=dict(size=4))
    st.plotly_chart(fig_sc1, use_container_width=True)

with col2:
    fig_sc2 = px.scatter(
        muestra, x="latitud", y="valorobservado", color="departamento",
        opacity=0.5, trendline="ols",
        title="Relación entre latitud y temperatura",
    )
    fig_sc2.update_traces(marker=dict(size=4), selector=dict(mode="markers"))
    st.plotly_chart(fig_sc2, use_container_width=True)
```

---

### 9. Muestra de Datos

![Muestra de Datos](screenshots/09_muestra_datos.png)

Tabla interactiva con los primeros 500 registros del dataset filtrado. Permite inspeccionar los datos crudos con todas las columnas: código de estación, fecha, temperatura, departamento, municipio, zona hidrográfica y coordenadas.

```python
st.dataframe(df_f.head(500), use_container_width=True)
```

---

## Power BI

El archivo `temperatura_caribe.pbix` contiene el dashboard interactivo conectado directamente a la vista `temperatura_aire_limpia` en Neon. Al abrirlo pedirá las credenciales de conexión.

### Dashboard principal

![Power BI Dashboard](screenshots/10_powerbi_dashboard.png)

Incluye KPIs de temperatura mínima, media y máxima, temperatura media por departamento, evolución anual 2005–2019, patrón horario diario por departamento y temperatura media por mes.

### Modelo de datos

![Power BI Modelo de Datos](screenshots/12_powerbi_modelo.png)

Vista del modelo en Power BI con todos los campos de `temperatura_aire_limpia` y la medida calculada `Total Registros`.

### Datos cargados

![Power BI Tabla de Datos](screenshots/11_powerbi_tabla_datos.png)

Registros conectados en tiempo real desde Neon, con todos los campos visibles por fila.

---

## Notas sobre los datos

- Los datos provienen de estaciones automáticas del IDEAM con control de calidad básico.
- Se identificaron 17,937 registros con errores de sensor (5.1% del total): valores de temperatura ≤ 1 °C, > 50 °C, o sin coordenadas. Estos registros **no fueron eliminados** de la tabla original — la vista `temperatura_aire_limpia` los excluye al consultar.
- El período con mayor densidad de registros es 2013–2018.
- Córdoba presenta la mayor cantidad de valores atípicos (≈15,000), causados por fallas técnicas en sensores de varias estaciones entre 2010 y 2015. Están presentes en la tabla original pero son excluidos por la vista.
