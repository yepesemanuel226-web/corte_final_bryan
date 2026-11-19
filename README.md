# 🌡️ Temperatura Ambiente del Aire — Región Caribe Colombiana

> Análisis Exploratorio de Datos sobre registros de temperatura del aire en los 7 departamentos de la región Caribe colombiana, usando datos abiertos del IDEAM a través del portal datos.gov.co.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?style=flat&logo=postgresql&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=flat&logo=powerbi&logoColor=black)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=flat&logo=plotly&logoColor=white)

---

## 📋 Información general

| Campo | Detalle |
|---|---|
| **Asignatura** | Minería de Datos |
| **Fuente de datos** | [IDEAM – datos.gov.co](https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Temperatura-Ambiente-del-Aire/sbwg-7ju4/about_data) |
| **Período analizado** | 2005 – 2019 |
| **Registros originales** | 350,000 (50,000 por departamento) |
| **Registros depurados** | 332,063 (tras filtrar errores de sensor) |
| **Departamentos** | 7 — Atlántico, Bolívar, Cesar, Córdoba, La Guajira, Magdalena, Sucre |

---

## 🗂️ Tabla de contenidos

1. [Estructura del proyecto](#️-estructura-del-proyecto)
2. [Instalación](#-instalación)
3. [Configuración](#️-configuración)
4. [Uso paso a paso](#-uso-paso-a-paso)
5. [Base de datos en Neon](#️-base-de-datos-en-neon)
6. [Aplicación Streamlit](#-aplicación-streamlit)
7. [Power BI](#-power-bi)
8. [Hallazgos del análisis](#-hallazgos-del-análisis)
9. [Notas sobre los datos](#-notas-sobre-los-datos)

---

## 🗃️ Estructura del proyecto

```
corte_final/
│
├── 📄 app.py                   # Aplicación Streamlit — EDA completo
├── 📄 cargar_datos.py          # Descarga y carga de datos a PostgreSQL Neon
├── 📄 exportar_csv.py          # Exportación de datos a CSV
├── 📄 check.py                 # Verificación de conexión a la BD
├── 📄 requirements.txt         # Dependencias del proyecto
├── 📄 temperatura_caribe.csv   # Dataset exportado
├── 📄 .env                     # Variables de entorno (no compartir)
│
├── 📁 utils/
│   └── conexion.py             # Carga de datos desde Neon y filtros del sidebar
│
└── 📁 screenshots/             # Capturas de pantalla de la app y Power BI
```

---

## 📦 Instalación

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
| `streamlit` | Aplicación web interactiva |
| `plotly` | Visualizaciones interactivas |
| `statsmodels` | Línea de tendencia OLS en dispersión |
| `numpy` | Cálculos numéricos |

---

## ⚙️ Configuración

Crea un archivo `.env` en la raíz del proyecto:

```
DATABASE_URL=postgresql://usuario:contraseña@host/neondb?sslmode=require&channel_binding=require
```

> ⚠️ Nunca compartas este archivo públicamente. Está incluido en `.gitignore`.

---

## 🚀 Uso paso a paso

### Paso 1 — Cargar los datos

```powershell
python cargar_datos.py
```

Descarga los datos del IDEAM (7 departamentos × 50,000 registros) y los carga en la tabla `temperatura_aire`. Tarda aproximadamente 10–15 minutos.

### Paso 2 — Crear la vista de depuración

Ejecuta este SQL en el editor de Neon:

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

Filtra 17,937 registros con errores de sensor (5.1%), manteniendo la tabla original intacta.

### Paso 3 — Verificar la carga *(opcional)*

```powershell
python check.py
```

### Paso 4 — Ejecutar la aplicación

```powershell
streamlit run app.py
```

La app se abre en `http://localhost:8501`.

---

## 🗄️ Base de datos en Neon

| Objeto | Tipo | Registros | Descripción |
|---|---|---|---|
| `temperatura_aire` | Tabla | 350,000 | Datos originales sin modificar |
| `temperatura_aire_limpia` | Vista | 332,063 | Datos depurados sin errores de sensor |

> Los registros originales se conservan intactos. La depuración se aplica mediante una vista SQL, cumpliendo el principio de trazabilidad del dato.

---

## 📊 Aplicación Streamlit

La app tiene **13 secciones**. Cada una muestra su captura, descripción y el código que la construye.

---

### 1️⃣ Resumen General

![Resumen General](screenshots/01_resumen_general.png)

KPIs principales: total de registros, temperatura media, máxima, mínima, departamentos, estaciones, municipios y rango temporal. Los filtros del sidebar controlan todo el análisis.

```python
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total registros",    f"{len(df_f):,}")
col2.metric("Temperatura media",  f"{df_f['valorobservado'].mean():.2f} °C")
col3.metric("Temperatura máxima", f"{df_f['valorobservado'].max():.2f} °C")
col4.metric("Temperatura mínima", f"{df_f['valorobservado'].min():.2f} °C")
```

---

### 2️⃣ Datos y Transformaciones

![Datos y Transformaciones](screenshots/02_transformaciones.png)

![Vista datos originales vs depurados](screenshots/02_transformaciones_tabla.png)

Información del conjunto de datos, tabla de transformaciones con técnica/aplicación/justificación, comparativa original vs depurado y botones de descarga CSV.

```python
transformaciones = pd.DataFrame([
    {"Técnica": "Conservación de datos originales", ...},
    {"Técnica": "Depuración mediante vista SQL", ...},
    {"Técnica": "Conversión de tipos", ...},
    {"Técnica": "Extracción de variables temporales", ...},
    {"Técnica": "Filtro geográfico interactivo", ...},
])
st.dataframe(transformaciones, use_container_width=True, hide_index=True)
```

---

### 3️⃣ Calidad de Datos

![Calidad de Datos](screenshots/03_calidad_datos.png)

Conteo de valores nulos por columna y estadísticas descriptivas (count, mean, std, percentiles) agrupadas por departamento.

```python
nulos = df_f.isnull().sum().reset_index()
nulos["% del total"] = (nulos["Valores nulos"] / len(df_f) * 100).round(2)
desc = df_f.groupby("departamento")["valorobservado"].describe().round(2)
```

---

### 4️⃣ Distribución de Temperaturas

![Distribución de Temperaturas](screenshots/04_distribucion_temperaturas.png)

Histograma superpuesto (60 bins) y diagrama de caja por departamento. Compara la forma de la distribución y dispersión entre los 7 departamentos.

```python
fig_hist = px.histogram(df_f, x="valorobservado", color="departamento",
                        nbins=60, barmode="overlay", opacity=0.7)
fig_box  = px.box(df_f, x="departamento", y="valorobservado", color="departamento")
```

---

### 5️⃣ Valores Atípicos

![Valores Atípicos](screenshots/05_valores_atipicos.png)

Detección de outliers con el método IQR (Q1 − 1.5×IQR / Q3 + 1.5×IQR). Métricas a la izquierda, gráfico de barras por departamento a la derecha.

```python
Q1, Q3  = df_f["valorobservado"].quantile([0.25, 0.75])
IQR     = Q3 - Q1
atipicos = df_f[(df_f["valorobservado"] < Q1 - 1.5*IQR) |
                (df_f["valorobservado"] > Q3 + 1.5*IQR)]
```

---

### 6️⃣ Tendencia Temporal

![Tendencia Temporal](screenshots/06_tendencia_temporal.png)

Evolución mensual de temperatura media (2005–2019) y patrón promedio por hora del día que revela el ciclo térmico diario.

```python
temp_mensual = df_f.groupby(["anio","mes","departamento"])["valorobservado"].mean()
temp_hora    = df_f.groupby(["hora","departamento"])["valorobservado"].mean()
```

---

### 7️⃣ Mapa de Calor de Correlaciones

![Mapa de Calor de Correlaciones](screenshots/07_mapa_calor_correlaciones.png)

Correlación de Pearson entre: temperatura, latitud, longitud, año, mes y hora. Escala RdBu centrada en 0.

```python
cols_num = ["valorobservado","latitud","longitud","anio","mes","hora"]
corr = df_f[cols_num].corr().round(2)
fig_corr = go.Figure(data=go.Heatmap(z=corr.values, colorscale="RdBu", zmid=0))
```

---

### 8️⃣ Mapa de Estaciones

![Mapa de Estaciones](screenshots/08_mapa_estaciones.png)

Mapa interactivo con las estaciones meteorológicas. Cada punto está coloreado y dimensionado por temperatura media. Hover muestra nombre, departamento, municipio y temperatura.

```python
fig_mapa = px.scatter_map(estaciones, lat="latitud", lon="longitud",
                          color="temp_media", size="temp_media",
                          color_continuous_scale="YlOrRd",
                          map_style="carto-positron")
```

---

### 9️⃣ Gráficos de Dispersión

![Gráficos de Dispersión](screenshots/09_graficos_dispersion.png)

Scatter plots sobre 5,000 registros: temperatura vs hora del día y temperatura vs latitud con tendencia OLS por departamento (`statsmodels`).

```python
muestra  = df_f.sample(min(5000, len(df_f)), random_state=42)
fig_sc2  = px.scatter(muestra, x="latitud", y="valorobservado",
                      color="departamento", trendline="ols")
```

---

### 🔟 Análisis Departamental

![Análisis Departamental](screenshots/10_analisis_departamental.png)

Temperatura media por departamento en barras, participación de registros en dona y tabla de resumen estadístico completo.

```python
temp_depto = df_f.groupby("departamento")["valorobservado"].mean().reset_index()
fig_depto  = px.bar(temp_depto, x="departamento", y="temp_media", text="temp_media")
fig_pie    = px.pie(reg_depto, names="departamento", values="Registros", hole=0.4)
```

---

### 1️⃣1️⃣ Análisis Municipal

![Análisis Municipal](screenshots/11_analisis_municipal.png)

Ranking interactivo de municipios con slider (5–30), gráficos horizontales de temperatura media y registros, y tabla completa de municipios.

```python
top_n = st.slider("Cantidad de municipios a visualizar", min_value=5, max_value=30, value=15)
muni_resumen = df_f.groupby(["departamento","municipio"])["valorobservado"].agg(
    Registros="count", temp_media="mean", temp_max="max", temp_min="min"
).reset_index()
```

---

### 1️⃣2️⃣ Muestra de Datos

![Muestra de Datos](screenshots/12_muestra_datos.png)

Tabla interactiva con los primeros 500 registros filtrados y todas las columnas.

```python
st.dataframe(df_f.head(500), use_container_width=True)
```

---

### 1️⃣3️⃣ Conclusiones

![Conclusiones](screenshots/13_conclusiones.png)

![Conclusiones metodológicas](screenshots/13_conclusiones_2.png)

Resumen dinámico calculado sobre los datos filtrados y conclusiones metodológicas del proceso.

```python
depto_mas_calido = df_f.groupby("departamento")["valorobservado"].mean().idxmax()
muni_mas_calido  = df_f.groupby("municipio")["valorobservado"].mean().idxmax()
hora_pico        = df_f.groupby("hora")["valorobservado"].mean().idxmax()
```

---

## 📈 Power BI

Dashboard interactivo conectado directamente a la vista `temperatura_aire_limpia` en Neon.

### Dashboard principal

![Power BI Dashboard](screenshots/10_powerbi_dashboard.png)

KPIs de temperatura, temperatura media por departamento, evolución anual 2005–2019, patrón horario y temperatura media por mes.

### Modelo de datos

![Power BI Modelo de Datos](screenshots/12_powerbi_modelo.png)

Tabla `temperatura_aire_limpia` con todos sus campos y la medida calculada `Total Registros`.

### Datos cargados

![Power BI Tabla de Datos](screenshots/11_powerbi_tabla_datos.png)

Registros conectados en tiempo real desde Neon con todos los campos visibles.

---

## 🔎 Hallazgos del análisis

> Resultados del análisis exploratorio sobre los 332,063 registros depurados (2005–2019). Referencia para el documento de investigación.

### Estadísticas generales

| Indicador | Valor |
|---|---|
| 🌡️ Temperatura media regional | **26.63 °C** |
| 🔺 Temperatura máxima | **50.00 °C** |
| 🔻 Temperatura mínima | **1.10 °C** |
| 📅 Período analizado | 2005 – 2019 |
| 🗺️ Departamentos | 7 |
| 📡 Estaciones meteorológicas | 59 |
| 🏘️ Municipios con registros | 43 |

### Comportamiento por departamento

| Departamento | Media (°C) | Mín (°C) | Máx (°C) | Registros |
|---|---|---|---|---|
| ATLÁNTICO | 27.86 | 1.2 | 46.0 | 49,207 |
| BOLÍVAR | 27.94 | 16.3 | 48.6 | 49,775 |
| CESAR | 24.00 | 1.8 | 49.2 | 49,553 |
| CÓRDOBA | 27.87 | 1.3 | 50.0 | 34,781 |
| LA GUAJIRA | 27.76 | 1.1 | 50.0 | 49,568 |
| MAGDALENA | 25.50 | 1.2 | 41.4 | 49,535 |
| SUCRE | 25.82 | 1.2 | 49.8 | 48,221 |

> Bolívar y Atlántico tienen las temperaturas medias más altas. Cesar y Magdalena las más bajas, asociadas a estaciones en zonas de mayor altitud.

### Patrón horario diario

| Momento | Hora | Temperatura aprox. |
|---|---|---|
| 🌙 Mínimo diario | 05:00 – 06:00 h | 21 – 24 °C |
| ☀️ Máximo diario | 13:00 – 15:00 h | 30 – 34 °C |
| 📊 Amplitud térmica | — | ~8 – 10 °C |

### Valores atípicos

| Indicador | Valor |
|---|---|
| Total atípicos (IQR) | **16,175** (4.89%) |
| Límite inferior | 16.70 °C |
| Límite superior | 37.50 °C |
| Mayor concentración | Córdoba (~7,000) y Sucre (~4,800) |

### Correlaciones

| Variables | Correlación | Interpretación |
|---|---|---|
| Temperatura – Hora | **0.17** | Positiva débil — confirma ciclo diario |
| Temperatura – Latitud | 0.01 | Sin correlación significativa |
| Temperatura – Longitud | -0.06 | Sin correlación significativa |
| Temperatura – Año | -0.07 | Sin tendencia temporal marcada |
| Temperatura – Mes | -0.02 | Sin estacionalidad marcada |
| Latitud – Longitud | **0.72** | Correlación geográfica esperada |

---

## 📝 Notas sobre los datos

- Los datos provienen de estaciones automáticas del IDEAM con control de calidad básico.
- Se identificaron **17,937 registros** con errores de sensor (5.1%): valores ≤ 1 °C, > 50 °C o sin coordenadas. No fueron eliminados — la vista los excluye.
- El período con mayor densidad de registros es **2013–2018**.
- Córdoba presenta la mayor cantidad de valores atípicos (~15,000), por fallas en sensores entre 2010 y 2015.
