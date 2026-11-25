"""
Pruebas Unitarias: Proveedores de Datos (POO y Abstracción)
Verifica catálogo de coordenadas fijas, escenarios de simulación y reproducibilidad de semillas.
"""

import pytest
from models.data_providers import (
    DataProvider,
    OpenMeteoDataProvider,
    SimulatedDataProvider,
    load_regions_catalog,
)


def test_catalogo_regiones_oficiales():
    """El catálogo debe contener las 25 jurisdicciones (24 departamentos + Callao)."""
    catalog = load_regions_catalog()
    assert len(catalog) == 25
    
    nombres = [r["name"] for r in catalog]
    assert "Piura" in nombres
    assert "Tumbes" in nombres
    assert "Callao" in nombres
    assert "Lima" in nombres
    
    # Coordenadas geográficas dentro de los límites del Perú [-18.5, 0] lat y [-81.5, -68.5] lon
    for r in catalog:
        assert -19.0 <= r["lat"] <= 1.0, f"Latitud fuera de rango para {r['name']}"
        assert -82.0 <= r["lon"] <= -68.0, f"Longitud fuera de rango para {r['name']}"


def test_simulador_reproducibilidad_con_semilla():
    """La misma semilla debe producir exactamente los mismos datos numéricos."""
    provider_1 = SimulatedDataProvider(scenario="costa_norte_severa", random_seed=42)
    provider_2 = SimulatedDataProvider(scenario="costa_norte_severa", random_seed=42)

    df_1 = provider_1.fetch_data()
    df_2 = provider_2.fetch_data()

    assert len(df_1) == 25
    assert len(df_2) == 25
    assert df_1["precipitation_mm"].tolist() == df_2["precipitation_mm"].tolist()
    assert df_1["temperature_c"].tolist() == df_2["temperature_c"].tolist()


def test_simulador_advertencia_clara():
    """El proveedor simulado debe retornar obligatoriamente una advertencia de simulación."""
    provider = SimulatedDataProvider(scenario="costa_norte_severa")
    assert provider.is_simulation is True
    warning = provider.get_warning_message()
    assert warning is not None
    assert "ADVERTENCIA" in warning
    assert "SENAMHI" in warning


def test_polimorfismo_data_provider():
    """Ambos proveedores deben heredar de la clase base abstracta DataProvider."""
    sim = SimulatedDataProvider()
    real = OpenMeteoDataProvider(sample_size=3)

    assert isinstance(sim, DataProvider)
    assert isinstance(real, DataProvider)
    assert sim.is_simulation is True
    assert real.is_simulation is False
