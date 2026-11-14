import os, psycopg
from dotenv import load_dotenv
load_dotenv()

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    rows = conn.execute(
        "SELECT DATE_PART('year', fechaobservacion) as anio, COUNT(*) FROM temperatura_aire GROUP BY anio ORDER BY anio;"
    ).fetchall()
    print("Años en la base de datos:")
    for r in rows:
        print(f"  {int(r[0])}: {r[1]:,} registros")
