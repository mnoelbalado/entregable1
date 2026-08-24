"""
Módulo para manejar premios y castigos.
"""
from typing import Dict
from juego.jugadores import (
    mover_jugador,
    retroceder_jugador,
    agregar_turno_perdido
)


# -------------------------
# Premios
# -------------------------

def aplicar_p1(jugador_objetivo: Dict) -> Dict:
    """
    P1: el jugador elegido pierde un turno.

    Función pura.
    """
    return agregar_turno_perdido(jugador_objetivo)


def aplicar_p2(jugador: Dict, nuevo_dado: int) -> Dict:
    """
    P2: el jugador tira nuevamente el dado
    y avanza la cantidad obtenida.

    El dado se recibe como parámetro para
    mantener esta función pura.
    """
    return mover_jugador(jugador, nuevo_dado)


def aplicar_p3(jugador: Dict) -> Dict:
    """
    P3: el jugador avanza dos casillas.

    Función pura.
    """
    return mover_jugador(jugador, 2)


# -------------------------
# Castigos
# -------------------------

def aplicar_c1(jugador: Dict) -> Dict:
    """
    C1: el jugador pierde un turno.

    Función pura.
    """
    return agregar_turno_perdido(jugador)


def aplicar_c2(jugador: Dict) -> Dict:
    """
    C2: el jugador retrocede tres casillas.

    Función pura.
    """
    return retroceder_jugador(jugador, 3)


# -------------------------
# Aplicación general
# -------------------------

def aplicar_efecto(
    jugador: Dict,
    efecto: str,
    dado_p2: int = 0
) -> Dict:
    """
    Aplica el efecto correspondiente a una casilla.

    P1 no se maneja aquí porque afecta a otro jugador
    elegido por quien cayó en la casilla.

    Función pura.
    """

    efectos = {
        "P2": lambda j: aplicar_p2(j, dado_p2),
        "P3": aplicar_p3,
        "C1": aplicar_c1,
        "C2": aplicar_c2
    }

    funcion_efecto = efectos.get(efecto)

    if funcion_efecto:
        return funcion_efecto(jugador)

    return jugador.copy()