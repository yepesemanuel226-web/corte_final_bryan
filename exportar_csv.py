import os
import pandas as pd
import psycopg
from dotenv import load_dotenv

load_dotenv()

print("Conectando a Neon...")
with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                codigoestacion,
                fechaobservacion,
                valorobservado,
                nombreestacion,
                departamento,
                municipio,
                zonahidrografica,
                latitud,
                longitud
            FROM temperatura_aire
            ORDER BY fechaobservacion;
        """)
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()

df = pd.DataFrame(rows, columns=cols)
df["fechaobservacion"] = pd.to_datetime(df["fechaobservacion"])
df["valorobservado"] = pd.to_numeric(df["valorobservado"], errors="coerce")

# Filtramos valores imposibles para el Caribe (ceros de sensor y valores > 50°C)
df = df[(df["valorobservado"] > 1) & (df["valorobservado"] <= 50)]
df["anio"] = df["fechaobservacion"].dt.year
df["mes"]  = df["fechaobservacion"].dt.month
df["hora"] = df["fechaobservacion"].dt.hour

ruta = "temperatura_caribe.csv"
df.to_csv(ruta, index=False, encoding="utf-8-sig")
print(f"Exportado: {ruta} ({len(df):,} filas)")
