"""
Motor de Reglas y Clasificación en Python
Implementa un sistema de inferencia basado en reglas con prioridades,
manejo exhaustivo de rangos, validación de valores nulos y compatibilidad hacia atrás.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from models.risk_classifier import RiskClassifier, RiskLevel, RiskThresholds


class Rule:
    """Representa una regla declarativa individual con condición, conclusión, prioridad y justificación."""
    def __init__(
        self,
        condition: Callable[[Dict[str, Any]], bool],
        conclusion: str,
        priority: int,
        description: str = ""
    ):
        self.condition = condition
        self.conclusion = conclusion
        self.priority = priority
        self.description = description

    def matches(self, fact: Dict[str, Any]) -> bool:
        try:
            return bool(self.condition(fact))
        except Exception:
            return False


class RuleEngine:
    """
    Motor de inferencia basado en reglas ordenadas por precedencia.
    Corrige la laguna donde precipitaciones > 120 mm con temperatura <= 30°C
    quedaban sin clasificar (ahora categorizadas exhaustivamente).
    """

    def __init__(self, thresholds: Optional[RiskThresholds] = None):
        self.classifier = RiskClassifier(thresholds)
        self.rules: List[Rule] = []
        self._setup_default_rules()

    def add_rule(
        self,
        condition: Callable[[Dict[str, Any]], bool],
        conclusion: str,
        priority: int = 10,
        description: str = ""
    ) -> None:
        """Agrega una regla personalizada con prioridad (menor número = mayor precedencia)."""
        rule = Rule(condition, conclusion, priority, description)
        self.rules.append(rule)
        # Ordenar por prioridad ascendente
        self.rules.sort(key=lambda r: r.priority)

    def _setup_default_rules(self) -> None:
        """Configura la tabla de decisión completa y sin huecos lógicos."""
        th = self.classifier.thresholds
        
        # Prioridad 1: Validación de valores nulos o inválidos
        self.add_rule(
            lambda f: (
                f.get('precipitation_mm') is None or
                f.get('temperature_c') is None or
                float(f.get('precipitation_mm', -1)) < th.MIN_VALID_PRECIPITATION or
                float(f.get('precipitation_mm', 9999)) > th.MAX_VALID_PRECIPITATION or
                float(f.get('temperature_c', -999)) < th.MIN_VALID_TEMPERATURE or
                float(f.get('temperature_c', 999)) > th.MAX_VALID_TEMPERATURE
            ),
            RiskLevel.INVALIDO.value,
            priority=1,
            description="Validación de integridad física de las mediciones"
        )

        # Prioridad 2: Riesgo Extremo (Torrencial + Calor extremo)
        self.add_rule(
            lambda f: (
                float(f['precipitation_mm']) > th.PRECIPITATION_EXTREME and
                float(f['temperature_c']) > th.TEMPERATURE_EXTREME
            ),
            RiskLevel.EXTREMO.value,
            priority=2,
            description=f"Precipitación > {th.PRECIPITATION_EXTREME} mm y Temp > {th.TEMPERATURE_EXTREME} °C"
        )

        # Prioridad 3: Riesgo Alto - Corrección del defecto original (Lluvia extrema con temp moderada/baja)
        self.add_rule(
            lambda f: (
                float(f['precipitation_mm']) > th.PRECIPITATION_EXTREME and
                float(f['temperature_c']) <= th.TEMPERATURE_EXTREME
            ),
            RiskLevel.ALTO.value,
            priority=3,
            description=f"Precipitación extrema > {th.PRECIPITATION_EXTREME} mm con Temp <= {th.TEMPERATURE_EXTREME} °C"
        )

        # Prioridad 4: Riesgo Alto estándar (80 < P <= 120 mm)
        self.add_rule(
            lambda f: (
                th.PRECIPITATION_HIGH < float(f['precipitation_mm']) <= th.PRECIPITATION_EXTREME
            ),
            RiskLevel.ALTO.value,
            priority=4,
            description=f"Precipitación entre {th.PRECIPITATION_HIGH} y {th.PRECIPITATION_EXTREME} mm"
        )

        # Prioridad 5: Riesgo Moderado (40 < P <= 80 mm)
        self.add_rule(
            lambda f: (
                th.PRECIPITATION_MODERATE < float(f['precipitation_mm']) <= th.PRECIPITATION_HIGH
            ),
            RiskLevel.MODERADO.value,
            priority=5,
            description=f"Precipitación entre {th.PRECIPITATION_MODERATE} y {th.PRECIPITATION_HIGH} mm"
        )

        # Prioridad 6: Riesgo Normal (0 <= P <= 40 mm)
        self.add_rule(
            lambda f: (
                th.MIN_VALID_PRECIPITATION <= float(f['precipitation_mm']) <= th.PRECIPITATION_MODERATE
            ),
            RiskLevel.NORMAL.value,
            priority=6,
            description=f"Precipitación normal/baja <= {th.PRECIPITATION_MODERATE} mm"
        )

    def evaluate(self, fact: Dict[str, Any]) -> str:
        """
        Evalúa un hecho dict contra las reglas en orden de prioridad.
        Retorna la conclusión string correspondiente.
        """
        conclusion, _ = self.evaluate_with_justification(fact)
        return conclusion

    def evaluate_with_justification(self, fact: Dict[str, Any]) -> Tuple[str, str]:
        """
        Evalúa un hecho y retorna tanto la conclusión como la regla que la activó.
        """
        for rule in self.rules:
            if rule.matches(fact):
                return rule.conclusion, rule.description
                
        # Fallback defensivo usando el clasificador directo
        p = fact.get('precipitation_mm')
        t = fact.get('temperature_c')
        level, just = self.classifier.evaluate(p, t)
        return level.value, just
