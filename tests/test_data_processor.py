"""
Pruebas Unitarias: Programación Funcional y Procesador de Datos
Verifica funciones puras, inmutabilidad, orden superior, composición y pipelines pandas.
"""

import pandas as pd
import pytest
from models.data_processor import (
    ElNinoDataProcessor,
    calcular_promedio,
    clasificar_precipitacion,
    componer,
    curried_filtro_riesgo,
    normalizar_medicion,
    validar_medicion,
)
from models.risk_classifier import RiskLevel


def test_normalizar_medicion_puro_e_inmutable():
    """Verifica que la función no modifique el diccionario original (inmutabilidad)."""
    original = {"region": "  piura ", "precipitation_mm": "120.456", "temperature_c": 31.89}
    copia_verificacion = dict(original)
    
    resultado = normalizar_medicion(original)
    
    assert original == copia_verificacion, "El diccionario original no debe ser mutado"
    assert resultado["region"] == "Piura"
    assert resultado["precipitation_mm"] == 120.46
    assert resultado["temperature_c"] == 31.89


def test_validar_medicion_casos():
    """Valida registros correctos, nulos e inconsistentes."""
    assert validar_medicion({"precipitation_mm": 50.0, "temperature_c": 20.0})[0] is True
    assert validar_medicion({"precipitation_mm": None, "temperature_c": 20.0})[0] is False
    assert validar_medicion({"precipitation_mm": -10.0, "temperature_c": 20.0})[0] is False
    assert validar_medicion({"precipitation_mm": 50.0, "temperature_c": 100.0})[0] is False


def test_calcular_promedio_con_reduce():
    """Verifica el cálculo de promedio mediante reduce."""
    assert calcular_promedio([10.0, 20.0, 30.0, 40.0]) == 25.0
    assert calcular_promedio([]) == 0.0
    assert calcular_promedio([15.5]) == 15.5


def test_composicion_de_funciones():
    """Demuestra la propiedad asociativa de (f ∘ g)(x) = f(g(x))."""
    duplicar = lambda x: x * 2
    sumar_cinco = lambda x: x + 5
    restar_uno = lambda x: x - 1

    # componer(f, g, h)(x) evalúa h, luego g, luego f
    operacion = componer(duplicar, sumar_cinco, restar_uno)
    # x = 10 -> restar_uno(10)=9 -> sumar_cinco(9)=14 -> duplicar(14)=28
    assert operacion(10) == 28


def test_currying_filtro_riesgo():
    """Verifica la generación de predicados especializados mediante currying."""
    filtro_extremo = curried_filtro_riesgo(RiskLevel.EXTREMO.value)
    
    assert filtro_extremo({"risk_level": RiskLevel.EXTREMO.value}) is True
    assert filtro_extremo({"risk_level": RiskLevel.NORMAL.value}) is False


def test_pipeline_procesamiento_inmutable_dataframe():
    """Verifica que el procesamiento de DataFrames no mute la entrada y retorne nuevas instancias."""
    df_raw = pd.DataFrame([
        {"region": "Piura", "lat": -5.19, "lon": -80.63, "precipitation_mm": 180.0, "temperature_c": 32.0, "is_coastal_north": True},
        {"region": "Lima", "lat": -12.04, "lon": -77.04, "precipitation_mm": 15.0, "temperature_c": 22.0, "is_coastal_north": False},
        {"region": "Invalida", "lat": 0.0, "lon": 0.0, "precipitation_mm": -50.0, "temperature_c": 22.0, "is_coastal_north": False},
    ])
    
    processor = ElNinoDataProcessor()
    df_processed, df_at_risk = processor.process_data(df_raw)

    assert "risk_level" not in df_raw.columns, "El DataFrame original no debe modificarse"
    assert "risk_level" in df_processed.columns
    # El registro inválido de precipitación negativa fue filtrado en el pipeline
    assert len(df_processed) == 2
    assert len(df_at_risk) == 1
    assert df_at_risk.iloc[0]["region"] == "Piura"
    assert df_at_risk.iloc[0]["risk_level"] == RiskLevel.EXTREMO.value


def test_resumen_estadistico_pandas():
    """Verifica las métricas descriptivas agregadas."""
    df = pd.DataFrame([
        {"region": "A", "precipitation_mm": 100.0, "temperature_c": 25.0, "risk_level": "Alto"},
        {"region": "B", "precipitation_mm": 50.0, "temperature_c": 20.0, "risk_level": "Moderado"},
    ])
    stats = ElNinoDataProcessor.calcular_resumen_estadistico(df)
    assert stats["total_registros"] == 2
    assert stats["precipitacion"]["promedio_mm"] == 75.0
    assert stats["temperatura"]["promedio_c"] == 22.5
