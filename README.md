# Temperatura Ambiente del Aire — Región Caribe Colombiana

Análisis exploratorio de datos de temperatura del aire en 7 departamentos del Caribe colombiano, con datos abiertos del IDEAM (2005–2019).

**Asignatura:** Minería de Datos | **Fuente:** [IDEAM – datos.gov.co](https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Temperatura-Ambiente-del-Aire/sbwg-7ju4/about_data)

---

## Estructura del proyecto

```
corte_final/
├── app.py                  # Aplicación Streamlit — EDA completo
├── cargar_datos.py         # Descarga y carga de datos a PostgreSQL Neon
├── schema.sql              # Script DDL de la base de datos
├── exportar_csv.py         # Exporta los datos a CSV
├── check.py                # Verifica registros cargados por año
├── requirements.txt        # Dependencias
├── temperatura_caribe.csv  # Dataset exportado
├── ultimo_corte.pbix       # Dashboard Power BI
├── utils/
│   └── conexion.py         # Conexión a Neon y filtros del sidebar
└── screenshots/            # Capturas de la app, Neon y Power BI
```

---

## Instalación

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Crear archivo `.env` en la raíz:

```
DATABASE_URL=postgresql://usuario:contraseña@host/neondb?sslmode=require&channel_binding=require
```

---

## Uso

**1. Cargar datos en PostgreSQL Neon**
```powershell
python cargar_datos.py
```
Descarga 350.000 registros del IDEAM (7 departamentos × 50.000). Tarda ~15 minutos.

**2. Crear la vista de depuración**

Ejecutar en el editor SQL de Neon:
```sql
CREATE VIEW temperatura_aire_limpia AS
SELECT id, codigoestacion, codigosensor, fechaobservacion,
       valorobservado, nombreestacion, departamento, municipio,
       zonahidrografica, latitud, longitud, descripcionsensor, unidadmedida
FROM temperatura_aire
WHERE valorobservado > 1
  AND valorobservado <= 50
  AND latitud IS NOT NULL
  AND longitud IS NOT NULL;
```
Filtra 17.937 registros con errores de sensor, dejando 332.063. La tabla original queda intacta.

**3. Verificar la carga** *(opcional)*
```powershell
python check.py
```
Muestra el conteo de registros por año para confirmar que la carga fue correcta.

**4. Ejecutar la aplicación**
```powershell
streamlit run app.py
```
Se abre en `http://localhost:8501`.

---

## Base de datos

| Objeto | Tipo | Registros |
|---|---|---|
| `temperatura_aire` | Tabla | 350.000 |
| `temperatura_aire_limpia` | Vista | 332.063 |

El script completo de la BD está en `schema.sql`.

---

## Hallazgos principales

| Indicador | Valor |
|---|---|
| Temperatura media regional | 26,63 °C |
| Período analizado | 2005 – 2019 |
| Departamentos | 7 |
| Estaciones | 59 |
| Municipios | 43 |

**Por departamento:**

| Departamento | Media (°C) |
|---|---|
| Bolívar | 27,94 |
| Córdoba | 27,87 |
| Atlántico | 27,86 |
| La Guajira | 27,76 |
| Sucre | 25,82 |
| Magdalena | 25,50 |
| Cesar | 24,00 |

- La variación entre departamentos (1,57 °C de desv. estándar) supera la variación mensual (0,27 °C).
- El ciclo diario es el factor de mayor variación: ~23,4 °C a las 5 h y ~30,8 °C a las 13 h.
- La Guajira es el único departamento con estacionalidad marcada (3,33 °C entre enero y agosto).
- Se identificaron 16.175 valores atípicos (4,89 %) por método IQR, concentrados en Cesar y Sucre.
