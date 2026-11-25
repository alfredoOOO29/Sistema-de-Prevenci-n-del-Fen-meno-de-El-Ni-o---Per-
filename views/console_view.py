"""
Vista de Consola (CLI)
Implementa el menú interactivo de 12 opciones, presentación de reportes estadísticos,
comparaciones entre motores (Python vs Prolog), advertencias y demostraciones académicas.
"""

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd


class ConsoleView:
    """Presentador de la interfaz de usuario en terminal."""

    @staticmethod
    def display_menu() -> str:
        """Despliega el menú principal de 12 opciones y captura la entrada del usuario."""
        print("\n" + "=" * 70)
        print("🌊 SISTEMA DE PREVENCIÓN DEL FENÓMENO DE EL NIÑO EN EL PERÚ")
        print("   Universidad Tecnológica del Perú - Lenguajes de Programación")
        print("   Enfoque Multiparadigma: POO, Funcional y Lógico (Prolog)")
        print("=" * 70)
        print(" 1. Generar datos simulados (Escenarios NumPy)")
        print(" 2. Obtener datos reales en vivo (API pública Open-Meteo)")
        print(" 3. Procesar y limpiar mediciones (Pipeline Funcional con Pandas)")
        print(" 4. Clasificar riesgos mediante motor Python (RuleEngine)")
        print(" 5. Clasificar riesgos mediante motor Prolog (SWI-Prolog formal)")
        print(" 6. Comparar resultados de ambos motores (Python vs Prolog)")
        print(" 7. Visualizar estadísticas avanzadas (Agrupaciones y métricas)")
        print(" 8. Consultar historial de mediciones almacenadas (SQLite)")
        print(" 9. Generar mapa geoespacial interactivo (Folium HTML)")
        print("10. Ejecutar demostración de Programación Funcional (Unidad 1)")
        print("11. Ejecutar demostración de Programación Lógica (Unidad 2)")
        print("12. Salir del sistema")
        print("=" * 70)
        try:
            return input("👉 Seleccione una opción (1-12): ").strip()
        except (KeyboardInterrupt, EOFError):
            return "12"

    @staticmethod
    def display_message(msg: str) -> None:
        """Muestra un mensaje informativo en consola."""
        print(f"\n[INFO] {msg}")

    @staticmethod
    def display_warning(msg: str) -> None:
        """Muestra una advertencia destacada."""
        print(f"\n⚠️  [ADVERTENCIA] {msg}")

    @staticmethod
    def display_error(msg: str) -> None:
        """Muestra un mensaje de error sin provocar caídas de la aplicación."""
        print(f"\n❌ [ERROR] {msg}")

    @staticmethod
    def display_success(msg: str) -> None:
        """Muestra un mensaje de confirmación exitosa."""
        print(f"\n✅ [ÉXITO] {msg}")

    @staticmethod
    def prompt_scenario_selection() -> Tuple[str, int]:
        """Permite al usuario seleccionar el escenario de simulación y la semilla aleatoria."""
        print("\n--- SELECCIÓN DE ESCENARIO DE SIMULACIÓN ---")
        print("1. Fenómeno de El Niño Costero Severo (Lluvias extremas en el norte)")
        print("2. Fenómeno de El Niño Moderado (Anomalías intermedias)")
        print("3. Condiciones Normales (Precipitaciones bajas)")
        opcion = input("Elija escenario [1-3, defecto 1]: ").strip()
        
        escenarios = {
            "1": "costa_norte_severa",
            "2": "nino_moderado",
            "3": "condiciones_normales",
        }
        scenario = escenarios.get(opcion, "costa_norte_severa")
        
        seed_input = input("Semilla aleatoria (entero) [defecto 42]: ").strip()
        try:
            seed = int(seed_input) if seed_input else 42
        except ValueError:
            seed = 42

        return scenario, seed

    @staticmethod
    def display_risk_report(df: pd.DataFrame) -> None:
        """Imprime la tabla formateada de regiones evaluadas."""
        if df.empty:
            print("\nNo existen registros para reportar.")
            return

        print("\n" + "-" * 75)
        print(f"{'REGIÓN':<16} | {'RIESGO EVALUADO':<28} | {'LLUVIA (mm)':<11} | {'TEMP (°C)':<8}")
        print("-" * 75)
        
        for _, row in df.iterrows():
            region = str(row.get("region", "N/A"))[:15]
            risk = str(row.get("risk_level", "Normal"))[:27]
            rain = float(row.get("precipitation_mm", 0.0))
            temp = float(row.get("temperature_c", 0.0))
            print(f"{region:<16} | {risk:<28} | {rain:>11.2f} | {temp:>8.2f}")
            
        print("-" * 75)

    @staticmethod
    def display_comparison(df_python: pd.DataFrame, df_prolog: pd.DataFrame) -> None:
        """Muestra una comparación lado a lado entre los resultados de Python y Prolog."""
        print("\n" + "=" * 80)
        print("📊 COMPARACIÓN DE MOTORES: Python RuleEngine vs SWI-Prolog")
        print("=" * 80)
        print(f"{'REGIÓN':<16} | {'MOTOR PYTHON':<26} | {'SWI-PROLOG':<24} | {'COINCIDENCIA'}")
        print("-" * 80)

        merged = pd.merge(
            df_python[["region", "risk_level"]].rename(columns={"risk_level": "py_risk"}),
            df_prolog[["region", "risk_level"]].rename(columns={"risk_level": "pl_risk"}),
            on="region",
            how="outer"
        )

        coincidencias = 0
        total = len(merged)

        for _, row in merged.iterrows():
            reg = str(row.get("region", "N/A"))[:15]
            py_r = str(row.get("py_risk", "N/A"))[:25]
            pl_r = str(row.get("pl_risk", "N/A"))[:23]
            match = (py_r == pl_r)
            if match:
                coincidencias += 1
            icono = "✅ COINCIDE" if match else "⚠️ DISCREPA"
            print(f"{reg:<16} | {py_r:<26} | {pl_r:<24} | {icono}")

        print("-" * 80)
        porcentaje = (coincidencias / total * 100) if total > 0 else 0
        print(f"Total regiones comparadas: {total} | Coincidencias exactas: {coincidencias} ({porcentaje:.1f}%)")
        print("=" * 80)

    @staticmethod
    def display_statistics(stats: Dict[str, Any]) -> None:
        """Presenta el resumen estadístico calculado con pandas."""
        print("\n" + "=" * 55)
        print("📈 RESUMEN ESTADÍSTICO HIDROMETEOROLÓGICO (PANDAS)")
        print("=" * 55)
        print(f"Total de registros analizados : {stats.get('total_registros', 0)}")
        print(f"Valores nulos detectados      : {stats.get('valores_nulos_detectados', 0)}")
        
        precip = stats.get("precipitacion", {})
        print("\n--- Estadísticas de Precipitación (mm) ---")
        print(f"  • Promedio           : {precip.get('promedio_mm', 0):.2f} mm")
        print(f"  • Mediana            : {precip.get('mediana_mm', 0):.2f} mm")
        print(f"  • Desviación Estándar: {precip.get('desviacion_estandar_mm', 0):.2f} mm")
        print(f"  • Valor Máximo       : {precip.get('maximo_mm', 0):.2f} mm")
        print(f"  • Valor Mínimo       : {precip.get('minimo_mm', 0):.2f} mm")

        temp = stats.get("temperatura", {})
        print("\n--- Estadísticas de Temperatura (°C) ---")
        print(f"  • Promedio           : {temp.get('promedio_c', 0):.2f} °C")
        print(f"  • Valor Máximo       : {temp.get('maximo_c', 0):.2f} °C")
        print(f"  • Valor Mínimo       : {temp.get('minimo_c', 0):.2f} °C")

        dist = stats.get("distribucion_riesgos", {})
        print("\n--- Distribución de Niveles de Riesgo ---")
        for nivel, count in dist.items():
            print(f"  • {nivel:<30}: {count} departamentos")
        print("=" * 55)

    @staticmethod
    def display_history(records: List[Dict[str, Any]]) -> None:
        """Muestra el historial de mediciones persistidas en SQLite."""
        if not records:
            print("\nNo existen registros históricos en la base de datos.")
            return

        print("\n" + "=" * 90)
        print("🗄️  HISTORIAL DE MEDICIONES Y EVALUACIONES PERSISTIDAS (SQLite)")
        print("=" * 90)
        print(f"{'FECHA':<19} | {'REGIÓN':<14} | {'LLUVIA':<8} | {'TEMP':<6} | {'RIESGO':<24} | {'MOTOR'}")
        print("-" * 90)
        for r in records:
            fecha = str(r.get("recorded_at", ""))[:19]
            reg = str(r.get("region", ""))[:13]
            rain = f"{float(r.get('precipitation_mm', 0)):.1f}mm"
            temp = f"{float(r.get('temperature_c', 0)):.1f}°C"
            riesgo = str(r.get("risk_level", "N/A"))[:23]
            motor = str(r.get("engine_used", "N/A"))[:12]
            print(f"{fecha:<19} | {reg:<14} | {rain:>8} | {temp:>6} | {riesgo:<24} | {motor}")
        print("-" * 90)

    @staticmethod
    def display_functional_demo(demo_results: Dict[str, Any]) -> None:
        """Muestra los resultados de la demostración de programación funcional."""
        print("\n" + "=" * 70)
        print("🧩 DEMOSTRACIÓN DE PROGRAMACIÓN FUNCIONAL (UNIDAD 1)")
        print("=" * 70)
        print("1. Inmutabilidad y Funciones Puras:")
        print(f"   • Mediciones procesadas sin modificar colecciones originales.")
        print(f"   • Total crudas: {demo_results.get('total_originales')} | Válidas puras: {demo_results.get('total_validas')}")
        print("\n2. Funciones de Orden Superior (map, filter, reduce):")
        print(f"   • Promedio obtenido con reduce(): {demo_results.get('promedio_lluvia_reducido')} mm")
        print(f"   • Zonas críticas filtradas mediante currying: {demo_results.get('zonas_extremas_detectadas')}")
        print("\n3. Composición de Funciones (f ∘ g ∘ h)(x):")
        print(f"   • Resultado compuesto: '{demo_results.get('ejemplo_composicion')}'")
        print("=" * 70)

    @staticmethod
    def display_logic_demo(demo_results: Dict[str, Any]) -> None:
        """Muestra los resultados de la demostración de programación lógica."""
        print("\n" + "=" * 70)
        print("🧠 DEMOSTRACIÓN DE PROGRAMACIÓN LÓGICA CON PROLOG (UNIDAD 2)")
        print("=" * 70)
        if not demo_results.get("available"):
            print(demo_results.get("message", "SWI-Prolog no está disponible."))
            return
            
        print(f"Versión de Prolog detectada: {demo_results.get('version', 'SWI-Prolog')}\n")
        print("Salida de consultas ejecutadas en SWI-Prolog:")
        print("-" * 50)
        print(demo_results.get("output", "Sin salida."))
        print("-" * 50)
        print("Conceptos demostrados: Unificación, Resolución, Corte (!), Backtracking y Listas.")
        print("=" * 70)



