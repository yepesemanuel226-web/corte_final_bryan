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

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS temperatura_aire (
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
    "CREATE INDEX IF NOT EXISTS idx_temp_fecha        ON temperatura_aire (fechaobservacion);",
    "CREATE INDEX IF NOT EXISTS idx_temp_departamento ON temperatura_aire (departamento);",
    "CREATE INDEX IF NOT EXISTS idx_temp_estacion     ON temperatura_aire (codigoestacion);",
]

INSERT_SQL = """
INSERT INTO temperatura_aire
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
    def safe_float(v):
        try:
            return float(v) if v not in ("", None) else None
        except ValueError:
            return None

    def safe_ts(v):
        return v.replace(".000", "") if v else None

    return (
        row.get("codigoestacion"),
        row.get("codigosensor"),
        safe_ts(row.get("fechaobservacion")),
        safe_float(row.get("valorobservado")),
        row.get("nombreestacion"),
        row.get("departamento"),
        row.get("municipio"),
        row.get("zonahidrografica"),
        safe_float(row.get("latitud")),
        safe_float(row.get("longitud")),
        row.get("descripcionsensor"),
        row.get("unidadmedida"),
    )


def cargar_departamento(conn, departamento):
    offset = 0
    total  = 0

    while True:
        restante = MAX_POR_DEPTO - total
        if restante <= 0:
            break

        bloque = min(LIMIT, restante)
        print(f"    Descargando desde fila {offset}...")
        filas = descargar_bloque(departamento, offset, bloque)

        if not filas:
            break

        with conn.cursor() as cur:
            cur.executemany(INSERT_SQL, [parsear_fila(f) for f in filas])
        conn.commit()

        total += len(filas)

        if len(filas) < bloque:
            break

        offset += bloque

    return total


def main():
    print("Conectando a Neon...")
    with psycopg.connect(DATABASE_URL) as conn:

        conn.execute(CREATE_TABLE_SQL)
        for idx in CREATE_INDEXES_SQL:
            conn.execute(idx)
        conn.commit()

        prev = conn.execute("SELECT COUNT(*) FROM temperatura_aire;").fetchone()[0]
        if prev > 0:
            print(f"  Había {prev:,} filas. Borrando para cargar de nuevo...")
            conn.execute("TRUNCATE TABLE temperatura_aire RESTART IDENTITY;")
            conn.commit()

        for depto in DEPTOS_CARIBE:
            print(f"\n[{depto}] Descargando...")
            n = cargar_departamento(conn, depto)
            print(f"[{depto}] {n:,} filas cargadas.")

        count = conn.execute("SELECT COUNT(*) FROM temperatura_aire;").fetchone()[0]
        print(f"\nTotal: {count:,} registros cargados.")

        print("\nDesglose por departamento:")
        rows = conn.execute(
            "SELECT departamento, COUNT(*) FROM temperatura_aire GROUP BY departamento ORDER BY COUNT(*) DESC;"
        ).fetchall()
        for r in rows:
            print(f"  {r[0]:<20} {r[1]:>10,}")


if __name__ == "__main__":
    main()
