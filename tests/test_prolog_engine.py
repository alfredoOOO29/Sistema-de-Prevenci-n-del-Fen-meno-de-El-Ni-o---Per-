"""
Pruebas Unitarias: Adaptador de Integración con SWI-Prolog
Verifica presencia de archivos de reglas, sanitización de átomos y comportamiento ante falta de binario.
"""

import os
import pytest
from models.prolog_engine import PrologEngine
from models.risk_classifier import RiskLevel


def test_archivo_reglas_prolog_existe():
    """El archivo logic/el_nino_rules.pl debe existir físicamente en el repositorio."""
    engine = PrologEngine()
    assert os.path.exists(engine.rules_path), f"Falta el archivo: {engine.rules_path}"
    assert os.path.exists(engine.DEFAULT_FACTS_PATH)


def test_sanitizacion_atomos_prolog():
    """Verifica que cadenas con tildes, mayúsculas y espacios se transformen en átomos Prolog válidos."""
    assert PrologEngine._sanitize_atom("Áncash") == "ancash"
    assert PrologEngine._sanitize_atom("La Libertad") == "la_libertad"
    assert PrologEngine._sanitize_atom("Huánuco") == "huanuco"
    assert PrologEngine._sanitize_atom("San Martín") == "san_martin"


def test_mapeo_atomos_prolog_a_enum():
    """Verifica el mapeo bidireccional entre átomos Prolog y RiskLevel."""
    assert PrologEngine._map_prolog_atom_to_risk("extremo") == RiskLevel.EXTREMO
    assert PrologEngine._map_prolog_atom_to_risk("alto") == RiskLevel.ALTO
    assert PrologEngine._map_prolog_atom_to_risk("moderado") == RiskLevel.MODERADO
    assert PrologEngine._map_prolog_atom_to_risk("normal") == RiskLevel.NORMAL
    assert PrologEngine._map_prolog_atom_to_risk("desconocido") == RiskLevel.INVALIDO


def test_instrucciones_instalacion_claras():
    """Cuando SWI-Prolog no está disponible, las instrucciones deben ser completas y claras."""
    instructions = PrologEngine.get_installation_instructions()
    assert "winget" in instructions
    assert "swi-prolog.org" in instructions
    assert "SWI-PROLOG NO DETECTADO" in instructions
