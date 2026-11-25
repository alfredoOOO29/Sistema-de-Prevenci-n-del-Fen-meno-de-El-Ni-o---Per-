"""
Pruebas Unitarias: Generación de Mapa Interactivo con Folium
"""

import os
import tempfile
import pandas as pd
import pytest
from views.map_view import MapView


def test_generacion_archivo_mapa_html():
    """Verifica que el mapa interactivo se genere en disco como un HTML válido con capas Folium."""
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        html_path = tmp.name

    try:
        df_test = pd.DataFrame([
            {"region": "Piura", "lat": -5.19, "lon": -80.63, "precipitation_mm": 160.0, "temperature_c": 32.0, "risk_level": "Riesgo de Inundacion Extremo"},
            {"region": "Lima", "lat": -12.04, "lon": -77.04, "precipitation_mm": 12.0, "temperature_c": 21.0, "risk_level": "Riesgo Normal"},
        ])

        map_view = MapView(output_file=html_path)
        output = map_view.generate_heat_map(df_test, source_title="Test Unitario", is_simulation=True)

        assert os.path.exists(output)
        assert os.path.getsize(output) > 1000  # Archivo HTML con scripts de Folium / Leaflet

        with open(output, "r", encoding="utf-8") as f:
            content = f.read()
            assert "leaflet" in content.lower()
            assert "Piura" in content
            assert "Lima" in content
            assert "SIMULACIÓN ACADÉMICA" in content

    finally:
        if os.path.exists(html_path):
            os.remove(html_path)
