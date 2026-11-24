import pandas as pd

class ConsoleView:
    @staticmethod
    def display_menu():
        print("\n" + "="*50)
        print("SISTEMA DE PREVENCIÓN DEL FENÓMENO DEL NIÑO - PERÚ")
        print("Enfoque Multiparadigma (Funcional, Lógico, POO)")
        print("="*50)
        print("1. Extraer datos (Scraping de Regiones)")
        print("2. Procesar datos y aplicar reglas lógicas de riesgo")
        print("3. Generar Mapa de Calor (Inundaciones)")
        print("4. Mostrar reporte en consola (Tuplas/Diccionarios)")
        print("5. Salir")
        return input("Seleccione una opción: ")

    @staticmethod
    def display_message(msg):
        print(f"\n[INFO] {msg}")
        
    @staticmethod
    def display_error(msg):
        print(f"\n[ERROR] {msg}")

    @staticmethod
    def display_report(at_risk_df):
        print("\n--- REPORTE DE ZONAS EN RIESGO ---")
        if at_risk_df.empty:
            print("No se encontraron zonas en riesgo.")
            return
            
        records = at_risk_df.to_dict('records')
        
        for i, rec in enumerate(records):
            region, risk, rain = rec['region'], rec['risk_level'], rec['precipitation_mm']
            print(f"{i+1}. Región: {region} | Riesgo: {risk} | Lluvia: {rain:.2f} mm")
        
        print("-" * 34)
