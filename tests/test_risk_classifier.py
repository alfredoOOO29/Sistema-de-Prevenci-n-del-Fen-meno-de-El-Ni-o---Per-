"""
Pruebas Unitarias: Clasificador de Riesgo y Casos Límite
Verifica umbrales exactos (40mm, 80mm, 120mm, 30°C), resolución de la laguna lógica,
valores nulos, negativos y límites físicos.
"""

import pytest
from models.risk_classifier import RiskClassifier, RiskLevel, RiskThresholds


@pytest.fixture
def classifier():
    return RiskClassifier()


def test_clasificacion_limite_exacto_40mm(classifier):
    """Precipitación exactamente en 40.0 mm debe ser clasificada como Riesgo Normal."""
    level, _ = classifier.evaluate(precipitation=40.0, temperature=22.0)
    assert level == RiskLevel.NORMAL


def test_clasificacion_limite_exacto_80mm(classifier):
    """Precipitación exactamente en 80.0 mm debe ser clasificada como Riesgo Moderado."""
    level, _ = classifier.evaluate(precipitation=80.0, temperature=24.0)
    assert level == RiskLevel.MODERADO


def test_clasificacion_limite_exacto_120mm(classifier):
    """Precipitación exactamente en 120.0 mm debe ser clasificada como Riesgo Alto."""
    level, _ = classifier.evaluate(precipitation=120.0, temperature=25.0)
    assert level == RiskLevel.ALTO


def test_clasificacion_lluvia_extrema_con_temperatura_limite_30c(classifier):
    """
    CASO CRÍTICO (Corrección del defecto):
    Precipitación > 120mm con temperatura EXACTAMENTE en 30.0°C (no mayor a 30°C)
    debe clasificarse como Riesgo Alto (nunca Normal).
    """
    level, _ = classifier.evaluate(precipitation=135.0, temperature=30.0)
    assert level == RiskLevel.ALTO


def test_clasificacion_lluvia_extrema_con_baja_temperatura(classifier):
    """
    CASO CRÍTICO (Corrección del defecto):
    Precipitación > 120mm con temperatura de 18.0°C (selva o sierra fría lluviosa)
    debe clasificarse como Riesgo Alto (nunca Normal).
    """
    level, _ = classifier.evaluate(precipitation=150.0, temperature=18.0)
    assert level == RiskLevel.ALTO


def test_clasificacion_riesgo_extremo_el_nino(classifier):
    """Precipitación > 120mm Y temperatura > 30°C debe clasificarse como Riesgo Extremo."""
    level, _ = classifier.evaluate(precipitation=180.0, temperature=32.5)
    assert level == RiskLevel.EXTREMO


def test_clasificacion_lluvia_extremadamente_elevada(classifier):
    """Precipitación extremadamente alta dentro del límite físico (e.g. 500 mm)."""
    level, _ = classifier.evaluate(precipitation=500.0, temperature=31.0)
    assert level == RiskLevel.EXTREMO


def test_clasificacion_temperatura_negativa_valida(classifier):
    """Temperatura bajo cero en zonas andinas de heladas con poca lluvia."""
    level, _ = classifier.evaluate(precipitation=10.0, temperature=-5.0)
    assert level == RiskLevel.NORMAL


def test_rechazo_valores_nulos(classifier):
    """Valores None en precipitación o temperatura deben retornar INVALIDO."""
    level_p, _ = classifier.evaluate(precipitation=None, temperature=25.0)
    assert level_p == RiskLevel.INVALIDO

    level_t, _ = classifier.evaluate(precipitation=50.0, temperature=None)
    assert level_t == RiskLevel.INVALIDO


def test_rechazo_precipitacion_negativa(classifier):
    """Precipitaciones negativas (< 0 mm) son físicamente imposibles."""
    level, motivo = classifier.evaluate(precipitation=-15.0, temperature=22.0)
    assert level == RiskLevel.INVALIDO
    assert "negativa" in motivo.lower()


def test_rechazo_temperatura_fuera_de_rango(classifier):
    """Temperaturas fuera de [-40, 60] °C deben ser invalidadas."""
    level_frio, _ = classifier.evaluate(precipitation=20.0, temperature=-80.0)
    assert level_frio == RiskLevel.INVALIDO

    level_calor, _ = classifier.evaluate(precipitation=20.0, temperature=95.0)
    assert level_calor == RiskLevel.INVALIDO


def test_rechazo_datos_no_numericos(classifier):
    """Strings que no puedan convertirse a flotantes deben ser rechazados."""
    level, _ = classifier.evaluate(precipitation="muchisima_lluvia", temperature=25.0)
    assert level == RiskLevel.INVALIDO
