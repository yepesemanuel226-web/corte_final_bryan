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

**1. Resumen General** – KPIs principales y filtros laterales por departamento y año.

![Resumen General](screenshots/01_resumen_general.png)

**2. Calidad de Datos** – Tabla de valores nulos y estadísticas descriptivas por departamento.

![Calidad de Datos](screenshots/02_calidad_datos.png)

**3. Distribución de Temperaturas** – Histograma superpuesto y boxplot por departamento.

![Distribución de Temperaturas](screenshots/03_distribucion_temperaturas.png)

**4. Valores Atípicos** – Detección por método IQR con métricas y gráfico de barras.

![Valores Atípicos](screenshots/04_valores_atipicos.png)

**5. Tendencia Temporal** – Evolución mensual 2005–2019 y patrón diario por hora.

![Tendencia Temporal](screenshots/05_tendencia_temporal.png)

**6. Mapa de Calor de Correlaciones** – Correlación entre variables numéricas del dataset.

![Mapa de Calor de Correlaciones](screenshots/06_mapa_calor_correlaciones.png)

**7. Mapa de Estaciones** – Ubicación geográfica de las 59 estaciones con temperatura media.

![Mapa de Estaciones](screenshots/07_mapa_estaciones.png)

**8. Gráficos de Dispersión** – Temperatura vs hora del día y temperatura vs latitud con tendencia OLS.

![Gráficos de Dispersión](screenshots/08_graficos_dispersion.png)

**9. Muestra de Datos** – Tabla interactiva con los primeros 500 registros filtrados.

![Muestra de Datos](screenshots/09_muestra_datos.png)

---

### Power BI

**Dashboard principal** – KPIs, temperatura media por departamento, evolución anual y patrón horario.

![Power BI Dashboard](screenshots/10_powerbi_dashboard.png)

**Modelo de datos** – Vista de la tabla `public temperatura_aire_limpia` con todos sus campos y la medida `Total Registros`.

![Power BI Modelo de Datos](screenshots/12_powerbi_modelo.png)

**Datos cargados** – Vista de los registros en Power BI conectados directamente a la vista de Neon.

![Power BI Tabla de Datos](screenshots/11_powerbi_tabla_datos.png)

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
