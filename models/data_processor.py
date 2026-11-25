"""
Módulo de Procesamiento de Datos y Demostración de Programación Funcional
Curso: Lenguajes de Programación - Unidad 1: Programación Funcional
Implementa funciones puras, inmutabilidad, funciones de orden superior,
composición funcional, lambda, map/filter/reduce y transformaciones declarativas con pandas.
"""

from functools import reduce
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar
import numpy as np
import pandas as pd

from models.logic_engine import RuleEngine
from models.risk_classifier import RiskClassifier, RiskLevel

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')


# ==============================================================================
# 1. FUNCIONES PURAS Y DE VALIDACIÓN (UNIDAD 1: CONCEPTOS FUNDAMENTALES)
# ==============================================================================

def normalizar_medicion(medicion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Función pura: Normaliza valores numéricos y nombres sin mutar el diccionario original.
    Retorna un nuevo diccionario garantizando inmutabilidad.
    """
    nueva_medicion = dict(medicion)
    try:
        p = float(nueva_medicion.get("precipitation_mm", 0.0))
        t = float(nueva_medicion.get("temperature_c", 0.0))
    except (ValueError, TypeError):
        p, t = 0.0, 0.0

    nueva_medicion["precipitation_mm"] = round(max(0.0, p), 2)
    nueva_medicion["temperature_c"] = round(t, 2)
    nueva_medicion["region"] = str(nueva_medicion.get("region", "")).strip().title()
    return nueva_medicion


def validar_medicion(medicion: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Función pura: Verifica la consistencia y plausibilidad de una medición.
    Retorna (es_valido, motivo_error).
    """
    p = medicion.get("precipitation_mm")
    t = medicion.get("temperature_c")
    if p is None or t is None:
        return False, "Valores nulos no permitidos"
    try:
        p_val = float(p)
        t_val = float(t)
    except (ValueError, TypeError):
        return False, "Tipos de datos no numéricos"

    if p_val < 0.0 or p_val > 1500.0:
        return False, f"Precipitación fuera de rango físico [0, 1500] mm: {p_val}"
    if t_val < -40.0 or t_val > 60.0:
        return False, f"Temperatura fuera de rango físico [-40, 60] °C: {t_val}"

    return True, None


def calcular_promedio(valores: List[float]) -> float:
    """
    Función pura: Calcula el promedio aritmético de una lista usando reduce().
    Demuestra funciones de orden superior y programación declarativa.
    """
    if not valores:
        return 0.0
    suma = reduce(lambda acumulador, elem: acumulador + elem, valores, 0.0)
    return round(suma / len(valores), 2)


def clasificar_precipitacion(p: float, t: float) -> str:
    """
    Función pura: Evalúa niveles de riesgo aplicando el clasificador centralizado.
    """
    classifier = RiskClassifier()
    level, _ = classifier.evaluate(p, t)
    return level.value


# ==============================================================================
# 2. FUNCIONES DE ORDEN SUPERIOR, CURRYING Y COMPOSICIÓN (UNIDAD 1)
# ==============================================================================

def componer(*funciones: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    Composición de funciones matemáticas: (f ∘ g)(x) = f(g(x)).
    Recibe una secuencia de funciones y retorna una nueva función compuesta.
    """
    def _compuesto(x: Any) -> Any:
        return reduce(lambda acumulado, f: f(acumulado), reversed(funciones), x)
    return _compuesto


def curried_filtro_riesgo(nivel_riesgo: str) -> Callable[[Dict[str, Any]], bool]:
    """
    Currying / Clausura funcional: Retorna un predicado que evalúa si un registro
    pertenece al nivel de riesgo especificado.
    """
    return lambda rec: str(rec.get("risk_level", "")).lower() == nivel_riesgo.lower()


def transformar_coleccion(
    coleccion: List[T],
    transformador: Callable[[T], U]
) -> List[U]:
    """
    Función de orden superior genérica: Aplica transformador sobre cada elemento.
    Equivalente declarativo a map() puro.
    """
    return list(map(transformador, coleccion))


def filtrar_coleccion(
    coleccion: List[T],
    predicado: Callable[[T], bool]
) -> List[T]:
    """
    Función de orden superior genérica: Filtra elementos que satisfacen un predicado.
    Equivalente declarativo a filter() puro.
    """
    return list(filter(predicado, coleccion))


# ==============================================================================
# 3. PIPELINES DECLARATIVOS CON PANDAS (INMUTABILIDAD CON COPY, ASSIGN Y PIPE)
# ==============================================================================

def limpiar_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Paso del pipeline: Remueve registros incompletos o atípicos de forma inmutable.
    """
    df_clean = df.copy()
    df_clean = df_clean.dropna(subset=["precipitation_mm", "temperature_c"])
    df_clean = df_clean[
        (df_clean["precipitation_mm"] >= 0.0) & 
        (df_clean["precipitation_mm"] <= 1500.0) &
        (df_clean["temperature_c"] >= -40.0) &
        (df_clean["temperature_c"] <= 60.0)
    ]
    return df_clean


def enriquecer_anomalias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Paso del pipeline: Agrega banderas analíticas mediante assign() sin mutar el original.
    """
    precip_mean = df["precipitation_mm"].mean() if not df.empty else 0.0
    return df.assign(
        anomalia_precipitacion=lambda d: (d["precipitation_mm"] - precip_mean).round(2),
        es_costa_norte=lambda d: d.get("is_coastal_north", False)
    )


# ==============================================================================
# 4. CLASE PROCESADORA DE DATOS (ARQUITECTURA MVC Y POO)
# ==============================================================================

class ElNinoDataProcessor:
    """
    Procesador de datos meteorológicos. Integra programación funcional con la arquitectura MVC.
    Garantiza inmutabilidad en las transformaciones de DataFrames.
    """

    def __init__(self):
        self.rule_engine = RuleEngine()

    def process_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Procesa el dataset aplicando un pipeline declarativo y evaluación de riesgo.
        
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (df_completo_evaluado, df_zonas_en_riesgo)
        """
        if df.empty:
            return df.copy(), df.copy()

        # Pipeline inmutable con pandas .pipe() y .assign()
        df_processed = (
            df.copy()
            .pipe(limpiar_dataset)
            .pipe(enriquecer_anomalias)
        )

        # Aplicación funcional de reglas lógicas
        evaluar_fila = lambda row: self.rule_engine.evaluate(row.to_dict())
        justificar_fila = lambda row: self.rule_engine.evaluate_with_justification(row.to_dict())[1]

        df_processed = df_processed.assign(
            risk_level=df_processed.apply(evaluar_fila, axis=1),
            justification=df_processed.apply(justificar_fila, axis=1),
            engine_used="Python RuleEngine"
        )

        # Filtrado funcional de zonas vulnerables
        at_risk = df_processed[df_processed["risk_level"] != RiskLevel.NORMAL.value].copy()
        return df_processed, at_risk

    @staticmethod
    def calcular_resumen_estadistico(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Genera un resumen estadístico detallado usando métodos vectorizados de pandas y NumPy.
        Demuestra agrupación, detección de nulos y estadísticas de dispersión.
        """
        if df.empty:
            return {"total_registros": 0}

        precip = df["precipitation_mm"]
        temp = df["temperature_c"]

        conteo_riesgos = df["risk_level"].value_counts().to_dict() if "risk_level" in df.columns else {}

        return {
            "total_registros": len(df),
            "valores_nulos_detectados": int(df.isnull().sum().sum()),
            "precipitacion": {
                "promedio_mm": round(float(precip.mean()), 2),
                "mediana_mm": round(float(precip.median()), 2),
                "desviacion_estandar_mm": round(float(precip.std()), 2),
                "maximo_mm": round(float(precip.max()), 2),
                "minimo_mm": round(float(precip.min()), 2),
            },
            "temperatura": {
                "promedio_c": round(float(temp.mean()), 2),
                "maximo_c": round(float(temp.max()), 2),
                "minimo_c": round(float(temp.min()), 2),
            },
            "distribucion_riesgos": conteo_riesgos
        }

    @staticmethod
    def run_functional_demo() -> Dict[str, Any]:
        """
        Ejecuta una demostración interactiva de los conceptos de Programación Funcional
        para la exposición universitaria de la Unidad 1.
        """
        # 1. Lista de mediciones crudas (Valores inmutables)
        mediciones_crudas = [
            {"region": "  piura ", "precipitation_mm": "165.2", "temperature_c": "32.1"},
            {"region": "tumbes", "precipitation_mm": 180.0, "temperature_c": 31.5},
            {"region": "LIMA", "precipitation_mm": 8.4, "temperature_c": 21.0},
            {"region": "cusco", "precipitation_mm": 55.0, "temperature_c": 17.5},
            {"region": "arequipa", "precipitation_mm": -5.0, "temperature_c": 19.0}, # Inválido
        ]

        # 2. Funciones de orden superior: map() con normalizar_medicion
        mediciones_normalizadas = list(map(normalizar_medicion, mediciones_crudas))

        # 3. filter() con predicado lambda
        mediciones_validas = list(filter(lambda m: validar_medicion(m)[0], mediciones_normalizadas))

        # 4. Clasificación funcional con clasificar_precipitacion
        mediciones_clasificadas = list(map(
            lambda m: {**m, "risk_level": clasificar_precipitacion(m["precipitation_mm"], m["temperature_c"])},
            mediciones_validas
        ))

        # 5. Currying: filtrar exclusivamente los extremos
        es_extremo = curried_filtro_riesgo(RiskLevel.EXTREMO.value)
        solo_extremos = list(filter(es_extremo, mediciones_clasificadas))

        # 6. reduce(): calcular promedio de precipitación de zonas válidas
        lluvias = [m["precipitation_mm"] for m in mediciones_validas]
        promedio_lluvia = calcular_promedio(lluvias)

        # 7. Composición de funciones: f(g(x))
        # Ejemplo: limpiar texto -> agregar prefijo -> pasar a mayúsculas
        dar_formato = componer(
            lambda s: f"ALERTA: {s}",
            lambda s: s.upper(),
            lambda s: s.strip()
        )
        mensaje_compuesto = dar_formato("zona de alta vulnerabilidad")

        return {
            "total_originales": len(mediciones_crudas),
            "total_validas": len(mediciones_validas),
            "promedio_lluvia_reducido": promedio_lluvia,
            "zonas_extremas_detectadas": [m["region"] for m in solo_extremos],
            "ejemplo_composicion": mensaje_compuesto,
            "detalle_clasificadas": mediciones_clasificadas
        }
