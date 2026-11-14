# Temperatura Ambiente del Aire – Región Caribe Colombiana

Análisis exploratorio de datos sobre registros de temperatura del aire en los 7 departamentos
de la región Caribe colombiana, usando datos abiertos del IDEAM a través del portal datos.gov.co.

**Asignatura:** Minería de Datos  
**Fuente de datos:** [IDEAM – datos.gov.co](https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Temperatura-Ambiente-del-Aire/sbwg-7ju4/about_data)  
**Período analizado:** 2005 – 2019  
**Total de registros originales:** 350,000 (50,000 por departamento)  
**Total de registros limpios:** 332,063 (después de filtrar errores de sensor)

---

## Estructura del proyecto

```
corte_final/
│
├── app.py                  # Aplicación Streamlit (EDA interactivo)
├── cargar_datos.py         # Script de carga de datos a PostgreSQL Neon
├── exportar_csv.py         # Script para exportar los datos a CSV
├── check.py                # Script de verificación de conexión a la BD
├── requirements.txt        # Dependencias del proyecto
├── temperatura_caribe.csv  # Datos exportados
├── .env                    # Variables de entorno (no compartir públicamente)
└── README.md               # Este archivo
```

---

## Requisitos previos

- Python 3.11 o superior
- Cuenta en [Neon](https://neon.tech) con una base de datos PostgreSQL activa
- Power BI Desktop instalado
- Conexión a internet (los datos se descargan desde datos.gov.co)

---

## Instalación

### 1. Descargar el proyecto

Descarga todos los archivos en una carpeta local.

### 2. Crear el entorno virtual (recomendado)

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias

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

Crea un archivo `.env` en la raíz del proyecto con la siguiente variable:

```
DATABASE_URL=postgresql://usuario:contraseña@host/neondb?sslmode=require&channel_binding=require
```

Reemplaza con los datos de conexión de tu proyecto en Neon. Nunca compartas este archivo públicamente.

---

## Uso

### Paso 1 – Cargar los datos en PostgreSQL Neon

Descarga los datos del IDEAM desde datos.gov.co y los carga en la base de datos,
departamento por departamento (7 departamentos, 50,000 registros cada uno).

```powershell
python cargar_datos.py
```

Tarda aproximadamente 10-15 minutos. Al finalizar muestra el desglose por departamento.

### Paso 2 – Crear la vista de datos limpios

Una vez cargados los datos, ejecuta este SQL en el editor de Neon para crear
la vista que excluye los errores de sensor sin borrar los registros originales:

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

Esta vista filtra 17,937 registros con errores de sensor (5.1% del total),
manteniendo la tabla original intacta.

### Paso 3 – Verificar la carga (opcional)

```powershell
python check.py
```

Muestra el conteo de registros por año para confirmar que los datos están correctos.

### Paso 4 – Ejecutar la aplicación Streamlit

```powershell
streamlit run app.py
```

La aplicación se abre en el navegador en `http://localhost:8501` y usa la vista
`temperatura_aire_limpia` para todos los análisis.

Secciones de la app:

1. Resumen General — KPIs principales
2. Calidad de Datos — valores faltantes y estadísticas descriptivas
3. Distribución de Temperaturas — histograma y diagrama de caja
4. Valores Atípicos — detección por método IQR
5. Tendencia Temporal — evolución mensual y patrón diario
6. Mapa de Calor de Correlaciones
7. Mapa de Estaciones — ubicación geográfica de las estaciones
8. Gráficos de Dispersión — temperatura vs hora y vs latitud
9. Muestra de Datos — tabla interactiva

---

## Capturas de pantalla

### Aplicación Streamlit

---

#### 1. Resumen General

![Resumen General](screenshots/01_resumen_general.png)

Muestra los KPIs principales del dataset filtrado: total de registros, temperatura media, máxima y mínima, número de departamentos, estaciones, municipios y el rango temporal. Los filtros laterales por departamento y año controlan todo el análisis de forma dinámica.

```python
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
```

---

#### 2. Calidad de Datos

![Calidad de Datos](screenshots/02_calidad_datos.png)

Presenta dos tablas lado a lado: la primera muestra el conteo de valores nulos por columna con su porcentaje sobre el total, y la segunda muestra las estadísticas descriptivas (count, mean, std, min, percentiles, max) agrupadas por departamento.

```python
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
```

---

#### 3. Distribución de Temperaturas

![Distribución de Temperaturas](screenshots/03_distribucion_temperaturas.png)

Histograma superpuesto con 60 bins por departamento (izquierda) y diagrama de caja (derecha). Permite comparar visualmente la forma de la distribución y la dispersión de temperaturas entre los 7 departamentos del Caribe.

```python
st.header("3. Distribución de Temperaturas")

col1, col2 = st.columns(2)

with col1:
    fig_hist = px.histogram(
        df_f, x="valorobservado", color="departamento",
        nbins=60, barmode="overlay", opacity=0.7,
        labels={"valorobservado": "Temperatura (°C)", "count": "Frecuencia"},
        title="Distribución de temperatura por departamento",
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    fig_box = px.box(
        df_f, x="departamento", y="valorobservado", color="departamento",
        labels={"valorobservado": "Temperatura (°C)", "departamento": "Departamento"},
        title="Boxplot de temperatura por departamento",
    )
    fig_box.update_layout(showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig_box, use_container_width=True)
```

---

#### 4. Valores Atípicos

![Valores Atípicos](screenshots/04_valores_atipicos.png)

Detecta outliers usando el método IQR (rango intercuartílico). Calcula los límites inferior y superior como Q1 − 1.5×IQR y Q3 + 1.5×IQR, muestra las métricas clave a la izquierda y un gráfico de barras con el conteo de atípicos por departamento a la derecha.

```python
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

#### 5. Tendencia Temporal

![Tendencia Temporal](screenshots/05_tendencia_temporal.png)

Dos gráficos de línea: el de la izquierda muestra la temperatura media mensual por departamento a lo largo de todo el período 2005–2019, y el de la derecha muestra el patrón promedio a lo largo de las horas del día, revelando el ciclo térmico diario de cada departamento.

```python
st.header("5. Tendencia Temporal")

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
        labels={"valorobservado": "Temp. media (°C)", "fecha": "Fecha"},
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
        labels={"valorobservado": "Temp. media (°C)", "hora": "Hora del día"},
        title="Patrón diario de temperatura",
        markers=True,
    )
    fig_hora.update_xaxes(dtick=2)
    st.plotly_chart(fig_hora, use_container_width=True)
```

---

#### 6. Mapa de Calor de Correlaciones

![Mapa de Calor de Correlaciones](screenshots/06_mapa_calor_correlaciones.png)

Heatmap con los coeficientes de correlación de Pearson entre las variables numéricas del dataset: temperatura observada, latitud, longitud, año, mes y hora. Usa escala de color RdBu centrada en 0 para distinguir correlaciones positivas (azul) de negativas (rojo).

```python
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
```

---

#### 7. Mapa de Estaciones

![Mapa de Estaciones](screenshots/07_mapa_estaciones.png)

Mapa interactivo con la ubicación geográfica de las 59 estaciones meteorológicas. Cada punto está coloreado y dimensionado según la temperatura media registrada. Al pasar el cursor sobre una estación se muestra su nombre, departamento, municipio y temperatura media.

```python
st.header("7. Mapa de Estaciones")

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
    hover_data={"departamento": True, "municipio": True, "temp_media": ":.2f",
                "latitud": False, "longitud": False},
    color_continuous_scale="YlOrRd",
    map_style="carto-positron",
    zoom=5, center={"lat": 9.5, "lon": -74.5},
    title="Temperatura media por estación meteorológica",
)
st.plotly_chart(fig_mapa, use_container_width=True)
```

---

#### 8. Gráficos de Dispersión

![Gráficos de Dispersión](screenshots/08_graficos_dispersion.png)

Dos scatter plots sobre una muestra aleatoria de 5,000 registros. El de la izquierda analiza la relación entre la hora del día y la temperatura. El de la derecha analiza la relación entre latitud y temperatura, incluyendo una línea de tendencia OLS por departamento calculada con `statsmodels`.

```python
st.header("8. Gráficos de Dispersión")

muestra = df_f.sample(min(5000, len(df_f)), random_state=42)

col1, col2 = st.columns(2)

with col1:
    fig_sc1 = px.scatter(
        muestra, x="hora", y="valorobservado", color="departamento", opacity=0.5,
        labels={"hora": "Hora del día", "valorobservado": "Temperatura (°C)"},
        title="Relación entre hora del día y temperatura",
    )
    fig_sc1.update_traces(marker=dict(size=4))
    st.plotly_chart(fig_sc1, use_container_width=True)

with col2:
    fig_sc2 = px.scatter(
        muestra, x="latitud", y="valorobservado", color="departamento",
        opacity=0.5, trendline="ols",
        labels={"latitud": "Latitud", "valorobservado": "Temperatura (°C)"},
        title="Relación entre latitud y temperatura",
    )
    fig_sc2.update_traces(marker=dict(size=4), selector=dict(mode="markers"))
    st.plotly_chart(fig_sc2, use_container_width=True)
```

---

#### 9. Muestra de Datos

![Muestra de Datos](screenshots/09_muestra_datos.png)

Tabla interactiva con los primeros 500 registros del dataset filtrado. Permite inspeccionar directamente los datos crudos con todas las columnas: código de estación, fecha, temperatura, departamento, municipio, zona hidrográfica y coordenadas.

```python
st.header("9. Muestra de Datos")
st.dataframe(df_f.head(500), use_container_width=True)
```

---

### Power BI

---

#### Dashboard principal

![Power BI Dashboard](screenshots/10_powerbi_dashboard.png)

Dashboard conectado directamente a la vista `temperatura_aire_limpia` en Neon. Incluye KPIs de temperatura mínima, media y máxima, un gráfico de barras con la temperatura media por departamento, la evolución anual 2005–2019, el patrón horario diario por departamento y la temperatura media por mes del año.

---

#### Modelo de datos

![Power BI Modelo de Datos](screenshots/12_powerbi_modelo.png)

Vista del modelo de datos en Power BI mostrando la tabla `public temperatura_aire_limpia` con todos sus campos: estación, sensor, fecha, temperatura, departamento, municipio, zona hidrográfica, coordenadas y la medida calculada `Total Registros`.

---

#### Datos cargados

![Power BI Tabla de Datos](screenshots/11_powerbi_tabla_datos.png)

Vista de los registros en Power BI conectados en tiempo real a la vista de Neon, con todos los campos visibles por fila: código de estación, sensor, fecha de observación, temperatura observada, nombre de estación, departamento, municipio, zona hidrográfica y coordenadas.

---

## Power BI

El archivo `temperatura_caribe.pbix` contiene el dashboard interactivo conectado
directamente a la vista `temperatura_aire_limpia` en Neon.

Para que funcione necesitas tener acceso a la base de datos con las credenciales configuradas.
Al abrir el archivo Power BI pedirá las credenciales de conexión a Neon.

> Las capturas del dashboard y el modelo de datos están en la sección [Capturas de pantalla → Power BI](#power-bi-1).

---

## Base de datos – Estructura en Neon

La base de datos tiene dos objetos en el schema `public`:

| Objeto | Tipo | Descripción |
|---|---|---|
| `temperatura_aire` | Tabla | Datos originales sin modificar (350,000 registros) |
| `temperatura_aire_limpia` | Vista | Datos filtrados sin errores de sensor (332,063 registros) |

---

## Notas sobre los datos

- Los datos provienen de estaciones automáticas del IDEAM con control de calidad básico.
- Se identificaron 17,937 registros con `valorobservado = 0` o fuera del rango esperado para el Caribe, que corresponden a errores de sensor. Estos registros **no fueron eliminados** de la tabla original.
- Para el análisis se usa la vista `temperatura_aire_limpia` que excluye dichos errores.
- El período con mayor densidad de registros es 2013–2018.
- Córdoba presenta la mayor cantidad de valores atípicos (≈15,000). Esto se debe a que varias estaciones del departamento registraron valores de 0°C durante períodos prolongados entre 2010 y 2015, lo que indica fallas técnicas en los sensores de medición. Estos registros están presentes en la tabla original pero son excluidos por la vista `temperatura_aire_limpia`.
