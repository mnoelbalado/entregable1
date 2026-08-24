"""
Módulo con utilidades funcionales.
"""

from typing import List, Dict, Any, Callable
from functools import reduce
from juego.jugadores import *


# --------------------------------------------------
# Composición de funciones
# --------------------------------------------------

def componer(f: Callable, g: Callable) -> Callable:
    """
    Compone dos funciones.
    Devuelve una nueva función equivalente a:
    f(g(x))
    """
    return lambda x: f(g(x))


# --------------------------------------------------
# Generador
# --------------------------------------------------

def generador_turnos(jugadores: List[Dict]) -> Any:
    """
    Generador que produce jugadores de forma cíclica
    mientras no hayan ganado.
    """

    while True:
        for jugador in jugadores:
            if not jugador["ganador"]:
                yield jugador


# --------------------------------------------------
# Map
# --------------------------------------------------

def mapear_estado_jugadores(
    jugadores: List[Dict]
) -> List[str]:
    """
    Transforma el estado de los jugadores en
    descripciones de texto utilizando map.
    """

    return list(
        map(
            lambda jugador:
                f"{jugador['nombre']} "
                f"({jugador['color']}) "
                f"en posición {jugador['posicion']}",
            jugadores
        )
    )


# --------------------------------------------------
# Filter
# --------------------------------------------------

def filtrar_jugadores_activos(
    jugadores: List[Dict]
) -> List[Dict]:
    """
    Obtiene los jugadores que todavía no ganaron
    utilizando filter.
    """

    return list(
        filter(
            lambda jugador: not jugador["ganador"],
            jugadores
        )
    )


# --------------------------------------------------
# Reduce
# --------------------------------------------------

def reducir_estado_juego(
    jugadores: List[Dict]
) -> Dict:
    """
    Genera un resumen del estado de la partida
    utilizando reduce.
    """

    return reduce(
        lambda acumulador, jugador: {
            "total":
                acumulador["total"] + 1,

            "activos":
                acumulador["activos"]
                + (0 if jugador["ganador"] else 1),

            "ganadores":
                acumulador["ganadores"]
                + (1 if jugador["ganador"] else 0)
        },
        jugadores,
        {
            "total": 0,
            "activos": 0,
            "ganadores": 0
        }
    )


# --------------------------------------------------
# Generador de eventos
# --------------------------------------------------

def generador_eventos_juego(
    jugadores: List[Dict]
) -> Any:
    """
    Genera descripciones de eventos correspondientes
    a jugadores que todavía no ganaron.
    """

    for jugador in jugadores:
        if not jugador["ganador"]:
            yield (
                f"Turno de {jugador['nombre']} "
                f"en posición {jugador['posicion']}"
            )

def obtener_posicion(jugador: Dict) -> int:
    """
    Devuelve la posición de un jugador.
    Función pura.
    """
    return jugador["posicion"]


def crear_movimiento_compuesto(pasos: int) -> Callable:
    """
    Compone mover_jugador con obtener_posicion.

    Primero mueve al jugador y luego obtiene
    la posición resultante.
    """

    return componer(
        obtener_posicion,
        lambda jugador: mover_jugador(jugador, pasos)
    )