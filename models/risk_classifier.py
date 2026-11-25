"""
Módulo de Clasificación de Riesgo Hidrometeorológico
Define umbrales centralizados, niveles de riesgo y matriz de decisión determinista.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional, Any, Dict


class RiskLevel(str, Enum):
    """Niveles de riesgo clasificados según severidad."""
    EXTREMO = "Riesgo de Inundacion Extremo"
    ALTO = "Riesgo de Inundacion Alto"
    MODERADO = "Riesgo Moderado"
    NORMAL = "Riesgo Normal"
    INVALIDO = "Dato Invalido"


@dataclass(frozen=True)
class RiskThresholds:
    """Umbrales cuantitativos configurables para la clasificación de riesgo."""
    PRECIPITATION_EXTREME: float = 120.0
    TEMPERATURE_EXTREME: float = 30.0
    PRECIPITATION_HIGH: float = 80.0
    PRECIPITATION_MODERATE: float = 40.0
    
    # Límites físicos para validación de datos
    MIN_VALID_PRECIPITATION: float = 0.0
    MAX_VALID_PRECIPITATION: float = 1500.0
    MIN_VALID_TEMPERATURE: float = -40.0
    MAX_VALID_TEMPERATURE: float = 60.0


class RiskClassifier:
    """
    Clasificador determinista basado en tabla de decisión completa.
    Resuelve vacíos lógicos (p.ej. lluvia > 120mm con temperatura <= 30°C clasificada como ALTO).
    """
    
    def __init__(self, thresholds: Optional[RiskThresholds] = None):
        self.thresholds = thresholds or RiskThresholds()

    def validate_inputs(self, precipitation: Any, temperature: Any) -> Tuple[bool, Optional[str]]:
        """
        Valida que las mediciones sean numéricas y se encuentren en rangos físicos razonables.
        
        Returns:
            Tuple[bool, Optional[str]]: (es_valido, motivo_error)
        """
        if precipitation is None or temperature is None:
            return False, "Valores nulos no permitidos"
            
        try:
            p = float(precipitation)
            t = float(temperature)
        except (ValueError, TypeError):
            return False, "Las mediciones deben ser valores numéricos"
            
        if p < self.thresholds.MIN_VALID_PRECIPITATION:
            return False, f"Precipitación negativa ({p} mm) no es válida"
            
        if p > self.thresholds.MAX_VALID_PRECIPITATION:
            return False, f"Precipitación fuera de rango físico plausible ({p} mm)"
            
        if t < self.thresholds.MIN_VALID_TEMPERATURE or t > self.thresholds.MAX_VALID_TEMPERATURE:
            return False, f"Temperatura fuera de rango físico ({t} °C)"
            
        return True, None

    def evaluate(self, precipitation: float, temperature: float) -> Tuple[RiskLevel, str]:
        """
        Evalúa las variables y retorna (RiskLevel, justificación).
        Tabla de decisión exhaustiva y sin solapamientos.
        """
        is_valid, error_msg = self.validate_inputs(precipitation, temperature)
        if not is_valid:
            return RiskLevel.INVALIDO, error_msg or "Entrada inválida"
            
        p = float(precipitation)
        t = float(temperature)
        th = self.thresholds
        
        # Regla 1: Torrencial extrema con calor extremo
        if p > th.PRECIPITATION_EXTREME and t > th.TEMPERATURE_EXTREME:
            return (
                RiskLevel.EXTREMO,
                f"Lluvia extrema ({p:.1f} mm > {th.PRECIPITATION_EXTREME} mm) combinada con alta temperatura ({t:.1f} °C > {th.TEMPERATURE_EXTREME} °C)"
            )
            
        # Regla 2: Lluvia extrema sin calor extremo (Corrección del defecto original)
        if p > th.PRECIPITATION_EXTREME and t <= th.TEMPERATURE_EXTREME:
            return (
                RiskLevel.ALTO,
                f"Lluvia extrema ({p:.1f} mm > {th.PRECIPITATION_EXTREME} mm) con temperatura moderada ({t:.1f} °C <= {th.TEMPERATURE_EXTREME} °C)"
            )
            
        # Regla 3: Lluvia alta (80 - 120 mm]
        if th.PRECIPITATION_HIGH < p <= th.PRECIPITATION_EXTREME:
            return (
                RiskLevel.ALTO,
                f"Precipitación alta ({p:.1f} mm en rango {th.PRECIPITATION_HIGH}-{th.PRECIPITATION_EXTREME} mm)"
            )
            
        # Regla 4: Lluvia moderada (40 - 80 mm]
        if th.PRECIPITATION_MODERATE < p <= th.PRECIPITATION_HIGH:
            return (
                RiskLevel.MODERADO,
                f"Precipitación moderada ({p:.1f} mm en rango {th.PRECIPITATION_MODERATE}-{th.PRECIPITATION_HIGH} mm)"
            )
            
        # Regla 5: Lluvia normal o baja [0 - 40 mm]
        if th.MIN_VALID_PRECIPITATION <= p <= th.PRECIPITATION_MODERATE:
            return (
                RiskLevel.NORMAL,
                f"Precipitación baja/normal ({p:.1f} mm <= {th.PRECIPITATION_MODERATE} mm)"
            )
            
        return RiskLevel.INVALIDO, "Condición no prevista en matriz de decisión"
        
    def to_dict_summary(self) -> Dict[str, Any]:
        """Retorna la configuración de umbrales como diccionario."""
        return {
            "umbral_extremo_lluvia_mm": self.thresholds.PRECIPITATION_EXTREME,
            "umbral_extremo_temp_c": self.thresholds.TEMPERATURE_EXTREME,
            "umbral_alto_lluvia_mm": self.thresholds.PRECIPITATION_HIGH,
            "umbral_moderado_lluvia_mm": self.thresholds.PRECIPITATION_MODERATE,
        }
