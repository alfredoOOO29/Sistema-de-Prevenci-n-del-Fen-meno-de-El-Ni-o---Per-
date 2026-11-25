# Demostración Académica de Paradigmas de Programación
**Curso:** Lenguajes de Programación — Ingeniería de Sistemas e Informática (UTP)  
**Proyecto:** Sistema de Prevención del Fenómeno de El Niño en el Perú  
**Documento de Sustentación Teórico-Práctica**

---

# UNIDAD 1: PROGRAMACIÓN FUNCIONAL

El paradigma funcional concibe el cómputo como la evaluación de funciones matemáticas puras, evitando el estado mutable y los efectos secundarios (*side-effects*). En este proyecto se implementaron de forma explícita los siguientes fundamentos:

## 1.1 Programas como Funciones y Funciones Definidas
- **Concepto:** Las funciones son ciudadanos de primer orden (*first-class citizens*), pueden ser nombradas, asignadas a variables y evaluadas de forma aislada.
- **Implementación:** `models/data_processor.py`
```python
def normalizar_medicion(medicion: Dict[str, Any]) -> Dict[str, Any]:
    nueva_medicion = dict(medicion)
    p = float(nueva_medicion.get("precipitation_mm", 0.0))
    t = float(nueva_medicion.get("temperature_c", 0.0))
    nueva_medicion["precipitation_mm"] = round(max(0.0, p), 2)
    nueva_medicion["temperature_c"] = round(t, 2)
    nueva_medicion["region"] = str(nueva_medicion.get("region", "")).strip().title()
    return nueva_medicion
```

## 1.2 Inmutabilidad y Funciones Puras
- **Concepto:** Una función pura garantiza transparencia referencial: ante las mismas entradas siempre produce la misma salida, sin modificar variables externas ni los argumentos recibidos.
- **Implementación:** `models/data_processor.py`
  - La función `normalizar_medicion` crea un nuevo diccionario `dict(medicion)` en lugar de modificar la estructura recibida.
  - En `tests/test_data_processor.py`, la prueba `test_normalizar_medicion_puro_e_inmutable` verifica formalmente que el objeto de entrada no sea mutado.

## 1.3 Funciones Anónimas (Lambda)
- **Concepto:** Funciones sin identificador nominal empleadas para transformaciones puntuales o proyecciones.
- **Implementación:** `models/scraper.py` y `models/data_processor.py`
```python
# models/scraper.py (Generación estocástica condicional)
rain_generator = lambda n: np.random.normal(160, 40) if n else np.random.normal(25, 12)

# models/data_processor.py (Evaluación declarativa sobre DataFrames)
evaluar_fila = lambda row: self.rule_engine.evaluate(row.to_dict())
```

## 1.4 Funciones como Parámetros y Funciones de Orden Superior
- **Concepto:** Una función de orden superior (*Higher-Order Function*) recibe una o más funciones como parámetros o retorna una función como resultado.
- **Implementación:** `models/data_processor.py`
```python
def filtrar_coleccion(coleccion: List[T], predicado: Callable[[T], bool]) -> List[T]:
    return list(filter(predicado, coleccion))
```
- **Uso de `map()`, `filter()` y `reduce()`:**
  - `map()`: Aplica la función pura `normalizar_medicion` a toda la lista de registros crudos.
  - `filter()`: Filtra mediciones inválidas usando `validar_medicion`.
  - `reduce()`: Acumula y suma elementos sin bucles en `calcular_promedio()`:
```python
def calcular_promedio(valores: List[float]) -> float:
    if not valores:
        return 0.0
    suma = reduce(lambda acumulador, elem: acumulador + elem, valores, 0.0)
    return round(suma / len(valores), 2)
```

## 1.5 Currying y Clausuras Funcionales
- **Concepto:** Descomposición de una función de múltiples argumentos en una secuencia de funciones que toman un único argumento cada una.
- **Implementación:** `models/data_processor.py`
```python
def curried_filtro_riesgo(nivel_riesgo: str) -> Callable[[Dict[str, Any]], bool]:
    return lambda rec: str(rec.get("risk_level", "")).lower() == nivel_riesgo.lower()

# Uso:
es_extremo = curried_filtro_riesgo("Riesgo de Inundacion Extremo")
zonas_criticas = list(filter(es_extremo, mediciones))
```

## 1.6 Composición de Funciones
- **Concepto:** Combinación algebraica de funciones donde la salida de una función es la entrada de la siguiente: $(f \circ g \circ h)(x) = f(g(h(x)))$.
- **Implementación:** `models/data_processor.py`
```python
def componer(*funciones: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def _compuesto(x: Any) -> Any:
        return reduce(lambda acumulado, f: f(acumulado), reversed(funciones), x)
    return _compuesto
```

## 1.7 Pipelines Declarativos con Pandas (`pipe`, `assign`, `copy`)
- **Concepto:** Procesamiento encadenado inmutable de estructuras tabulares, evitando reasignaciones y modificaciones en sitio (*in-place*).
- **Implementación:** `models/data_processor.py` (`ElNinoDataProcessor.process_data`)
```python
df_processed = (
    df.copy()
    .pipe(limpiar_dataset)
    .pipe(enriquecer_anomalias)
)
```

---

# UNIDAD 2: PROGRAMACIÓN LÓGICA (PROLOG)

A diferencia de los paradigmas imperativos, la programación lógica expresa **relaciones declarativas** entre entidades del dominio mediante **hechos, predicados y reglas**, delegando la deducción al motor de inferencia mediante **unificación y resolución con backtracking**.

En este proyecto se implementó un motor real de Prolog en el archivo `logic/el_nino_rules.pl` y su adaptador en `models/prolog_engine.py`.

## 2.1 Términos, Átomos y Constantes
- **Átomos:** Identificadores que inician en minúscula o van entre comillas simples: `piura`, `tumbes`, `extremo`, `alto`, `moderado`, `normal`, `invalido`.
- **Constantes numéricas:** Valores flotantes y enteros: `120.0`, `30.0`, `80.0`, `40.0`.
- **Términos compuestos:** Estructuras functor-argumento: `medicion(piura, 142.0, 31.0)`.

## 2.2 Predicados y Hechos
- **Hechos:** Declaraciones incondicionales de verdades en el universo del discurso.
- **Implementación:** `logic/test_facts.pl`
```prolog
% Hechos atómicos de regiones
region(piura).
region(tumbes).

% Hechos de mediciones observadas
precipitacion(piura, 142.0).
temperatura(piura, 31.0).

% Hecho en término compuesto
medicion(piura, 142.0, 31.0).
```

## 2.3 Reglas Lógicas
- **Concepto:** Deducciones condicionales de la forma `Cabeza :- Cuerpo` (Conclusión si Premisas son verdaderas).
- **Implementación:** `logic/el_nino_rules.pl`
```prolog
% Regla 1: Riesgo Extremo
clasificar_riesgo(P, T, extremo) :-
    umbral_precipitacion_extremo(P_Ext),
    umbral_temperatura_extremo(T_Ext),
    P > P_Ext,
    T > T_Ext,
    !.

% Regla 2: Riesgo Alto por Lluvia Torrencial con Temperatura Moderada (Corrección del defecto)
clasificar_riesgo(P, _, alto) :-
    umbral_precipitacion_extremo(P_Ext),
    P > P_Ext,
    !.

% Regla 3: Riesgo Alto estándar
clasificar_riesgo(P, _, alto) :-
    umbral_precipitacion_alto(P_Alto),
    umbral_precipitacion_extremo(P_Ext),
    P > P_Alto,
    P =< P_Ext,
    !.
```

## 2.4 Control de Ejecución mediante el Operador de Corte (`!`)
- **Concepto:** El operador `!` poda el árbol de búsqueda de Prolog, evitando que el motor retroceda (*backtrack*) a evaluar reglas de menor severidad una vez que se satisfizo una categoría más alta.
- **Ejemplo:** En `clasificar_riesgo(P, T, extremo) :- ... !.`, si $P > 120$ y $T > 30$, se asigna `extremo` y el corte impide evaluar las reglas de riesgo alto o moderado.

## 2.5 Unificación y Resolución
- **Unificación:** Proceso de emparejar dos términos ligando variables libres a valores concretos.
- **Resolución:** Deducción lógica mediante el algoritmo SLD-Resolution para responder a una meta (*goal*).
- **Ejemplo de Consulta:**
```prolog
?- clasificar_riesgo(150.0, 32.0, Riesgo).
% Prolog unifica P=150.0, T=32.0 y resuelve la variable:
% Riesgo = extremo.
```

## 2.6 Backtracking e Indeterminismo
- **Concepto:** Cuando una consulta admite múltiples soluciones, el motor explora todas las ramas válidas volviendo atrás automáticamente al fallar o al solicitar más alternativas con `;`.
- **Implementación:** `logic/test_facts.pl`
```prolog
% Consulta interactiva que recupera todas las regiones en riesgo extremo por backtracking:
?- evaluar_region(Region, extremo).
% Solución 1: Region = tumbes ;
% Solución 2: Region = piura.
```

## 2.7 Estructuras de Datos mediante Listas y Recursión
- **Concepto:** Listas representadas como `[Cabeza | Cola]`, procesadas recursivamente sin variables mutables.
- **Implementación:** `logic/el_nino_rules.pl`
```prolog
% Caso base: lista vacía
longitud_lista([], 0).
% Caso recursivo: inducción estructural
longitud_lista([_|Resto], N) :-
    longitud_lista(Resto, NResto),
    N is NResto + 1.

% Consulta de orden superior en Prolog con findall/3
obtener_regiones_en_riesgo(NivelRiesgo, Regiones) :-
    findall(R, evaluar_region(R, NivelRiesgo), Regiones).
```

## 2.8 Adaptador de Integración Python-Prolog
- **Implementación:** `models/prolog_engine.py`
  - Invoca el proceso `swipl` pasando las mediciones del sistema y recuperando las clasificaciones unificadas.
  - Implementa manejo de ausencia del binario sin falsear la ejecución: informa honestamente al usuario cómo instalar SWI-Prolog.

---

# UNIDAD 3: PROGRAMACIÓN MULTIPARADIGMA Y ORIENTADA A OBJETOS

Python combina armónicamente características de POO, programación imperativa estructurada, funcional y científica. En el sistema se demuestran los siguientes contenidos:

## 3.1 Estructuras de Datos Nativas y Tipos
- **Primitivos:** `float` (precipitación, latitud), `int` (códigos, contadores), `str` (nombres de departamentos), `bool` (`is_simulation`).
- **Tuplas:** Valores inmutables para coordenadas y retornos múltiples: `Tuple[bool, Optional[str]]` en `models/risk_classifier.py`.
- **Diccionarios:** Factores y mapas de configuración: `to_dict_summary()` en `models/risk_classifier.py` y hechos en `models/logic_engine.py`.
- **Listas:** Colecciones ordenadas de regiones y reglas: `self.rules: List[Rule] = []`.

## 3.2 Programación Orientada a Objetos (POO)

### Abstracción
Ocultamiento de la complejidad interna definiendo interfaces claras.
- **Implementación:** `DataProvider` en `models/data_providers.py` expone `fetch_data()` y `get_warning_message()`.

### Encapsulamiento
Protección de atributos internos mediante propiedades `@property` y métodos privados/protegidos.
- **Implementación:** `models/data_providers.py`
```python
class DataProvider(ABC):
    def __init__(self, source_name: str, is_simulation: bool):
        self._source_name = source_name
        self._is_simulation = is_simulation

    @property
    def source_name(self) -> str:
        return self._source_name
```

### Herencia
Reutilización de código y especialización jerárquica justificada.
- **Implementación:** `models/data_providers.py`
  - `SimulatedDataProvider(DataProvider)`
  - `OpenMeteoDataProvider(DataProvider)`

### Polimorfismo
Capacidad de tratar instancias de diferentes clases a través de una interfaz común.
- **Implementación:** En `MainController`, tanto el proveedor simulado como el de la API Open-Meteo se invocan polimórficamente mediante `.fetch_data()`.

## 3.3 Introducción a NumPy (Cálculo Científico y Estocástico)
- **Concepto:** Arreglos multidimensionales y distribuciones estadísticas reproducibles para modelado probabilístico.
- **Implementación:** `models/data_providers.py` (`SimulatedDataProvider.fetch_data`)
```python
np.random.seed(self.random_seed)
rain = max(0.0, float(np.random.normal(160.0, 35.0)))
temp = float(np.random.normal(32.5, 1.8))
```

## 3.4 Introducción a Pandas (Análisis y Transformación Tabular)
- **DataFrames y Series:** Estructuración matricial de mediciones hidrometeorológicas.
- **Agrupamiento y Agregaciones Estadísticas:**
  - `df.groupby()`, `mean()`, `std()`, `median()`, `value_counts()` en `models/data_processor.py`.
- **Filtrado Vectorizado y Detección de Nulos:**
  - `df.isnull().sum()`, `df.dropna()`.
