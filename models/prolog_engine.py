"""
Adaptador de Integración con SWI-Prolog
Permite interactuar formalmente con el motor lógico de Prolog mediante el ejecutable `swipl`.
Garantiza que no exista fallback silencioso simulado en Python.
"""

import os
import shutil
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

from models.risk_classifier import RiskLevel


class PrologEngine:
    """
    Controlador y adaptador para la ejecución de inferencia en SWI-Prolog.
    Comunica Python con el motor lógico real `swipl` a través de procesos controlados.
    """
    
    DEFAULT_RULES_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "logic", "el_nino_rules.pl")
    )
    DEFAULT_FACTS_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "logic", "test_facts.pl")
    )

    KNOWN_SWIPL_PATHS = [
        r"C:\Program Files\swipl\bin\swipl.exe",
        r"C:\Program Files (x86)\swipl\bin\swipl.exe",
        r"C:\swipl\bin\swipl.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\swipl\bin\swipl.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\swipl\bin\swipl.exe"),
        os.path.expandvars(r"%ProgramFiles%\swipl\bin\swipl.exe"),
    ]

    def __init__(self, rules_path: Optional[str] = None, custom_swipl_path: Optional[str] = None):
        self.rules_path = rules_path or self.DEFAULT_RULES_PATH
        self.custom_swipl_path = custom_swipl_path
        self._swipl_path = self._locate_swipl()

    def _locate_swipl(self) -> Optional[str]:
        """Localiza el ejecutable de SWI-Prolog en el PATH o ubicaciones estándar."""
        if self.custom_swipl_path and os.path.exists(self.custom_swipl_path):
            return self.custom_swipl_path
            
        system_swipl = shutil.which("swipl")
        if system_swipl:
            return system_swipl
            
        for path in self.KNOWN_SWIPL_PATHS:
            if os.path.exists(path):
                return path
                
        return None

    def is_available(self) -> bool:
        """Verifica si el binario de SWI-Prolog está presente y operativo en el sistema."""
        if not self._swipl_path:
            # Reintentar búsqueda por si se instaló recientemente
            self._swipl_path = self._locate_swipl()
            
        if not self._swipl_path:
            return False
            
        try:
            res = subprocess.run(
                [self._swipl_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return res.returncode == 0
        except Exception:
            return False

    def get_swipl_version(self) -> Optional[str]:
        """Retorna la versión de SWI-Prolog si está disponible."""
        if not self.is_available():
            return None
        try:
            res = subprocess.run(
                [self._swipl_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return res.stdout.strip()
        except Exception:
            return None

    @staticmethod
    def get_installation_instructions() -> str:
        """Retorna instrucciones detalladas para instalar SWI-Prolog en Windows / Linux / macOS."""
        return (
            "\n" + "=" * 65 + "\n"
            "⚠️  SWI-PROLOG NO DETECTADO EN EL SISTEMA\n"
            "=" * 65 + "\n"
            "Para ejecutar la inferencia mediante Programación Lógica formal con Prolog,\n"
            "es necesario contar con SWI-Prolog instalado y disponible en la variable PATH.\n\n"
            "Pasos de Instalación según su Sistema Operativo:\n"
            "1. En Windows (mediante Administrador de Paquetes winget):\n"
            "   winget install SWI-Prolog.SWI-Prolog\n\n"
            "2. En Windows (Descarga directa instalador oficial):\n"
            "   Descargar desde: https://www.swi-prolog.org/download/stable\n"
            "   *IMPORTANTE*: Marcar la opción 'Add swipl to system PATH' durante la instalación.\n\n"
            "3. En Linux (Debian / Ubuntu):\n"
            "   sudo apt update && sudo apt install swi-prolog\n\n"
            "4. En macOS (Homebrew):\n"
            "   brew install swi-prolog\n\n"
            "Nota académica: Por rigurosidad técnica, el sistema NO sustituye la inferencia\n"
            "Prolog con condiciones en Python de forma encubierta."
        )

    @staticmethod
    def _sanitize_atom(text: str) -> str:
        """Convierte una cadena a un átomo válido en minúsculas para Prolog."""
        clean = text.lower().strip()
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n',
            ' ': '_', '-': '_', '.': '', ',': ''
        }
        for k, v in replacements.items():
            clean = clean.replace(k, v)
        # Asegurar que inicie con letra minúscula
        if clean and not clean[0].isalpha():
            clean = 'r_' + clean
        return clean or 'desconocido'

    @staticmethod
    def _map_prolog_atom_to_risk(atom: str) -> RiskLevel:
        """Mapea átomos Prolog al Enum de RiskLevel de la aplicación."""
        atom_clean = atom.lower().strip()
        mapping = {
            "extremo": RiskLevel.EXTREMO,
            "alto": RiskLevel.ALTO,
            "moderado": RiskLevel.MODERADO,
            "normal": RiskLevel.NORMAL,
            "invalido": RiskLevel.INVALIDO,
        }
        return mapping.get(atom_clean, RiskLevel.INVALIDO)

    def evaluate_dataframe(self, df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Evalúa un DataFrame de mediciones hidrometeorológicas utilizando SWI-Prolog.
        
        Args:
            df: DataFrame con columnas ['region', 'precipitation_mm', 'temperature_c']
            
        Returns:
            Tuple[Optional[pd.DataFrame], Optional[str]]: (df_evaluado, mensaje_error)
            Si SWI-Prolog no está disponible, retorna (None, instrucciones_instalacion).
        """
        if not self.is_available():
            return None, self.get_installation_instructions()

        if not os.path.exists(self.rules_path):
            return None, f"No se encontró el archivo de reglas Prolog en: {self.rules_path}"

        # Preparar archivo temporal con hechos y script de consulta
        # Normalizar rutas con barras diagonales compatibles con Prolog
        rules_prolog_path = self.rules_path.replace("\\", "/")
        
        prolog_commands = [
            f":- [ '{rules_prolog_path}' ].\n",
            ":- dynamic temp_med/4.\n",
        ]

        # Crear predicados con índice único para preservar el orden original
        records = df.to_dict("records")
        for idx, row in enumerate(records):
            region_atom = self._sanitize_atom(str(row.get("region", "desconocido")))
            try:
                p = float(row.get("precipitation_mm", 0.0))
                t = float(row.get("temperature_c", 0.0))
            except (ValueError, TypeError):
                p, t = -1.0, -99.0
            prolog_commands.append(f"temp_med({idx}, {region_atom}, {p:.2f}, {t:.2f}).\n")

        # Predicado de consulta masiva que imprime: ID;REGION;RIESGO
        query_code = (
            "ejecutar_evaluacion :-\n"
            "    temp_med(Idx, Reg, P, T),\n"
            "    clasificar_riesgo(P, T, Riesgo),\n"
            "    format('~w;~w;~w~n', [Idx, Reg, Riesgo]),\n"
            "    fail.\n"
            "ejecutar_evaluacion :-\n"
            "    halt(0).\n"
        )
        prolog_commands.append(query_code)

        with tempfile.NamedTemporaryFile("w", suffix=".pl", delete=False, encoding="utf-8") as tmp:
            tmp.writelines(prolog_commands)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [self._swipl_path, "-q", "-s", tmp_path, "-g", "ejecutar_evaluacion", "-t", "halt(1)"],
                capture_output=True,
                text=True,
                timeout=15,
                encoding="utf-8"
            )
            
            if result.returncode != 0 and not result.stdout:
                return None, f"Error en ejecución de Prolog: {result.stderr}"

            # Parsear salida
            evaluations: Dict[int, RiskLevel] = {}
            for line in result.stdout.strip().splitlines():
                parts = line.strip().split(";")
                if len(parts) == 3:
                    try:
                        idx = int(parts[0])
                        risk = self._map_prolog_atom_to_risk(parts[2])
                        evaluations[idx] = risk
                    except ValueError:
                        continue

            df_result = df.copy()
            df_result["risk_level"] = [
                evaluations.get(i, RiskLevel.INVALIDO).value for i in range(len(df_result))
            ]
            df_result["engine_used"] = "SWI-Prolog"
            return df_result, None

        except subprocess.TimeoutExpired:
            return None, "Tiempo de espera agotado al consultar SWI-Prolog"
        except Exception as e:
            return None, f"Fallo al invocar el proceso Prolog: {e}"
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    def run_demonstration_queries(self) -> Dict[str, Any]:
        """
        Ejecuta consultas de demostración pedagógica de Programación Lógica (Unidad 2).
        Verifica unificación, resolución, backtracking y manejo de listas.
        """
        if not self.is_available():
            return {
                "available": False,
                "message": self.get_installation_instructions()
            }

        facts_prolog_path = self.DEFAULT_FACTS_PATH.replace("\\", "/")
        demo_script = (
            f":- [ '{facts_prolog_path}' ].\n"
            "demo :-\n"
            "    write('=== CONSULTA 1: Unificacion directa ==='), nl,\n"
            "    clasificar_riesgo(150.0, 32.0, R1), format('P=150, T=32 -> Riesgo: ~w~n', [R1]),\n"
            "    clasificar_riesgo(130.0, 25.0, R2), format('P=130, T=25 -> Riesgo: ~w (Correccion bug)~n', [R2]),\n"
            "    write('=== CONSULTA 2: Backtracking y soluciones multiples ==='), nl,\n"
            "    forall(evaluar_region(Region, extremo), format('Zona en riesgo extremo: ~w~n', [Region])),\n"
            "    write('=== CONSULTA 3: Estructuras de datos (Listas) ==='), nl,\n"
            "    obtener_todas_vulnerables(Lista), format('Lista de vulnerables: ~w~n', [Lista]),\n"
            "    contar_zonas_vulnerables(Total), format('Total zonas en riesgo: ~w~n', [Total]),\n"
            "    halt(0).\n"
        )

        with tempfile.NamedTemporaryFile("w", suffix=".pl", delete=False, encoding="utf-8") as tmp:
            tmp.write(demo_script)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [self._swipl_path, "-q", "-s", tmp_path, "-g", "demo", "-t", "halt(1)"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8"
            )
            return {
                "available": True,
                "output": result.stdout,
                "version": self.get_swipl_version()
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
