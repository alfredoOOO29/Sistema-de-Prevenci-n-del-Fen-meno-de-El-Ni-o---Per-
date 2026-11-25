"""
Capa de Acceso a Datos y Persistencia con SQLite
Gestiona el almacenamiento histórico de mediciones, fuentes y evaluaciones de riesgo.
Utiliza consultas parametrizadas, transacciones atómicas y liberación explícita de recursos.
"""

from contextlib import contextmanager
import logging
import os
import sqlite3
from typing import Any, Dict, Generator, List, Optional
import pandas as pd

from models.data_providers import load_regions_catalog

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Gestor de persistencia en SQLite para el Sistema de Prevención de El Niño.
    Aísla las consultas SQL de controladores y vistas.
    """

    DEFAULT_DB_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "database", "el_nino.db")
    )

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self.DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_schema()
        self._seed_regions_if_empty()

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager que gestiona el ciclo de vida de la conexión SQLite.
        Garantiza commit automático ante éxito, rollback ante error y cierre explícito.
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_schema(self) -> None:
        """Crea el esquema relacional normalizado si no existe."""
        with self.connection() as conn:
            cursor = conn.cursor()
            
            # Tabla 1: Regiones Geográficas Oficiales
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS regions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    capital TEXT,
                    lat REAL NOT NULL,
                    lon REAL NOT NULL,
                    is_coastal_north INTEGER NOT NULL DEFAULT 0,
                    zone TEXT
                );
            """)

            # Tabla 2: Fuentes de Datos (Simuladas vs Reales)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    is_simulation INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Tabla 3: Mediciones Hidrometeorológicas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id INTEGER NOT NULL,
                    region_id TEXT NOT NULL,
                    precipitation_mm REAL NOT NULL,
                    temperature_c REAL NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_id) REFERENCES data_sources(id) ON DELETE CASCADE,
                    FOREIGN KEY (region_id) REFERENCES regions(id) ON DELETE CASCADE
                );
            """)

            # Tabla 4: Evaluaciones de Riesgo Inferidas (Python o Prolog)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id INTEGER NOT NULL,
                    engine_used TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    justification TEXT,
                    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (measurement_id) REFERENCES measurements(id) ON DELETE CASCADE
                );
            """)

    def _seed_regions_if_empty(self) -> None:
        """Puebla la tabla de regiones a partir del catálogo JSON si la base está vacía."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM regions;")
            count = cursor.fetchone()[0]
            if count == 0:
                catalog = load_regions_catalog()
                for reg in catalog:
                    cursor.execute("""
                        INSERT OR IGNORE INTO regions (id, name, capital, lat, lon, is_coastal_north, zone)
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                    """, (
                        reg.get("id"),
                        reg.get("name"),
                        reg.get("capital"),
                        reg.get("lat"),
                        reg.get("lon"),
                        1 if reg.get("is_coastal_north") else 0,
                        reg.get("zone")
                    ))

    def save_evaluation_batch(
        self,
        df: pd.DataFrame,
        source_name: str,
        is_simulation: bool,
        engine_used: str
    ) -> int:
        """
        Inserta atómicamente un lote completo de mediciones y sus clasificaciones de riesgo.
        """
        if df.empty:
            return 0

        with self.connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO data_sources (name, is_simulation)
                VALUES (?, ?);
            """, (source_name, 1 if is_simulation else 0))
            source_id = cursor.lastrowid

            inserted_count = 0
            records = df.to_dict("records")
            for rec in records:
                reg_name = rec.get("region", "Desconocido")
                reg_id = rec.get("region_id")
                if not reg_id:
                    cursor.execute("SELECT id FROM regions WHERE name = ? LIMIT 1;", (reg_name,))
                    row = cursor.fetchone()
                    reg_id = row[0] if row else "PE-UNK"

                p = float(rec.get("precipitation_mm", 0.0))
                t = float(rec.get("temperature_c", 0.0))
                risk = str(rec.get("risk_level", "Riesgo Normal"))
                justification = str(rec.get("justification", "Evaluación de motor lógico"))

                cursor.execute("""
                    INSERT INTO measurements (source_id, region_id, precipitation_mm, temperature_c)
                    VALUES (?, ?, ?, ?);
                """, (source_id, reg_id, p, t))
                measurement_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO risk_evaluations (measurement_id, engine_used, risk_level, justification)
                    VALUES (?, ?, ?, ?);
                """, (measurement_id, engine_used, risk, justification))
                inserted_count += 1

            return inserted_count

    def get_historical_measurements(
        self,
        limit: int = 50,
        region_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Recupera el historial de mediciones y riesgos evaluados."""
        query = """
            SELECT 
                m.id AS measurement_id,
                r.name AS region,
                r.lat,
                r.lon,
                m.precipitation_mm,
                m.temperature_c,
                m.recorded_at,
                ds.name AS source_name,
                ds.is_simulation,
                re.engine_used,
                re.risk_level,
                re.justification
            FROM measurements m
            JOIN regions r ON m.region_id = r.id
            JOIN data_sources ds ON m.source_id = ds.id
            LEFT JOIN risk_evaluations re ON re.measurement_id = m.id
        """
        params: List[Any] = []
        if region_name:
            query += " WHERE r.name LIKE ? "
            params.append(f"%{region_name}%")

        query += " ORDER BY m.recorded_at DESC, m.id DESC LIMIT ?;"
        params.append(limit)

        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_risk_summary(self) -> pd.DataFrame:
        """Genera un resumen estadístico agregado de riesgos evaluados por departamento."""
        query = """
            SELECT 
                r.name AS region,
                COUNT(m.id) AS total_mediciones,
                ROUND(AVG(m.precipitation_mm), 2) AS promedio_lluvia_mm,
                ROUND(MAX(m.precipitation_mm), 2) AS max_lluvia_mm,
                ROUND(AVG(m.temperature_c), 2) AS promedio_temp_c,
                SUM(CASE WHEN re.risk_level LIKE '%Extremo%' THEN 1 ELSE 0 END) AS conteo_extremo,
                SUM(CASE WHEN re.risk_level LIKE '%Alto%' THEN 1 ELSE 0 END) AS conteo_alto,
                SUM(CASE WHEN re.risk_level LIKE '%Moderado%' THEN 1 ELSE 0 END) AS conteo_moderado
            FROM regions r
            LEFT JOIN measurements m ON r.id = m.region_id
            LEFT JOIN risk_evaluations re ON re.measurement_id = m.id
            GROUP BY r.id, r.name
            ORDER BY conteo_extremo DESC, promedio_lluvia_mm DESC;
        """
        with self.connection() as conn:
            return pd.read_sql_query(query, conn)
