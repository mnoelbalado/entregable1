from typing import List, Dict, Callable
from functools import reduce
from juego.jugadores import mover_jugador


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
# Composicion aplicada
# --------------------------------------------------

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