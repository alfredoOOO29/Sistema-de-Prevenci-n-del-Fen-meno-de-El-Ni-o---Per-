"""
Punto de Entrada del Sistema de Prevención del Fenómeno de El Niño en el Perú
Universidad Tecnológica del Perú (UTP) - Curso: Lenguajes de Programación
Arquitectura: MVC (Modelo - Vista - Controlador)
Paradigmas: Orientado a Objetos, Funcional y Lógico (Prolog)
"""

import logging
import os
import sys

# Asegurar que el directorio raíz del proyecto esté en el sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Configuración de logging centralizado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

from controllers.main_controller import MainController


def main():
    """Inicializa y ejecuta la aplicación principal."""
    app = MainController()
    app.run()


if __name__ == "__main__":
    main()
