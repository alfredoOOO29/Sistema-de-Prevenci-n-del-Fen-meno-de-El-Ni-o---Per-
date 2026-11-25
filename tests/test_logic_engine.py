"""
Pruebas Unitarias: Motor de Reglas en Python (Precedencia y Exhaustividad)
"""

import pytest
from models.logic_engine import RuleEngine
from models.risk_classifier import RiskLevel


@pytest.fixture
def rule_engine():
    return RuleEngine()


def test_motor_reglas_extremo(rule_engine):
    """Regla de prioridad alta: Lluvia extrema con calor extremo."""
    conclusion, desc = rule_engine.evaluate_with_justification({
        "precipitation_mm": 160.0,
        "temperature_c": 33.0
    })
    assert conclusion == RiskLevel.EXTREMO.value
    assert "120" in desc


def test_motor_reglas_correccion_defecto_lluvia_extrema_temp_moderada(rule_engine):
    """
    Verifica que el defecto reportado por el usuario esté resuelto:
    Precipitación > 120 mm con Temperatura <= 30 °C (ej. 24°C)
    debe clasificarse como Riesgo Alto, NO normal.
    """
    conclusion, _ = rule_engine.evaluate_with_justification({
        "precipitation_mm": 140.0,
        "temperature_c": 24.0
    })
    assert conclusion == RiskLevel.ALTO.value


def test_motor_reglas_precedencia_validaciones(rule_engine):
    """Las reglas de validación de integridad (prioridad 1) tienen precedencia sobre las demás."""
    conclusion, _ = rule_engine.evaluate_with_justification({
        "precipitation_mm": None,
        "temperature_c": 35.0
    })
    assert conclusion == RiskLevel.INVALIDO.value
