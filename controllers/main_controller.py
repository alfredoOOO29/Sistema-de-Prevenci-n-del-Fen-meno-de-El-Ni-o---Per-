"""
Controlador Principal de la Aplicación (Arquitectura MVC)
Coordina los modelos (proveedores de datos, motores de reglas, Prolog y SQLite)
con las vistas (consola y mapa interactivo).
"""

import os
import webbrowser
from typing import Optional
import pandas as pd

from models.data_processor import ElNinoDataProcessor
from models.data_providers import OpenMeteoDataProvider, SimulatedDataProvider
from models.database import DatabaseManager
from models.prolog_engine import PrologEngine
from models.scraper import ElNinoScraper
from views.console_view import ConsoleView
from views.map_view import MapView


class MainController:
    """
    Controlador central del Sistema de Prevención del Fenómeno de El Niño.
    Implementa el flujo de control para las 12 opciones requeridas.
    """

    def __init__(self):
        self.console_view = ConsoleView()
        self.map_view = MapView()
        self.processor = ElNinoDataProcessor()
        self.prolog_engine = PrologEngine()
        self.db_manager = DatabaseManager()
        self.scraper = ElNinoScraper()

        # Estado en memoria de la sesión
        self.raw_data: Optional[pd.DataFrame] = None
        self.processed_data: Optional[pd.DataFrame] = None
        self.at_risk_data: Optional[pd.DataFrame] = None
        self.prolog_evaluated_data: Optional[pd.DataFrame] = None
        self.current_source_name: str = "Sin datos cargados"
        self.current_is_simulation: bool = True

    def run(self) -> None:
        """Ciclo principal de ejecución de la aplicación."""
        while True:
            try:
                opcion = self.console_view.display_menu()

                if opcion == "1":
                    self._handle_simulated_data()
                elif opcion == "2":
                    self._handle_real_data()
                elif opcion == "3":
                    self._handle_process_data()
                elif opcion == "4":
                    self._handle_classify_python()
                elif opcion == "5":
                    self._handle_classify_prolog()
                elif opcion == "6":
                    self._handle_compare_engines()
                elif opcion == "7":
                    self._handle_view_statistics()
                elif opcion == "8":
                    self._handle_view_history()
                elif opcion == "9":
                    self._handle_generate_map()
                elif opcion == "10":
                    self._handle_functional_demo()
                elif opcion == "11":
                    self._handle_logic_demo()
                elif opcion == "12":
                    self.console_view.display_message("Finalizando el sistema. ¡Hasta pronto!")
                    break
                else:
                    self.console_view.display_error("Opción no válida. Ingrese un número entre 1 y 12.")

            except Exception as e:
                self.console_view.display_error(f"Ocurrió un error inesperado: {e}")

    # ==========================================================================
    # MANEJADORES DE CADA OPCIÓN
    # ==========================================================================

    def _handle_simulated_data(self) -> None:
        """Opción 1: Generar datos estocásticos con NumPy."""
        scenario, seed = self.console_view.prompt_scenario_selection()
        provider = SimulatedDataProvider(scenario=scenario, random_seed=seed)
        
        self.console_view.display_message(f"Generando escenario '{scenario}' con semilla={seed}...")
        self.raw_data = provider.fetch_data()
        self.processed_data = None
        self.at_risk_data = None
        self.current_source_name = provider.source_name
        self.current_is_simulation = True

        warning = provider.get_warning_message()
        if warning:
            self.console_view.display_warning(warning)
            
        self.console_view.display_success(
            f"Se generaron {len(self.raw_data)} mediciones para todos los departamentos."
        )

    def _handle_real_data(self) -> None:
        """Opción 2: Consultar la API pública Open-Meteo para datos en vivo."""
        self.console_view.display_message("Conectando con la API pública de Open-Meteo...")
        provider = OpenMeteoDataProvider(sample_size=None)  # Todos los departamentos
        
        try:
            self.raw_data = provider.fetch_data()
            self.processed_data = None
            self.at_risk_data = None
            self.current_source_name = provider.source_name
            self.current_is_simulation = False
            self.console_view.display_success(
                f"Datos en vivo obtenidos exitosamente para {len(self.raw_data)} regiones."
            )
        except Exception as e:
            self.console_view.display_error(f"Fallo al conectar con Open-Meteo: {e}")

    def _handle_process_data(self) -> None:
        """Opción 3: Limpiar dataset mediante pipeline funcional."""
        if self.raw_data is None:
            self.console_view.display_error("Primero debe cargar o generar datos (Opción 1 o 2).")
            return

        self.console_view.display_message("Ejecutando pipeline declarativo (limpieza y normalización)...")
        self.processed_data, self.at_risk_data = self.processor.process_data(self.raw_data)
        self.console_view.display_success("Pipeline completado exitosamente.")
        self.console_view.display_risk_report(self.processed_data)

    def _handle_classify_python(self) -> None:
        """Opción 4: Clasificar riesgos usando el RuleEngine de Python."""
        if self.raw_data is None:
            self.console_view.display_error("No hay datos en memoria. Seleccione la Opción 1 o 2.")
            return

        self.console_view.display_message("Evaluando riesgos con el motor de reglas de Python...")
        self.processed_data, self.at_risk_data = self.processor.process_data(self.raw_data)
        
        # Guardar en SQLite
        guardados = self.db_manager.save_evaluation_batch(
            self.processed_data,
            source_name=self.current_source_name,
            is_simulation=self.current_is_simulation,
            engine_used="Python RuleEngine"
        )
        self.console_view.display_success(
            f"Evaluación completada. {guardados} registros persistidos en SQLite."
        )
        self.console_view.display_risk_report(self.at_risk_data)

    def _handle_classify_prolog(self) -> None:
        """Opción 5: Clasificar riesgos utilizando SWI-Prolog formal."""
        if self.raw_data is None:
            self.console_view.display_error("No hay datos en memoria. Seleccione la Opción 1 o 2.")
            return

        if not self.prolog_engine.is_available():
            # Honestidad académica: no fingir que se ejecutó Prolog
            instrucciones = self.prolog_engine.get_installation_instructions()
            self.console_view.display_warning(instrucciones)
            return

        self.console_view.display_message("Invocando SWI-Prolog mediante subproceso controlado...")
        df_prolog, err = self.prolog_engine.evaluate_dataframe(self.raw_data)
        if err or df_prolog is None:
            self.console_view.display_error(f"Fallo en motor Prolog: {err}")
            return

        self.prolog_evaluated_data = df_prolog
        guardados = self.db_manager.save_evaluation_batch(
            df_prolog,
            source_name=self.current_source_name,
            is_simulation=self.current_is_simulation,
            engine_used="SWI-Prolog"
        )
        self.console_view.display_success(
            f"Inferencia lógica en Prolog completada. {guardados} registros persistidos."
        )
        self.console_view.display_risk_report(df_prolog)

    def _handle_compare_engines(self) -> None:
        """Opción 6: Comparación lado a lado de Python vs Prolog con el mismo dataset."""
        if self.raw_data is None:
            self.console_view.display_error("Cargue datos primero (Opción 1 o 2) para comparar.")
            return

        if not self.prolog_engine.is_available():
            self.console_view.display_warning(
                "Para comparar ambos motores, SWI-Prolog debe estar instalado en el sistema.\n" +
                self.prolog_engine.get_installation_instructions()
            )
            return

        self.console_view.display_message("Ejecutando inferencia en ambos motores sobre el mismo dataset...")
        df_py, _ = self.processor.process_data(self.raw_data)
        df_pl, err = self.prolog_engine.evaluate_dataframe(self.raw_data)

        if err or df_pl is None:
            self.console_view.display_error(f"Error al evaluar en Prolog: {err}")
            return

        self.console_view.display_comparison(df_py, df_pl)

    def _handle_view_statistics(self) -> None:
        """Opción 7: Métricas estadísticas calculadas con pandas."""
        target_df = self.processed_data if self.processed_data is not None else self.raw_data
        if target_df is None or target_df.empty:
            self.console_view.display_error("No hay datos cargados para calcular estadísticas.")
            return

        stats = self.processor.calcular_resumen_estadistico(target_df)
        self.console_view.display_statistics(stats)

    def _handle_view_history(self) -> None:
        """Opción 8: Consultar base de datos histórica SQLite."""
        self.console_view.display_message("Consultando mediciones persistidas en SQLite...")
        records = self.db_manager.get_historical_measurements(limit=30)
        self.console_view.display_history(records)

    def _handle_generate_map(self) -> None:
        """Opción 9: Generar mapa interactivo HTML de calor con Folium."""
        if self.processed_data is None:
            if self.raw_data is not None:
                self.console_view.display_message("Procesando datos antes de generar el mapa...")
                self.processed_data, self.at_risk_data = self.processor.process_data(self.raw_data)
            else:
                self.console_view.display_error("Debe cargar datos (Opción 1 o 2) antes de generar el mapa.")
                return

        filepath = self.map_view.generate_heat_map(
            self.processed_data,
            source_title=self.current_source_name,
            is_simulation=self.current_is_simulation
        )
        self.console_view.display_success(f"Mapa generado exitosamente en: {filepath}")
        try:
            webbrowser.open("file://" + filepath)
        except Exception:
            self.console_view.display_message(f"Abra el mapa manualmente en su navegador: {filepath}")

    def _handle_functional_demo(self) -> None:
        """Opción 10: Demostración pedagógica de Programación Funcional (Unidad 1)."""
        self.console_view.display_message("Ejecutando demostración interactiva de Programación Funcional...")
        resultados = self.processor.run_functional_demo()
        self.console_view.display_functional_demo(resultados)

    def _handle_logic_demo(self) -> None:
        """Opción 11: Demostración pedagógica de Programación Lógica (Unidad 2)."""
        self.console_view.display_message("Ejecutando consultas de demostración lógica con Prolog...")
        resultados = self.prolog_engine.run_demonstration_queries()
        self.console_view.display_logic_demo(resultados)
