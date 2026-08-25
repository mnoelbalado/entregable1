"""
Módulo para la gestión del tablero.
"""

from typing import List, Dict, Optional


# Constantes del tablero
POSICION_INICIO = 0
POSICION_FIN = 35


CASILLAS_ESPECIALES = {
    0: "INICIO",
    5: "P1",
    11: "P2",
    16: "C1",
    22: "P3",
    29: "C2",
    35: "FIN"
}


# Configuración lógica del recorrido del tablero
TABLERO_BASE = [
    {
        "posicion": posicion,
        "tipo": (
            "INICIO" if posicion == POSICION_INICIO
            else "FIN" if posicion == POSICION_FIN
            else "PREMIO" if CASILLAS_ESPECIALES.get(posicion) in ["P1", "P2", "P3"]
            else "CASTIGO" if CASILLAS_ESPECIALES.get(posicion) in ["C1", "C2"]
            else "NORMAL"
        ),
        "efecto": (
            CASILLAS_ESPECIALES.get(posicion)
            if CASILLAS_ESPECIALES.get(posicion) in ["P1", "P2", "P3", "C1", "C2"]
            else None
        )
    }
    for posicion in range(POSICION_FIN + 1)
]


# -------------------------
# Funciones puras
# -------------------------

def crear_tablero() -> List[Dict]:
    """
    Crea una nueva copia del tablero.
    Función pura.
    """
    return [casilla.copy() for casilla in TABLERO_BASE]


def obtener_casilla(
    tablero: List[Dict],
    posicion: int
) -> Optional[Dict]:
    """
    Obtiene una casilla a partir de su posición.
    Función pura.
    """
    return next(
        (
            casilla
            for casilla in tablero
            if casilla["posicion"] == posicion
        ),
        None
    )


def esta_en_fin(
    posicion: int,
    max_posicion: int = POSICION_FIN
) -> bool:
    """
    Verifica si el jugador llegó al final.
    Función pura.
    """
    return posicion >= max_posicion


def obtener_efecto_casilla(
    tablero: List[Dict],
    posicion: int
) -> Optional[str]:
    """
    Obtiene el efecto asociado a una casilla.
    Función pura.
    """
    casilla = obtener_casilla(tablero, posicion)

    return casilla["efecto"] if casilla else None
