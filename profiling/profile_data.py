"""Perfilado de datos.

La función definida en este archivo constituye uno de los puntos de
trabajo de la práctica.
"""

from pathlib import Path


def generate_profile(input_path: str, output_path: str) -> None:
    """Genera un reporte de perfilado a partir de un archivo CSV.

    La implementación queda a cargo del estudiante.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    raise NotImplementedError(
        "Completar la implementación de generate_profile()."
    )
