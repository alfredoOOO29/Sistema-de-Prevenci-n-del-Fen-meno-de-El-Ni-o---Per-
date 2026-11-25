"""
Pruebas Unitarias: Web Scraping de Regiones
"""

import pytest
from models.scraper import ElNinoScraper


@pytest.fixture
def scraper():
    return ElNinoScraper()


def test_scraper_extrae_departamentos(scraper):
    """Verifica que el scraper retorne una lista no vacía de departamentos."""
    regions = scraper.scrape_regions()
    assert isinstance(regions, list)
    assert len(regions) >= 7
    # Debe contener departamentos representativos
    assert any("piura" in r.lower() for r in regions)
    assert any("lima" in r.lower() for r in regions)


def test_scraper_generacion_datos_con_coordenadas_reales(scraper):
    """Verifica que los datos generados posean coordenadas y atributos consistentes."""
    regions = ["Piura", "Tumbes", "Lima"]
    df = scraper.generate_weather_data(regions, seed=42)
    
    assert len(df) == 3
    assert "lat" in df.columns
    assert "lon" in df.columns
    assert "precipitation_mm" in df.columns
    assert "temperature_c" in df.columns

    # Piura debe tener latitud aproximada a -5.19 y longitud -80.63
    piura_row = df[df["region"] == "Piura"].iloc[0]
    assert -6.0 <= piura_row["lat"] <= -4.0
    assert -82.0 <= piura_row["lon"] <= -79.0
