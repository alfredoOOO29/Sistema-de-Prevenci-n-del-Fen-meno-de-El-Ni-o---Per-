# 🌊 Sistema de Prevención del Fenómeno de El Niño - Perú
> **Proyecto Multiparadigma** | Paradigmas: Orientado a Objetos (POO), Funcional y Lógico  
> **Curso:** Lenguajes de Programación — Universidad Tecnológica del Perú (UTP)

---

## 📌 1. Información General del Proyecto

Este proyecto es un **sistema de alerta temprana y evaluación de riesgos** frente al impacto meteorológico del **Fenómeno de El Niño** en los departamentos del Perú. 

El sistema recolecta información geográfica de las regiones peruanas mediante *web scraping*, simula y analiza variables hidroclimáticas (precipitaciones en mm y temperatura en °C), y procesa los datos mediante un **motor de inferencia lógica** para clasificar el nivel de vulnerabilidad de cada zona. Finalmente, ofrece reportes en consola y un **mapa de calor geoespacial interactivo** exportado en formato HTML.

### 🎯 Objetivos Principales
- **Extracción automatizada:** Obtener dinámicamente las regiones y departamentos del Perú desde fuentes web públicas.
- **Simulación y modelado de datos:** Generar datos meteorológicos basados en distribuciones normales y patrones históricos (mayor intensidad en la costa norte).
- **Inferencia lógica basada en reglas:** Evaluar hechos y deducir niveles de riesgo de inundación usando un motor de reglas declarativas.
- **Visualización interactiva:** Representar geoespacialmente las zonas afectadas mediante mapas de calor y marcadores cromáticos de severidad con la librería Folium.

---

## 🧩 2. Enfoque Multiparadigma y Arquitectura

El núcleo del proyecto fue diseñado aplicando tres paradigmas fundamentales de la programación y el patrón de diseño **MVC (Modelo - Vista - Controlador)**:

```
                      +-------------------+
                      |      main.py      |
                      +---------+---------+
                                |
                                v
                    +-----------------------+
                    |    MainController     |
                    +---+---------------+---+
                        |               |
          +-------------+               +-------------+
          v                                           v
+-------------------+                       +-------------------+
|      MODELS       |                       |       VIEWS       |
| - scraper.py      |                       | - console_view.py |
| - data_processor  |                       | - map_view.py     |
| - logic_engine    |                       +-------------------+
+-------------------+                                 |
                                                      v
                                            mapa_riesgo_nino.html
```

### 🔹 Paradigma Orientado a Objetos (POO)
- Estructuración modular mediante clases con responsabilidades bien delimitadas:
  - **`MainController`**: Coordina el ciclo de vida de la aplicación, el flujo de opciones y el paso de datos entre modelos y vistas.
  - **`ElNinoScraper`**: Encapsula la lógica de conexión HTTP y extracción web.
  - **`RuleEngine`**: Abstracción del motor de inferencia que gestiona reglas y evalúa hechos.
  - **`ConsoleView` y `MapView`**: Encapsulan la presentación en terminal y la construcción del mapa HTML respectivamente.

### 🔹 Paradigma Funcional
- **Funciones de orden superior:** Empleo extensivo de `map()`, `filter()` y `apply()` para transformar y filtrar colecciones sin bucles imperativos explícitos.
- **Expresiones Lambda:** Funciones anónimas para evaluar condiciones de reglas lógicas, parsear filas de tablas HTML y estructurar coordenadas para Folium:
  - Generación condicional de lluvias: `lambda n: np.random.normal(150, 50) if n else ...`
  - Evaluación vectorizada en DataFrames: `evaluate_risk = lambda row: self.rule_engine.evaluate(row.to_dict())`
  - Transformación funcional de coordenadas para mapas: `list(map(lambda row: [...], df.to_dict('records')))`

### 🔹 Paradigma Lógico
- **Motor de Reglas Declarativas (`RuleEngine`):**
  - Se define una base de conocimiento compuesta por pares `(Condición -> Conclusión)`.
  - Se introduce un conjunto de hechos meteorológicos (`fact`) y el motor evalúa las premisas para inferir la conclusión adecuada según la prioridad de riesgo.
  - **Matriz de Inferencia:**
    | Condición Lógica | Clasificación de Riesgo |
    | :--- | :--- |
    | `Precipitación > 120 mm` **Y** `Temperatura > 30 °C` | 🔴 **Riesgo de Inundación Extremo** |
    | `80 mm < Precipitación <= 120 mm` | 🟠 **Riesgo de Inundación Alto** |
    | `40 mm < Precipitación <= 80 mm` | 🟡 **Riesgo Moderado** |
    | Cualquier otro valor | 🟢 **Riesgo Normal** |

---

## 📂 3. Estructura de Directorios

```text
proyecti lenguajes de programcion/
│
├── controllers/
│   ├── __init__.py
│   └── main_controller.py      # Controlador principal del flujo de la aplicación
│
├── models/
│   ├── __init__.py
│   ├── scraper.py             # Scraping de Wikipedia y generación de datos climáticos
│   ├── logic_engine.py        # Motor de reglas e inferencia lógica
│   └── data_processor.py      # Procesamiento y aplicación de reglas sobre DataFrames
│
├── views/
│   ├── __init__.py
│   ├── console_view.py        # Interfaz de usuario en consola (menú y reportes)
│   └── map_view.py            # Generador de mapa de calor HTML con Folium
│
├── main.py                    # Punto de entrada de la aplicación
├── requirements.txt           # Dependencias del proyecto
├── mapa_riesgo_nino.html      # Mapa interactivo generado (salida visual)
└── README.md                  # Documentación del proyecto
```

---

## ⚙️ 4. Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:
- **Python 3.8 o superior** ([Descargar Python](https://www.python.org/downloads/))
- **Git** (opcional, para clonar el repositorio)
- Conexión a internet (necesaria para el *web scraping* de regiones y la carga de capas cartográficas del mapa).

---

## 🚀 5. Guía de Instalación e Inicio Rápido

Sigue estos pasos en la terminal de tu sistema operativo para configurar el entorno e iniciar el proyecto:

### Paso 1: Clonar o situarse en la carpeta del proyecto
Abre tu terminal o consola (PowerShell, CMD, Bash) y sitúate en el directorio raíz del proyecto:
```bash
cd "c:\ruta\hacia\proyecti lenguajes de programcion"
```

### Paso 2: Crear el entorno virtual (Recomendado)
Crear un entorno virtual aísla las librerías del proyecto de tu instalación global de Python.

- **En Windows (PowerShell o CMD):**
  ```powershell
  python -m venv venv
  ```
- **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  ```

### Paso 3: Activar el entorno virtual

- **En Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  > *Nota para PowerShell:* Si aparece un error de política de ejecución de scripts, ejecuta una vez:  
  > `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` y vuelve a activar.

- **En Windows (Símbolo del sistema / CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```

- **En Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

*(Sabrás que está activado porque aparecerá `(venv)` al inicio de la línea de comandos).*

### Paso 4: Instalar las dependencias
Con el entorno virtual activado, instala todas las librerías necesarias ejecutando:
```bash
pip install -r requirements.txt
```

### Paso 5: Iniciar el sistema
Inicia la aplicación ejecutando el script principal:
```bash
python main.py
```

---

## 🖥️ 6. Guía de Uso del Menú Interactivo

Al iniciar la aplicación, se desplegará el siguiente menú en consola:

```text
==================================================
SISTEMA DE PREVENCIÓN DEL FENÓMENO DEL NIÑO - PERÚ
Enfoque Multiparadigma (Funcional, Lógico, POO)
==================================================
1. Extraer datos (Scraping de Regiones)
2. Procesar datos y aplicar reglas lógicas de riesgo
3. Generar Mapa de Calor (Inundaciones)
4. Mostrar reporte en consola (Tuplas/Diccionarios)
5. Salir
Seleccione una opción:
```

### Flujo de ejecución recomendado:
1. **Opción 1 (`Extraer datos`):**  
   Conecta con Wikipedia para extraer los nombres de los departamentos de Perú y genera de manera reproducible las variables meteorológicas (`latitud`, `longitud`, `precipitacion_mm`, `temperatura_c`).
2. **Opción 2 (`Procesar datos`):**  
   Aplica el motor lógico sobre cada registro para deducir el nivel de riesgo de cada región.
3. **Opción 3 (`Generar Mapa de Calor`):**  
   Crea el archivo `mapa_riesgo_nino.html` con un mapa interactivo (Tiles satelitales/topográficos de Esri, mapa de calor de precipitaciones y marcadores con tooltip descriptivo por departamento). Abre el archivo automáticamente en tu navegador predeterminado.
4. **Opción 4 (`Mostrar reporte en consola`):**  
   Imprime una lista tabular ordenada con las regiones identificadas que presentan riesgo moderado, alto o extremo.
5. **Opción 5 (`Salir`):**  
   Cierra la aplicación de forma segura.

---

## 🛠️ 7. Tecnologías y Librerías Utilizadas

| Librería | Versión típica | Propósito en el proyecto |
| :--- | :--- | :--- |
| **Python** | `>= 3.8` | Lenguaje de desarrollo principal. |
| **[pandas](https://pandas.pydata.org/)** | `>= 2.0` | Estructuración y manipulación tabular de datos (DataFrames). |
| **[numpy](https://numpy.org/)** | `>= 1.24` | Cálculos numéricos y generación de distribuciones normales para variables climáticas. |
| **[requests](https://requests.readthedocs.io/)** | `>= 2.31` | Solicitudes HTTP para consultar portales web. |
| **[beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)** | `>= 4.12` | Parseo y extracción de contenido HTML (Web Scraping). |
| **[folium](https://python-visualization.github.io/folium/)** | `>= 0.14` | Generación de mapas interactivos basados en Leaflet.js y capas Esri. |

---

## 👥 Créditos
- **Curso:** Lenguajes de Programación
- **Universidad:** Universidad Tecnológica del Perú (UTP)
- **Ciclo:** 7mo Ciclo

