from models.scraper import ElNinoScraper
from models.data_processor import ElNinoDataProcessor
from views.console_view import ConsoleView
from views.map_view import MapView
import webbrowser

class MainController:
    def __init__(self):
        self.scraper = ElNinoScraper()
        self.processor = ElNinoDataProcessor()
        self.console_view = ConsoleView()
        self.map_view = MapView()
        
        self.raw_data = None
        self.processed_data = None
        self.at_risk_data = None

    def run(self):
        while True:
            opcion = self.console_view.display_menu()
            
            if opcion == '1':
                self.console_view.display_message("Extrayendo datos de repositorios...")
                regions = self.scraper.scrape_regions()
                self.console_view.display_message(f"Regiones extraídas: {len(regions)}")
                self.raw_data = self.scraper.generate_weather_data(regions)
                self.console_view.display_message("Datos meteorológicos base generados.")
                
            elif opcion == '2':
                if self.raw_data is None:
                    self.console_view.display_error("Primero debe extraer los datos (Opción 1).")
                    continue
                    
                self.console_view.display_message("Procesando datos y aplicando motor de inferencia lógica...")
                self.processed_data, self.at_risk_data = self.processor.process_data(self.raw_data)
                self.console_view.display_message("Evaluación de riesgos completada.")
                
            elif opcion == '3':
                if self.processed_data is None:
                    self.console_view.display_error("Primero debe procesar los datos (Opción 2).")
                    continue
                    
                filepath = self.map_view.generate_heat_map(self.processed_data)
                try:
                    webbrowser.open('file://' + filepath)
                except Exception:
                    self.console_view.display_message(f"Abra el archivo manualmente: {filepath}")
                    
            elif opcion == '4':
                if self.at_risk_data is None:
                    self.console_view.display_error("Primero debe procesar los datos (Opción 2).")
                    continue
                    
                self.console_view.display_report(self.at_risk_data)
                
            elif opcion == '5':
                self.console_view.display_message("Saliendo del sistema...")
                break
                
            else:
                self.console_view.display_error("Opción no válida.")
