"""
Proveedores de Datos Meteorológicos (POO: Abstracción, Herencia y Polimorfismo)
Define la interfaz base DataProvider y sus implementaciones:
- SimulatedDataProvider: Simulación controlada con NumPy y escenarios.
- OpenMeteoDataProvider: Datos meteorológicos reales en tiempo real vía API pública de Open-Meteo.
"""

from abc import ABC, abstractmethod
import json
import logging
import os
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd
import requests

logger = logging.getLogger(__name__)


def load_regions_catalog() -> List[Dict[str, Any]]:
    """Carga el catálogo oficial de regiones y coordenadas fijas desde data/regions.json."""
    catalog_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "regions.json")
    )
    if os.path.exists(catalog_path):
        with open(catalog_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


class DataProvider(ABC):
    """
    Clase abstracta base que define el contrato para los proveedores de datos meteorológicos.
    Demuestra los principios de Abstracción y Polimorfismo en POO.
    """
    
    def __init__(self, source_name: str, is_simulation: bool):
        self._source_name = source_name
        self._is_simulation = is_simulation

    @property
    def source_name(self) -> str:
        """Nombre descriptivo de la fuente de datos."""
        return self._source_name

    @property
    def is_simulation(self) -> bool:
        """Indica si la fuente es una simulación sintética o una medición real."""
        return self._is_simulation

    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        """
        Obtiene los datos meteorológicos en un DataFrame estructurado con las columnas:
        ['region_id', 'region', 'lat', 'lon', 'precipitation_mm', 'temperature_c', 'is_coastal_north', 'data_source', 'is_simulation']
        """
        pass

    def get_warning_message(self) -> Optional[str]:
        """Retorna una advertencia clara cuando se emplean datos simulados."""
        if self._is_simulation:
            return (
                "⚠️ [ADVERTENCIA ACADÉMICA]: Los datos meteorológicos fueron generados "
                "mediante simulación estocástica (NumPy) con propósitos educativos y de modelado. "
                "NO constituyen pronósticos meteorológicos oficiales del SENAMHI."
            )
        return None


class SimulatedDataProvider(DataProvider):
    """
    Proveedor de datos meteorológicos simulados mediante distribuciones estadísticas de NumPy.
    Permite configurar semillas aleatorias, tamaño de muestra y escenarios de severidad.
    """

    SCENARIOS = {
        "costa_norte_severa": "Fenómeno de El Niño Costero Severo (lluvias torrenciales en el norte)",
        "nino_moderado": "Fenómeno de El Niño Moderado (anomalías medias)",
        "condiciones_normales": "Condiciones climáticas neutras (precipitaciones bajas)",
    }

    def __init__(
        self,
        scenario: str = "costa_norte_severa",
        random_seed: int = 42,
        sample_size: Optional[int] = None
    ):
        super().__init__(
            source_name=f"Simulación Estocástica NumPy (Escenario: {scenario})",
            is_simulation=True
        )
        self.scenario = scenario if scenario in self.SCENARIOS else "costa_norte_severa"
        self.random_seed = random_seed
        self.sample_size = sample_size
        self._regions_catalog = load_regions_catalog()

    def fetch_data(self) -> pd.DataFrame:
        """Genera el DataFrame sintético aplicando distribuciones normales según el escenario."""
        np.random.seed(self.random_seed)
        
        regions = list(self._regions_catalog)
        if self.sample_size and 0 < self.sample_size < len(regions):
            indices = np.random.choice(len(regions), size=self.sample_size, replace=False)
            regions = [regions[i] for i in indices]

        rows = []
        for reg in regions:
            is_north = reg.get("is_coastal_north", False)
            
            # Parametrización según escenario
            if self.scenario == "costa_norte_severa":
                # Norte: lluvias torrenciales extremas (>120mm) y alta temperatura (>30°C)
                if is_north:
                    rain = max(0.0, float(np.random.normal(160.0, 35.0)))
                    temp = float(np.random.normal(32.5, 1.8))
                else:
                    rain = max(0.0, float(np.random.normal(25.0, 15.0)))
                    temp = float(np.random.normal(22.0, 4.0))

            elif self.scenario == "nino_moderado":
                if is_north:
                    rain = max(0.0, float(np.random.normal(85.0, 20.0)))
                    temp = float(np.random.normal(28.0, 2.0))
                else:
                    rain = max(0.0, float(np.random.normal(30.0, 12.0)))
                    temp = float(np.random.normal(20.0, 3.5))

            else:  # condiciones_normales
                rain = max(0.0, float(np.random.normal(15.0, 10.0)))
                temp = float(np.random.normal(21.0, 3.0))

            rows.append({
                "region_id": reg.get("id", "PE-UNK"),
                "region": reg.get("name", "Desconocido"),
                "lat": float(reg.get("lat", 0.0)),
                "lon": float(reg.get("lon", 0.0)),
                "precipitation_mm": round(rain, 2),
                "temperature_c": round(temp, 2),
                "is_coastal_north": is_north,
                "data_source": self.source_name,
                "is_simulation": True
            })

        return pd.DataFrame(rows)


class OpenMeteoDataProvider(DataProvider):
    """
    Proveedor de datos meteorológicos reales vía la API pública y gratuita Open-Meteo.
    Consulta en tiempo real mediciones de precipitación y temperatura para las coordenadas oficiales.
    """

    BASE_URL = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast")
    TIMEOUT = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))

    def __init__(self, sample_size: Optional[int] = 10):
        super().__init__(
            source_name="Open-Meteo Weather API (Mediciones Reales en Vivo)",
            is_simulation=False
        )
        self.sample_size = sample_size
        self._regions_catalog = load_regions_catalog()

    def fetch_data(self) -> pd.DataFrame:
        """
        Consulta las coordenadas reales de cada región en la API de Open-Meteo.
        Si la red falla para alguna región, se registra advertencia sin interrumpir el lote completo.
        """
        regions = list(self._regions_catalog)
        if self.sample_size and 0 < self.sample_size < len(regions):
            regions = regions[:self.sample_size]

        rows = []
        for reg in regions:
            lat = reg.get("lat", 0.0)
            lon = reg.get("lon", 0.0)
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,precipitation",
                "timezone": "auto"
            }
            try:
                resp = requests.get(self.BASE_URL, params=params, timeout=self.TIMEOUT)
                resp.raise_for_status()
                data = resp.json()
                current = data.get("current", {})
                
                temp = float(current.get("temperature_2m", 20.0))
                rain = float(current.get("precipitation", 0.0))
                
            except Exception as e:
                logger.warning(f"No se pudo consultar Open-Meteo para {reg.get('name')}: {e}")
                # En caso de fallo de red puntual por región, valor neutro
                temp = 20.0
                rain = 0.0

            rows.append({
                "region_id": reg.get("id", "PE-UNK"),
                "region": reg.get("name", "Desconocido"),
                "lat": float(lat),
                "lon": float(lon),
                "precipitation_mm": round(rain, 2),
                "temperature_c": round(temp, 2),
                "is_coastal_north": reg.get("is_coastal_north", False),
                "data_source": self.source_name,
                "is_simulation": False
            })

        return pd.DataFrame(rows)
