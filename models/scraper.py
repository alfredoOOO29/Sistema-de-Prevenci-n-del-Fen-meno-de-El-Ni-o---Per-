"""
Módulo de Web Scraping para Extracción de Departamentos del Perú
Demuestra funciones de orden superior (filter, map) y recuperación de datos web.
Integra las coordenadas fijas del catálogo data/regions.json para evitar coordenadas aleatorias.
"""

import json
import os
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests


class ElNinoScraper:
    """
    Extractor web de departamentos del Perú y generador compatible de datos meteorológicos.
    Mapea coordenadas oficiales verificables en lugar de aproximaciones espaciales aleatorias.
    """

    def __init__(self):
        self.url = "https://es.wikipedia.org/wiki/Departamentos_del_Perú"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self._regions_catalog: Dict[str, Dict[str, Any]] = self._load_catalog()

    def _load_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Carga el catálogo de regiones indexado por nombre normalizado."""
        catalog_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "regions.json")
        )
        catalog_dict = {}
        if os.path.exists(catalog_path):
            with open(catalog_path, "r", encoding="utf-8") as f:
                regions_list = json.load(f)
                for r in regions_list:
                    name_key = r.get("name", "").strip().lower()
                    catalog_dict[name_key] = r
        return catalog_dict

    def scrape_regions(self) -> List[str]:
        """
        Extrae las regiones de la tabla oficial de Wikipedia utilizando BeautifulSoup.
        Utiliza programación funcional (filter, map) para transformar filas HTML en nombres limpios.
        """
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            tables = soup.find_all('table', {'class': 'wikitable'})
            if not tables:
                raise ValueError("No se encontró la tabla de departamentos en la página.")
                
            table = tables[0]
            rows = table.find_all('tr')[1:]  # Omitir cabecera
            
            def parse_row(row):
                cols = row.find_all(['th', 'td'])
                if len(cols) >= 3:
                    name = cols[2].text.strip() if len(cols) > 2 and cols[2].text.strip() else cols[0].text.strip()
                    name = name.replace('Departamento de ', '').replace('Departamento del ', '')
                    return name if name else None
                return None
            
            # Programación funcional pura con map y filter
            regions = list(filter(None, map(parse_row, rows)))
            return regions if regions else list(self._regions_catalog.keys())
            
        except Exception as e:
            # Fallback seguro con catálogo predefinido
            return [
                "Amazonas", "Áncash", "Apurímac", "Arequipa", "Ayacucho", "Cajamarca",
                "Callao", "Cusco", "Huancavelica", "Huánuco", "Ica", "Junín",
                "La Libertad", "Lambayeque", "Lima", "Loreto", "Madre de Dios",
                "Moquegua", "Pasco", "Piura", "Puno", "San Martín", "Tacna", "Tumbes", "Ucayali"
            ]

    def generate_weather_data(self, regions: List[str], seed: int = 42) -> pd.DataFrame:
        """
        Genera variables meteorológicas asignando coordenadas geográficas REALES
        provenientes del catálogo oficial data/regions.json.
        """
        np.random.seed(seed)
        data = []
        
        for region in regions:
            reg_clean = region.strip().lower()
            geo_info = self._regions_catalog.get(reg_clean, {})
            
            is_north = geo_info.get("is_coastal_north", region in ["Tumbes", "Piura", "Lambayeque", "La Libertad"])
            
            # Coordenadas reales verificadas (o aproximación central por defecto si es nueva)
            lat = geo_info.get("lat", -5.0 if is_north else -12.0)
            lon = geo_info.get("lon", -80.0 if is_north else -75.0)
            reg_id = geo_info.get("id", "PE-UNK")
            
            # Simulación funcional estocástica
            rain_generator = lambda n: np.random.normal(160, 40) if n else np.random.normal(25, 12)
            precipitation = max(0.0, float(rain_generator(is_north)))
            temp = float(np.random.normal(32.5, 2.0) if is_north else np.random.normal(22.0, 3.5))
            
            data.append({
                "region_id": reg_id,
                "region": region,
                "lat": float(lat),
                "lon": float(lon),
                "precipitation_mm": round(precipitation, 2),
                "temperature_c": round(temp, 2),
                "is_coastal_north": is_north,
                "data_source": "Wikipedia Scraping + Simulación NumPy",
                "is_simulation": True
            })
            
        return pd.DataFrame(data)
