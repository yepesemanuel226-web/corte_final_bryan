-- ============================================================
-- Script de base de datos
-- Proyecto: Temperatura Ambiente del Aire - Region Caribe
-- Base de datos: PostgreSQL (Neon)
-- ============================================================

-- Tabla principal con datos originales sin modificar
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

-- Indices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_temp_fecha
    ON temperatura_aire (fechaobservacion);

CREATE INDEX IF NOT EXISTS idx_temp_departamento
    ON temperatura_aire (departamento);

CREATE INDEX IF NOT EXISTS idx_temp_estacion
    ON temperatura_aire (codigoestacion);

-- Vista de datos depurados (sin eliminar registros originales)
-- Excluye: valores <= 1 C, valores > 50 C y registros sin coordenadas
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
