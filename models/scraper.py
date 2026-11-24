import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

class ElNinoScraper:
    def __init__(self):
        self.url = "https://es.wikipedia.org/wiki/Departamentos_del_Perú"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
    def scrape_regions(self):
        """Scrapes Peruvian regions to simulate government geographical data."""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            tables = soup.find_all('table', {'class': 'wikitable'})
            if not tables:
                raise ValueError("No table found on the page.")
                
            table = tables[0]
            
            rows = table.find_all('tr')[1:] # Skip header
            
            def parse_row(row):
                cols = row.find_all(['th', 'td'])
                if len(cols) >= 3:
                    # En la tabla de Wikipedia, el nombre del departamento se encuentra en la 3ra columna (índice 2)
                    name = cols[2].text.strip() if len(cols) > 2 and cols[2].text.strip() else cols[0].text.strip()
                    name = name.replace('Departamento de ', '').replace('Departamento del ', '')
                    return name if name else None
                return None
            
            regions = list(filter(None, map(parse_row, rows)))
            return regions if regions else ["Piura", "Tumbes", "Lambayeque", "La Libertad", "Lima", "Ica", "Loreto"]
        except Exception as e:
            print(f"Error en scraping: {e}")
            return ["Piura", "Tumbes", "Lambayeque", "La Libertad", "Lima", "Ica", "Loreto"]

    def generate_weather_data(self, regions):
        np.random.seed(42)
        
        data = []
        for region in regions:
            is_north = region in ["Tumbes", "Piura", "Lambayeque", "La Libertad"]
            
            lat = np.random.uniform(-18.0, 0.0) if not is_north else np.random.uniform(-8.0, -3.0)
            lon = np.random.uniform(-81.0, -68.0)
            
            rain_generator = lambda n: np.random.normal(150, 50) if n else np.random.normal(20, 10)
            precipitation = max(0, rain_generator(is_north))
            
            temp = np.random.normal(32, 2) if is_north else np.random.normal(24, 4)
            
            data.append({
                "region": region,
                "lat": lat,
                "lon": lon,
                "precipitation_mm": precipitation,
                "temperature_c": temp
            })
            
        df = pd.DataFrame(data)
        return df
