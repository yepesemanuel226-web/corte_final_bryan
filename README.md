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
├── app.py                          # Aplicación Streamlit (EDA completo en una sola página)
├── utils/                          # Módulos compartidos
│   └── conexion.py                 # Carga de datos desde Neon y filtros del sidebar
├── screenshots/                    # Capturas de pantalla de la app y Power BI
├── capturas_originales/            # Capturas originales sin renombrar
├── cargar_datos.py                 # Script de carga de datos a PostgreSQL Neon
├── exportar_csv.py                 # Script para exportar los datos a CSV
├── check.py                        # Script de verificación de conexión a la BD
├── requirements.txt                # Dependencias del proyecto
├── temperatura_caribe.csv          # Datos exportados
└── .env                            # Variables de entorno (no compartir públicamente)
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

La app tiene 13 secciones. A continuación se muestra cada una con su captura, una descripción y el código que la construye.

---

### 1. Resumen General

![Resumen General](screenshots/01_resumen_general.png)

KPIs principales del dataset filtrado: total de registros, temperatura media, máxima y mínima, número de departamentos, estaciones, municipios y rango temporal. Los filtros del sidebar por departamento, municipio y año controlan todo el análisis.

```python
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total registros",    f"{len(df_f):,}")
col2.metric("Temperatura media",  f"{df_f['valorobservado'].mean():.2f} °C")
col3.metric("Temperatura máxima", f"{df_f['valorobservado'].max():.2f} °C")
col4.metric("Temperatura mínima", f"{df_f['valorobservado'].min():.2f} °C")
```

---

### 2. Datos y Transformaciones

![Datos y Transformaciones](screenshots/02_transformaciones.png)

![Vista datos originales vs depurados](screenshots/02_transformaciones_tabla.png)

Información del conjunto de datos (registros originales vs depurados), tabla de transformaciones aplicadas con técnica, aplicación y justificación, vista comparativa de ambos datasets y botones de descarga en CSV.

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

### 3. Calidad de Datos

![Calidad de Datos](screenshots/03_calidad_datos.png)

Conteo de valores nulos por columna con su porcentaje sobre el total, y estadísticas descriptivas (count, mean, std, min, percentiles, max) agrupadas por departamento.

```python
nulos = df_f.isnull().sum().reset_index()
nulos.columns = ["Columna", "Valores nulos"]
nulos["% del total"] = (nulos["Valores nulos"] / len(df_f) * 100).round(2)
st.dataframe(nulos, use_container_width=True)

desc = df_f.groupby("departamento")["valorobservado"].describe().round(2)
st.dataframe(desc, use_container_width=True)
```

---

### 4. Distribución de Temperaturas

![Distribución de Temperaturas](screenshots/04_distribucion_temperaturas.png)

Histograma superpuesto con 60 bins por departamento y diagrama de caja. Compara la forma de la distribución y la dispersión entre los 7 departamentos.

```python
fig_hist = px.histogram(
    df_f, x="valorobservado", color="departamento",
    nbins=60, barmode="overlay", opacity=0.7,
    title="Distribución de temperatura por departamento",
)
fig_box = px.box(
    df_f, x="departamento", y="valorobservado", color="departamento",
    title="Boxplot de temperatura por departamento",
)
```

---

### 5. Valores Atípicos

![Valores Atípicos](screenshots/05_valores_atipicos.png)

Detección de outliers con el método IQR (Q1 − 1.5×IQR / Q3 + 1.5×IQR). Métricas a la izquierda y gráfico de barras con atípicos por departamento a la derecha.

```python
Q1  = df_f["valorobservado"].quantile(0.25)
Q3  = df_f["valorobservado"].quantile(0.75)
IQR = Q3 - Q1
lim_inf  = Q1 - 1.5 * IQR
lim_sup  = Q3 + 1.5 * IQR
atipicos = df_f[(df_f["valorobservado"] < lim_inf) | (df_f["valorobservado"] > lim_sup)]
```

---

### 6. Tendencia Temporal

![Tendencia Temporal](screenshots/06_tendencia_temporal.png)

Evolución de la temperatura media mensual por departamento (2005–2019) y patrón promedio por hora del día, que revela el ciclo térmico diario de cada departamento.

```python
temp_mensual = df_f.groupby(["anio", "mes", "departamento"])["valorobservado"].mean().reset_index()
temp_hora    = df_f.groupby(["hora", "departamento"])["valorobservado"].mean().reset_index()
```

---

### 7. Mapa de Calor de Correlaciones

![Mapa de Calor de Correlaciones](screenshots/07_mapa_calor_correlaciones.png)

Coeficientes de correlación de Pearson entre variables numéricas: temperatura, latitud, longitud, año, mes y hora. Escala RdBu centrada en 0.

```python
cols_num = ["valorobservado", "latitud", "longitud", "anio", "mes", "hora"]
corr = df_f[cols_num].corr().round(2)
fig_corr = go.Figure(data=go.Heatmap(z=corr.values, colorscale="RdBu", zmid=0))
```

---

### 8. Mapa de Estaciones

![Mapa de Estaciones](screenshots/08_mapa_estaciones.png)

Mapa interactivo con las estaciones meteorológicas. Cada punto está coloreado y dimensionado según la temperatura media. Al pasar el cursor muestra nombre, departamento, municipio y temperatura media.

```python
fig_mapa = px.scatter_map(
    estaciones, lat="latitud", lon="longitud",
    color="temp_media", size="temp_media",
    color_continuous_scale="YlOrRd",
    map_style="carto-positron",
    zoom=5, center={"lat": 9.5, "lon": -74.5},
)
```

---

### 9. Gráficos de Dispersión

![Gráficos de Dispersión](screenshots/09_graficos_dispersion.png)

Scatter plots sobre una muestra de 5,000 registros: temperatura vs hora del día y temperatura vs latitud con línea de tendencia OLS calculada con `statsmodels`.

```python
muestra = df_f.sample(min(5000, len(df_f)), random_state=42)
fig_sc2 = px.scatter(muestra, x="latitud", y="valorobservado",
                     color="departamento", trendline="ols")
```

---

### 10. Análisis Departamental

![Análisis Departamental](screenshots/10_analisis_departamental.png)

Temperatura media por departamento en gráfico de barras, participación de registros en gráfico de dona y tabla de resumen estadístico completo por departamento.

```python
temp_depto = df_f.groupby("departamento")["valorobservado"].mean().reset_index()
fig_depto  = px.bar(temp_depto, x="departamento", y="temp_media", text="temp_media")
fig_pie    = px.pie(reg_depto, names="departamento", values="Registros", hole=0.4)
```

---

### 11. Análisis Municipal

![Análisis Municipal](screenshots/11_analisis_municipal.png)

Ranking de municipios con slider interactivo (5–30 municipios), gráficos horizontales de temperatura media y cantidad de registros, y tabla completa de todos los municipios analizados.

```python
top_n = st.slider("Cantidad de municipios a visualizar", min_value=5, max_value=30, value=15)
muni_resumen = df_f.groupby(["departamento", "municipio"])["valorobservado"].agg(
    Registros="count", temp_media="mean", temp_max="max", temp_min="min"
).reset_index()
```

---

### 12. Muestra de Datos

![Muestra de Datos](screenshots/12_muestra_datos.png)

Tabla interactiva con los primeros 500 registros del dataset filtrado con todas las columnas.

```python
st.dataframe(df_f.head(500), use_container_width=True)
```

---

### 13. Conclusiones

![Conclusiones](screenshots/13_conclusiones.png)

![Conclusiones metodológicas](screenshots/13_conclusiones_2.png)

Resumen dinámico de hallazgos calculado sobre los datos filtrados actualmente (departamento más cálido, municipio con mayor temperatura, hora pico, atípicos) y conclusiones metodológicas del proceso de análisis.

```python
depto_mas_calido = df_f.groupby("departamento")["valorobservado"].mean().idxmax()
muni_mas_calido  = df_f.groupby("municipio")["valorobservado"].mean().idxmax()
hora_pico        = df_f.groupby("hora")["valorobservado"].mean().idxmax()
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

## Hallazgos del análisis

Esta sección resume los resultados obtenidos del análisis exploratorio sobre los 332,063 registros depurados de temperatura del aire en la Región Caribe colombiana (2005–2019). Puede usarse como referencia para el documento de investigación.

---

### Estadísticas generales

| Indicador | Valor |
|---|---|
| Temperatura media regional | 26.63 °C |
| Temperatura máxima registrada | 50.00 °C |
| Temperatura mínima registrada | 1.10 °C |
| Período analizado | 2005 – 2019 |
| Departamentos cubiertos | 7 |
| Estaciones meteorológicas | 59 |
| Municipios con registros | 43 |

---

### Comportamiento por departamento

| Departamento | Temp. media (°C) | Temp. mín (°C) | Temp. máx (°C) | Registros |
|---|---|---|---|---|
| ATLÁNTICO | 27.86 | 1.2 | 46.0 | 49,207 |
| BOLÍVAR | 27.94 | 16.3 | 48.6 | 49,775 |
| CESAR | 24.00 | 1.8 | 49.2 | 49,553 |
| CÓRDOBA | 27.87 | 1.3 | 50.0 | 34,781 |
| LA GUAJIRA | 27.76 | 1.1 | 50.0 | 49,568 |
| MAGDALENA | 25.50 | 1.2 | 41.4 | 49,535 |
| SUCRE | 25.82 | 1.2 | 49.8 | 48,221 |

> Bolívar y Atlántico presentan las temperaturas medias más altas de la región. Cesar y Magdalena registran las medias más bajas, asociadas a la presencia de estaciones en zonas de mayor altitud.

---

### Patrón horario diario

La temperatura sigue un ciclo térmico diario consistente en todos los departamentos:

- **Mínimo diario:** entre las 05:00 y 06:00 h (temperaturas cercanas a 21–24 °C según el departamento)
- **Máximo diario:** entre las 13:00 y 15:00 h (temperaturas cercanas a 30–34 °C)
- **Amplitud térmica diaria promedio:** aproximadamente 8–10 °C

Este patrón es característico del clima tropical de la región Caribe colombiana.

---

### Variación estacional

- El análisis mensual no muestra una estacionalidad marcada en temperatura media, lo que es consistente con el clima tropical de la región.
- Se observan caídas abruptas en la serie temporal (especialmente en Cesar y Córdoba entre 2010 y 2015) que corresponden a errores de sensor, conservados en la tabla original y excluidos por la vista de depuración.
- El período con mayor densidad de registros es **2013–2018**.

---

### Valores atípicos

- Se identificaron **16,175 valores atípicos** (4.89% del dataset depurado) mediante el método IQR.
- Límite inferior: **16.70 °C** · Límite superior: **37.50 °C**
- **Córdoba** concentra la mayor cantidad de atípicos (~7,000), seguido de Sucre (~4,800).
- Los atípicos en Córdoba se asocian a fallas técnicas en sensores de varias estaciones entre 2010 y 2015.

---

### Correlaciones entre variables

| Par de variables | Correlación |
|---|---|
| Temperatura – Hora del día | 0.17 (positiva débil) |
| Temperatura – Latitud | 0.01 (sin correlación significativa) |
| Temperatura – Longitud | -0.06 (sin correlación significativa) |
| Temperatura – Año | -0.07 (sin tendencia temporal marcada) |
| Temperatura – Mes | -0.02 (sin estacionalidad marcada) |
| Latitud – Longitud | 0.72 (correlación geográfica esperada) |

> La correlación más relevante para el análisis es la de temperatura con hora del día (0.17), que confirma el ciclo térmico diario. La ausencia de correlación con latitud sugiere que dentro de la región Caribe la variación espacial de temperatura es menor que la variación temporal diaria.

---

### Calidad de los datos

- El dataset original contiene **350,000 registros** sin valores nulos en las columnas principales.
- Se depuraron **17,937 registros** (5.1%) por errores de sensor: valores ≤ 1 °C, > 50 °C o sin coordenadas geográficas.
- Los datos originales se conservan intactos en la tabla `temperatura_aire`; la depuración se aplica exclusivamente a través de la vista `temperatura_aire_limpia`.

---



- Los datos provienen de estaciones automáticas del IDEAM con control de calidad básico.
- Se identificaron 17,937 registros con errores de sensor (5.1% del total): valores de temperatura ≤ 1 °C, > 50 °C, o sin coordenadas. Estos registros **no fueron eliminados** de la tabla original — la vista `temperatura_aire_limpia` los excluye al consultar.
- El período con mayor densidad de registros es 2013–2018.
- Córdoba presenta la mayor cantidad de valores atípicos (≈15,000), causados por fallas técnicas en sensores de varias estaciones entre 2010 y 2015. Están presentes en la tabla original pero son excluidos por la vista.
