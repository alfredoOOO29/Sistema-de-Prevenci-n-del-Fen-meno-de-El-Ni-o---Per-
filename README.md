# 🌊 Sistema de Prevención del Fenómeno de El Niño en el Perú
> **Aplicación Universitaria Multiparadigma**  
> **Curso:** Lenguajes de Programación — Ingeniería de Sistemas e Informática  
> **Institución:** Universidad Tecnológica del Perú (UTP)

---

## 📌 1. Descripción del Proyecto

El **Sistema de Prevención del Fenómeno de El Niño en el Perú** es una plataforma de software académico diseñada para la monitorización, simulación hidrometeorológica, evaluación determinista y representación geoespacial del riesgo de inundaciones pluviales en los 24 departamentos del Perú y la Provincia Constitucional del Callao.

El proyecto aborda formalmente los tres núcleos temáticos del curso:
1. **Unidad 1: Programación Funcional** (Funciones puras, inmutabilidad, orden superior, `map`/`filter`/`reduce`, currying, composición y pipelines con Pandas).
2. **Unidad 2: Programación Lógica** (Inferencia declarativa real con **SWI-Prolog**, unificación, resolución, backtracking, corte `!` y manejo recursivo de listas).
3. **Unidad 3: Programación Multiparadigma y POO** (Arquitectura MVC, abstracción, herencia, polimorfismo, SQLite normalizado, cálculo estocástico con NumPy y análisis descriptivo con Pandas).

---

## 🎯 2. Características Principales

- 🗺️ **Catálogo Geoespacial Verificable:** Base fija de coordenadas oficiales para las 25 jurisdicciones peruanas (`data/regions.json`), eliminando posiciones aleatorias.
- 🌦️ **Doble Modalidad de Datos:**
  - **Modo Simulación:** Generación estocástica controlada con NumPy basada en escenarios (*Costa Norte Severa*, *Niño Moderado*, *Condiciones Normales*) con semilla aleatoria configurable y advertencia explícita de modelado académico.
  - **Modo Tiempo Real:** Conexión con la API meteorológica pública y abierta de **Open-Meteo** para consultar variables climáticas en vivo.
- 🧠 **Doble Motor de Inferencia y Comparación:**
  - **Motor Python (`RuleEngine`):** Sistema de reglas ordenadas por precedencia con resolución de vacíos lógicos (clasificación exhaustiva de lluvias > 120 mm con temperaturas moderadas).
  - **Motor Lógico Prolog (`SWI-Prolog`):** Inferencia formal mediante base de conocimiento declarativa en sintaxis Prolog pura (`logic/el_nino_rules.pl`).
  - **Modo Comparativo:** Auditoría lado a lado evaluando discrepancias y porcentaje de concordancia entre ambos motores.
- 💾 **Persistencia Relacional (SQLite):** Almacenamiento histórico normalizado (3NF) de regiones, fuentes de datos, mediciones y evaluaciones en `data/database/el_nino.db`.
- 🗺️ **Visualización Cartográfica Interactiva (Folium/Leaflet):** Generación de mapa de calor de lluvias, marcadores circulares cromáticos según nivel de riesgo, ventanas emergentes (*popups*) con trazabilidad y leyenda cartográfica explicativa en `mapa_riesgo_nino.html`.
- 🧪 **Suite de Pruebas Automatizadas (Pytest):** 36 pruebas unitarias e integrales aprobadas al 100%.

---

## 🏗️ 3. Arquitectura del Software

El sistema implementa el patrón **Modelo - Vista - Controlador (MVC)**:

```text
Sistema-El-Nino/
│
├── main.py                     # Punto de entrada y configuración de logging
├── requirements.txt            # Dependencias del proyecto
├── .gitignore                  # Reglas de exclusión para control de versiones
├── .env.example                # Plantilla de variables de entorno
├── mapa_riesgo_nino.html       # Mapa interactivo generado con Folium
│
├── controllers/
│   ├── __init__.py
│   └── main_controller.py     # Controlador principal (orquestador de 12 opciones)
│
├── models/
│   ├── __init__.py
│   ├── risk_classifier.py     # Matriz de decisión y umbrales inmutables
│   ├── logic_engine.py        # Motor de reglas declarativo en Python
│   ├── prolog_engine.py       # Adaptador de integración formal con SWI-Prolog
│   ├── data_providers.py      # Proveedores de datos (Simulated y OpenMeteo)
│   ├── database.py            # Capa de persistencia SQLite (consultas parametrizadas)
│   ├── data_processor.py      # Pipelines funcionales inmutables y estadísticas
│   └── scraper.py             # Extracción web con BeautifulSoup y georreferenciación
│
├── logic/
│   ├── el_nino_rules.pl       # Base de conocimiento y reglas en sintaxis Prolog
│   └── test_facts.pl          # Hechos de prueba para unificación y backtracking
│
├── views/
│   ├── __init__.py
│   ├── console_view.py        # Interfaz de consola con menú interactivo
│   └── map_view.py            # Generador cartográfico con Folium
│
├── data/
│   ├── regions.json           # Catálogo fijo de 25 departamentos y coordenadas
│   ├── database/              # Almacenamiento de base de datos SQLite (el_nino.db)
│   └── simulations/           # Directorio para exportación de escenarios
│
├── tests/
│   ├── test_risk_classifier.py
│   ├── test_data_processor.py
│   ├── test_data_providers.py
│   ├── test_logic_engine.py
│   ├── test_prolog_engine.py
│   ├── test_database.py
│   ├── test_map_view.py
│   └── test_scraper.py
│
└── docs/
    ├── architecture.md             # Diagramas y responsabilidades de diseño
    ├── programming_paradigms.md    # Sustentación académica (Unidades 1, 2 y 3)
    ├── database_design.md          # Diagrama ER y diccionario de datos
    └── testing.md                  # Reporte y casos de prueba automatizados
```

---

## ⚖️ 4. Matriz de Decisión Hidrometeorológica

Para subsanar deficiencias en clasificaciones intermedias, se estableció una tabla de decisión completa, determinista y exhaustiva compartida por los motores de Python y Prolog:

| Condición Lógica de Precipitación (P) y Temperatura (T) | Nivel de Riesgo | Color Cartográfico |
| :--- | :--- | :---: |
| $P > 120.0 \text{ mm} \land T > 30.0 \text{ °C}$ | 🔴 **Riesgo de Inundacion Extremo** | `#D32F2F` |
| $P > 120.0 \text{ mm} \land T \le 30.0 \text{ °C}$ *(Defecto Corregido)* | 🟠 **Riesgo de Inundacion Alto** | `#F57C00` |
| $80.0 \text{ mm} < P \le 120.0 \text{ mm}$ | 🟠 **Riesgo de Inundacion Alto** | `#F57C00` |
| $40.0 \text{ mm} < P \le 80.0 \text{ mm}$ | 🟡 **Riesgo Moderado** | `#FBC02D` |
| $0.0 \text{ mm} \le P \le 40.0 \text{ mm}$ | 🟢 **Riesgo Normal** | `#388E3C` |
| Valores nulos, negativos o fuera de límites físicos | ⚪ **Dato Invalido** | `#757575` |

---

## 🚀 5. Instalación y Puesta en Marcha

### Requisitos del Sistema
- **Python:** 3.8 a 3.13 instalado.
- **SWI-Prolog (Opcional para inferencia lógica formal):**
  - En Windows: `winget install SWI-Prolog.SWI-Prolog` o desde [swi-prolog.org](https://www.swi-prolog.org/download/stable) (marcar *Add swipl to PATH*).
  - En Linux (Debian/Ubuntu): `sudo apt install swi-prolog`.
  - *Nota:* Si Prolog no está instalado, el sistema ejecuta todas las demás funciones e indica instrucciones claras de instalación sin fallar.

### Paso 1: Clonar o ingresar a la carpeta del proyecto
```bash
cd "c:\ruta\al\proyecto"
```

### Paso 2: Crear y activar entorno virtual
- **En Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **En Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar la aplicación
```bash
python main.py
```
*(O directamente sin activar venv: `.\venv\Scripts\python.exe main.py`)*

### Paso 5: Ejecutar pruebas automatizadas
```bash
pytest -v
```

---

## 🖥️ 6. Menú Interactivo de 12 Opciones

1. **Generar datos simulados:** Selecciona escenarios (*Costa Norte Severa*, *Moderado*, *Normal*) y fija la semilla NumPy.
2. **Obtener datos reales en vivo:** Conecta vía REST con la API de Open-Meteo.
3. **Procesar y limpiar mediciones:** Ejecuta el pipeline inmutable de Pandas (`pipe`, `assign`, `copy`).
4. **Clasificar riesgos mediante motor Python:** Infiere riesgos con `RuleEngine` y persiste en SQLite.
5. **Clasificar riesgos mediante motor Prolog:** Infiere riesgos mediante `SWI-Prolog` y persiste en SQLite.
6. **Comparar resultados de ambos motores:** Muestra auditoría comparativa de concordancia.
7. **Visualizar estadísticas avanzadas:** Agregaciones estadísticas descriptivas con Pandas y NumPy.
8. **Consultar historial:** Lista mediciones históricas persistidas en SQLite.
9. **Generar mapa geoespacial:** Genera `mapa_riesgo_nino.html` con capas de calor y marcadores Folium.
10. **Demostración de Programación Funcional (Unidad 1):** Muestra funciones puras, currying, orden superior y composición.
11. **Demostración de Programación Lógica (Unidad 2):** Ejecuta consultas Prolog interactivas de unificación y backtracking.
12. **Salir:** Finaliza la sesión de forma segura.

---

## 📚 7. Documentación Académica Detallada

Para la sustentación universitaria ante jurado o docente, consultar los manuales específicos en la carpeta `docs/`:
- 📘 [docs/programming_paradigms.md](docs/programming_paradigms.md): Sustentación de Funcional, Lógico y Multiparadigma con fragmentos de código y líneas correspondientes.
- 📐 [docs/architecture.md](docs/architecture.md): Diagramas de componentes e interacción MVC.
- 🗄️ [docs/database_design.md](docs/database_design.md): Diagrama Entidad-Relación (Mermaid) y diccionario de datos SQLite.
- 🧪 [docs/testing.md](docs/testing.md): Plan de pruebas y resultados de ejecución en Pytest (36 pruebas).
