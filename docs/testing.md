# Plan y Reporte de Pruebas Automatizadas (Pytest)

## 1. Estrategia de Pruebas y Marco de Trabajo

Para garantizar la estabilidad, consistencia matemática e integridad lógica del sistema, se implementó una suite integral de pruebas automatizadas utilizando **Pytest (versión 9.2.0)**.

Las pruebas cubren tanto casos nominales como valores frontera, datos extremos, entradas nulas e inválidas, transacciones de base de datos y generación de artefactos cartográficos.

---

## 2. Módulos de Prueba Implementados

| Archivo de Prueba | Módulo Objetivo | Propósito y Alcance | Casos |
| :--- | :--- | :--- | :---: |
| `tests/test_risk_classifier.py` | `models/risk_classifier.py` | Validación de umbrales límite (40mm, 80mm, 120mm, 30°C), corrección de la laguna lógica, entradas nulas, valores negativos y límites físicos. | 12 |
| `tests/test_data_processor.py` | `models/data_processor.py` | Funciones puras, inmutabilidad de diccionarios, cálculo declarativo con `reduce()`, composición funcional `(f ∘ g)(x)`, currying y pipelines de Pandas. | 7 |
| `tests/test_data_providers.py` | `models/data_providers.py` | Catálogo de 25 departamentos, rangos geográficos válidos del Perú, polimorfismo de `DataProvider` y reproducibilidad estocástica de semillas. | 4 |
| `tests/test_logic_engine.py` | `models/logic_engine.py` | Precedencia de reglas en Python, activación de justificaciones y corrección del defecto de lluvia extrema con baja temperatura. | 3 |
| `tests/test_prolog_engine.py` | `models/prolog_engine.py` | Detección de binario `swipl`, existencia de `el_nino_rules.pl`, sanitización de átomos con caracteres especiales y claridad en instrucciones. | 4 |
| `tests/test_database.py` | `models/database.py` | Creación de tablas, población automática del catálogo, transacciones atómicas de lotes, consultas parametrizadas y resúmenes SQL. | 3 |
| `tests/test_map_view.py` | `views/map_view.py` | Generación del archivo HTML con Folium, validación de capas Leaflet/Esri y renderizado de leyendas. | 1 |
| `tests/test_scraper.py` | `models/scraper.py` | Scraping de Wikipedia con headers, fallback defensivo y asignación de coordenadas oficiales. | 2 |

**Total de casos de prueba automatizados:** **36 pruebas unitarias e integrales**.

---

## 3. Casos Especiales y Pruebas de Frontera Críticas

### 3.1 Verificación de Umbrales Límite
- **Precipitación = 40.0 mm:** Evaluada como **Riesgo Normal** (`test_clasificacion_limite_exacto_40mm`).
- **Precipitación = 80.0 mm:** Evaluada como **Riesgo Moderado** (`test_clasificacion_limite_exacto_80mm`).
- **Precipitación = 120.0 mm:** Evaluada como **Riesgo Alto** (`test_clasificacion_limite_exacto_120mm`).

### 3.2 Corrección del Defecto Lógico (Bug Fix)
- **Escenario:** Precipitación > 120 mm (ej. 135 mm o 150 mm) con Temperatura <= 30.0 °C (ej. 30.0 °C o 18.0 °C).
- **Comportamiento previo defectuoso:** Caía en la regla por defecto ("Riesgo Normal").
- **Comportamiento corregido verificado:** Clasificado deterministamente como **Riesgo Alto** (`test_clasificacion_lluvia_extrema_con_temperatura_limite_30c` y `test_clasificacion_lluvia_extrema_con_baja_temperatura`).

### 3.3 Tolerancia a Fallos y Límites Físicos
- **Valores Nulos (`None`):** Retorna `RiskLevel.INVALIDO` sin lanzar excepciones no controladas.
- **Precipitaciones Negativas (< 0 mm):** Rechazadas como físicamente inadmisibles.
- **Temperaturas Negativas Válidas (-5 °C):** Permitidas para modelar heladas en la sierra sur peruana.
- **Temperaturas Extremas Inadmisibles (< -40 °C o > 60 °C):** Invalidadas por exceder los récords meteorológicos del Perú.

---

## 4. Resultados Reales de la Ejecución

Comando ejecutado en la terminal del proyecto:
```bash
.\venv\Scripts\pytest -v
```

Salida registrada en consola:
```text
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.2.0, pluggy-1.7.0 -- .\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\alfre\OneDrive\Escritorio\utp\ciclo 07\proyecti lenguajes de programcion
collecting ... collected 36 items

tests/test_data_processor.py::test_normalizar_medicion_puro_e_inmutable PASSED [  2%]
tests/test_data_processor.py::test_validar_medicion_casos PASSED         [  5%]
tests/test_data_processor.py::test_calcular_promedio_con_reduce PASSED   [  8%]
tests/test_data_processor.py::test_composicion_de_funciones PASSED       [ 11%]
tests/test_data_processor.py::test_currying_filtro_riesgo PASSED         [ 13%]
tests/test_data_processor.py::test_pipeline_procesamiento_inmutable_dataframe PASSED [ 16%]
tests/test_data_processor.py::test_resumen_estadistico_pandas PASSED     [ 19%]
tests/test_data_providers.py::test_catalogo_regiones_oficiales PASSED    [ 22%]
tests/test_data_providers.py::test_simulador_reproducibilidad_con_semilla PASSED [ 25%]
tests/test_data_providers.py::test_simulador_advertencia_clara PASSED    [ 27%]
tests/test_data_providers.py::test_polimorfismo_data_provider PASSED     [ 30%]
tests/test_database.py::test_inicializacion_esquema_y_regiones PASSED    [ 33%]
tests/test_database.py::test_guardado_y_recuperacion_historica PASSED    [ 36%]
tests/test_database.py::test_resumen_estadistico_sql PASSED              [ 38%]
tests/test_logic_engine.py::test_motor_reglas_extremo PASSED             [ 41%]
tests/test_logic_engine.py::test_motor_reglas_correccion_defecto_lluvia_extrema_temp_moderada PASSED [ 44%]
tests/test_logic_engine.py::test_motor_reglas_precedencia_validaciones PASSED [ 47%]
tests/test_map_view.py::test_generacion_archivo_mapa_html PASSED         [ 50%]
tests/test_prolog_engine.py::test_archivo_reglas_prolog_existe PASSED    [ 52%]
tests/test_prolog_engine.py::test_sanitizacion_atomos_prolog PASSED      [ 55%]
tests/test_prolog_engine.py::test_mapeo_atomos_prolog_a_enum PASSED      [ 58%]
tests/test_prolog_engine.py::test_instrucciones_instalacion_claras PASSED [ 61%]
tests/test_risk_classifier.py::test_clasificacion_limite_exacto_40mm PASSED [ 63%]
tests/test_risk_classifier.py::test_clasificacion_limite_exacto_80mm PASSED [ 66%]
tests/test_risk_classifier.py::test_clasificacion_limite_exacto_120mm PASSED [ 69%]
tests/test_risk_classifier.py::test_clasificacion_lluvia_extrema_con_temperatura_limite_30c PASSED [ 72%]
tests/test_risk_classifier.py::test_clasificacion_lluvia_extrema_con_baja_temperatura PASSED [ 75%]
tests/test_risk_classifier.py::test_clasificacion_riesgo_extremo_el_nino PASSED [ 77%]
tests/test_risk_classifier.py::test_clasificacion_lluvia_extremadamente_elevada PASSED [ 80%]
tests/test_risk_classifier.py::test_clasificacion_temperatura_negativa_valida PASSED [ 83%]
tests/test_risk_classifier.py::test_rechazo_valores_nulos PASSED         [ 86%]
tests/test_risk_classifier.py::test_rechazo_precipitacion_negativa PASSED [ 88%]
tests/test_risk_classifier.py::test_rechazo_temperatura_fuera_de_rango PASSED [ 91%]
tests/test_risk_classifier.py::test_rechazo_datos_no_numericos PASSED    [ 94%]
tests/test_scraper.py::test_scraper_extrae_departamentos PASSED          [ 97%]
tests/test_scraper.py::test_scraper_generacion_datos_con_coordenadas_reales PASSED [100%]

============================= 36 passed in 2.88s ==============================
```

> **Tasa de éxito:** 100% (36 pruebas aprobadas, 0 fallas, 0 errores).
