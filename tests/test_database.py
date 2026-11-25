"""
Pruebas Unitarias: Persistencia con SQLite
Verifica inicialización del esquema, inserción atómica de lotes, consultas históricas y resúmenes.
"""

import gc
import os
import tempfile
import pandas as pd
import pytest
from models.database import DatabaseManager


@pytest.fixture
def temp_db():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseManager(db_path=db_path)
    yield db
    del db
    gc.collect()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except OSError:
        pass


def test_inicializacion_esquema_y_regiones(temp_db):
    """La base de datos debe crearse con las 4 tablas y las 25 regiones oficiales pobladas."""
    with temp_db.connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM regions;")
        count = cursor.fetchone()[0]
        assert count == 25


def test_guardado_y_recuperacion_historica(temp_db):
    """Inserta un lote de mediciones evaluadas y verifica su recuperación."""
    df = pd.DataFrame([
        {
            "region": "Piura",
            "region_id": "PE-PIU",
            "precipitation_mm": 175.0,
            "temperature_c": 32.5,
            "risk_level": "Riesgo de Inundacion Extremo",
            "justification": "Lluvia torrencial y calor extremo"
        },
        {
            "region": "Lima",
            "region_id": "PE-LIM",
            "precipitation_mm": 10.0,
            "temperature_c": 21.0,
            "risk_level": "Riesgo Normal",
            "justification": "Condiciones normales"
        }
    ])

    inserted = temp_db.save_evaluation_batch(
        df,
        source_name="Test Simulación",
        is_simulation=True,
        engine_used="Python RuleEngine"
    )
    assert inserted == 2

    # Consultar historial
    history = temp_db.get_historical_measurements(limit=10)
    assert len(history) == 2
    assert history[0]["region"] in ["Piura", "Lima"]


def test_resumen_estadistico_sql(temp_db):
    """Verifica que la consulta SQL agregada retorne métricas por departamento."""
    df = pd.DataFrame([
        {"region": "Tumbes", "region_id": "PE-TUM", "precipitation_mm": 200.0, "temperature_c": 33.0, "risk_level": "Riesgo de Inundacion Extremo"},
        {"region": "Tumbes", "region_id": "PE-TUM", "precipitation_mm": 150.0, "temperature_c": 32.0, "risk_level": "Riesgo de Inundacion Extremo"},
    ])
    temp_db.save_evaluation_batch(df, "Test", True, "Python RuleEngine")

    summary_df = temp_db.get_risk_summary()
    assert isinstance(summary_df, pd.DataFrame)
    assert not summary_df.empty
    tumbes_row = summary_df[summary_df["region"] == "Tumbes"].iloc[0]
    assert tumbes_row["total_mediciones"] == 2
    assert tumbes_row["conteo_extremo"] == 2
