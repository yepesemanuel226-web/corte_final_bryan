import os
import time
import requests
import psycopg
import csv
import io
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL  = os.environ["DATABASE_URL"]
SOCRATA_BASE  = "https://www.datos.gov.co/resource/sbwg-7ju4.csv"
LIMIT         = 5_000
MAX_POR_DEPTO = 50_000

DEPTOS_CARIBE = [
    "ATLANTICO",
    "BOLIVAR",
    "CESAR",
    "CORDOBA",
    "LA GUAJIRA",
    "MAGDALENA",
    "SUCRE",
]

# Reglas de limpieza aplicadas en Python antes de insertar
TEMP_MIN = 1      # °C — valores <= 1 son errores de sensor
TEMP_MAX = 50     # °C — valores > 50 son imposibles para el Caribe

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS temperatura_aire_limpia (
    id                  SERIAL PRIMARY KEY,
    codigoestacion      TEXT,
    codigosensor        TEXT,
    fechaobservacion    TIMESTAMP,
    valorobservado      NUMERIC(10, 5),
    nombreestacion      TEXT,
    departamento        TEXT,
    municipio           TEXT,
    zonahidrografica    TEXT,
    latitud             NUMERIC(12, 9),
    longitud            NUMERIC(12, 9),
    descripcionsensor   TEXT,
    unidadmedida        TEXT
);
"""

CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_limpia_fecha        ON temperatura_aire_limpia (fechaobservacion);",
    "CREATE INDEX IF NOT EXISTS idx_limpia_departamento ON temperatura_aire_limpia (departamento);",
    "CREATE INDEX IF NOT EXISTS idx_limpia_estacion     ON temperatura_aire_limpia (codigoestacion);",
]

INSERT_SQL = """
INSERT INTO temperatura_aire_limpia
    (codigoestacion, codigosensor, fechaobservacion, valorobservado,
     nombreestacion, departamento, municipio, zonahidrografica,
     latitud, longitud, descripcionsensor, unidadmedida)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
ON CONFLICT DO NOTHING;
"""


def descargar_bloque(departamento, offset, limit, reintentos=4):
    params = {
        "$limit":  limit,
        "$offset": offset,
        "$where":  f"departamento='{departamento}'",
    }
    for intento in range(1, reintentos + 1):
        try:
            resp = requests.get(SOCRATA_BASE, params=params, timeout=120)
            resp.raise_for_status()
            return list(csv.DictReader(io.StringIO(resp.text)))
        except Exception as e:
            print(f"    Intento {intento}/{reintentos} falló: {e}")
            if intento == reintentos:
                raise
            time.sleep(10 * intento)


def parsear_fila(row):
    """Convierte tipos y retorna la tupla, o None si el registro no pasa la limpieza."""
    def safe_float(v):
        try:
            return float(v) if v not in ("", None) else None
        except ValueError:
            return None

    def safe_ts(v):
        return v.replace(".000", "") if v else None

    temp = safe_float(row.get("valorobservado"))
    lat  = safe_float(row.get("latitud"))
    lon  = safe_float(row.get("longitud"))

    # --- Limpieza en Python ---
    # 1. Descartar si la temperatura es nula, <= TEMP_MIN o > TEMP_MAX
    if temp is None or temp <= TEMP_MIN or temp > TEMP_MAX:
        return None
    # 2. Descartar si no tiene coordenadas
    if lat is None or lon is None:
        return None
    # --------------------------

    return (
        row.get("codigoestacion"),
        row.get("codigosensor"),
        safe_ts(row.get("fechaobservacion")),
        temp,
        row.get("nombreestacion"),
        row.get("departamento"),
        row.get("municipio"),
        row.get("zonahidrografica"),
        lat,
        lon,
        row.get("descripcionsensor"),
        row.get("unidadmedida"),
    )


def cargar_departamento(conn, departamento):
    offset        = 0
    total_vistos  = 0   # filas descargadas de la API
    total_limpios = 0   # filas que pasaron la limpieza e ingresaron a la BD
    descartados   = 0   # filas eliminadas por la limpieza

    while True:
        restante = MAX_POR_DEPTO - total_vistos
        if restante <= 0:
            break

        bloque = min(LIMIT, restante)
        print(f"    Descargando desde fila {offset}...")
        filas = descargar_bloque(departamento, offset, bloque)

        if not filas:
            break

        filas_limpias = []
        for f in filas:
            parsed = parsear_fila(f)
            if parsed is not None:
                filas_limpias.append(parsed)
            else:
                descartados += 1

        if filas_limpias:
            with conn.cursor() as cur:
                cur.executemany(INSERT_SQL, filas_limpias)
            conn.commit()

        total_vistos  += len(filas)
        total_limpios += len(filas_limpias)

        if len(filas) < bloque:
            break

        offset += bloque

    print(f"    Descartados por limpieza: {descartados:,}")
    return total_vistos, total_limpios


def main():
    print("Conectando a Neon...")
    with psycopg.connect(DATABASE_URL) as conn:

        conn.execute(CREATE_TABLE_SQL)
        for idx in CREATE_INDEXES_SQL:
            conn.execute(idx)
        conn.commit()

        prev = conn.execute("SELECT COUNT(*) FROM temperatura_aire_limpia;").fetchone()[0]
        if prev > 0:
            print(f"  Había {prev:,} filas. Borrando para cargar de nuevo...")
            conn.execute("TRUNCATE TABLE temperatura_aire_limpia RESTART IDENTITY;")
            conn.commit()

        total_vistos  = 0
        total_limpios = 0

        for depto in DEPTOS_CARIBE:
            print(f"\n[{depto}] Descargando y limpiando...")
            vistos, limpios = cargar_departamento(conn, depto)
            total_vistos  += vistos
            total_limpios += limpios
            print(f"[{depto}] {vistos:,} descargados → {limpios:,} almacenados.")

        print(f"\n{'='*50}")
        print(f"Total descargados de la API : {total_vistos:,}")
        print(f"Total almacenados (limpios) : {total_limpios:,}")
        print(f"Descartados por limpieza    : {total_vistos - total_limpios:,} "
              f"({(total_vistos - total_limpios) / total_vistos * 100:.1f}%)")

        print("\nDesglose por departamento:")
        rows = conn.execute(
            "SELECT departamento, COUNT(*) FROM temperatura_aire_limpia "
            "GROUP BY departamento ORDER BY COUNT(*) DESC;"
        ).fetchall()
        for r in rows:
            print(f"  {r[0]:<20} {r[1]:>10,}")


if __name__ == "__main__":
    main()
