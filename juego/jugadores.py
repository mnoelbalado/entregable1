"""
Módulo para la gestión de jugadores.
"""

from typing import List, Dict, Tuple
import random

from juego.tablero import POSICION_FIN


# -------------------------
# Funciones puras
# -------------------------

def crear_jugador(nombre: str, color: str, posicion: int = 0) -> Dict:
    """
    Crea un nuevo jugador.
    Función pura.
    """
    return {
        "nombre": nombre,
        "color": color,
        "posicion": posicion,
        "turnos_perdidos": 0,
        "ganador": False
    }


def mover_jugador(
    jugador: Dict,
    pasos: int,
    max_posicion: int = POSICION_FIN
) -> Dict:
    """
    Devuelve un nuevo jugador con su posición actualizada.
    Si llega o supera FIN, queda en FIN y se marca como ganador.
    Función pura.
    """

    if jugador["ganador"]:
        return jugador.copy()

    nueva_posicion = min(
        jugador["posicion"] + pasos,
        max_posicion
    )

    return {
        **jugador,
        "posicion": nueva_posicion,
        "ganador": nueva_posicion >= max_posicion
    }


def retroceder_jugador(jugador: Dict, pasos: int) -> Dict:
    """
    Devuelve un nuevo jugador retrocediendo la cantidad
    indicada de casillas, sin pasar de INICIO.
    Función pura.
    """

    nueva_posicion = max(
        jugador["posicion"] - pasos,
        0
    )

    return {
        **jugador,
        "posicion": nueva_posicion
    }


def agregar_turno_perdido(jugador: Dict) -> Dict:
    """
    Agrega un turno perdido al jugador.
    Función pura.
    """

    return {
        **jugador,
        "turnos_perdidos": jugador["turnos_perdidos"] + 1
    }


def consumir_turno_perdido(jugador: Dict) -> Dict:
    """
    Consume uno de los turnos perdidos del jugador.
    Función pura.
    """

    return {
        **jugador,
        "turnos_perdidos": max(
            jugador["turnos_perdidos"] - 1,
            0
        )
    }


def debe_perder_turno(jugador: Dict) -> bool:
    """
    Indica si el jugador debe perder su próximo turno.
    Función pura.
    """

    return jugador["turnos_perdidos"] > 0


# -------------------------
# Funciones no puras
# -------------------------

def tirar_dado() -> int:
    """
    Simula el lanzamiento de un dado.
    No es una función pura porque utiliza aleatoriedad.
    """

    return random.randint(1, 6)


# -------------------------
# Comprensiones
# -------------------------


# def obtener_jugadores_activos(
#     jugadores: List[Dict]
# ) -> List[Dict]:
#     """
#     Obtiene jugadores que todavía no ganaron
#     usando comprensión de listas.
#     Función pura.
#     """

#     return [
#         jugador
#         for jugador in jugadores
#         if not jugador["ganador"]
#     ]


# def obtener_posiciones_jugadores(
#     jugadores: List[Dict]
# ) -> Dict[int, List[str]]:
#     """
#     Devuelve las posiciones ocupadas y los nombres
#     de los jugadores en cada una.
#     Función pura.
#     """

#     posiciones = {
#         jugador["posicion"]
#         for jugador in jugadores
#     }

#     return {
#         posicion: [
#             jugador["nombre"]
#             for jugador in jugadores
#             if jugador["posicion"] == posicion
#         ]
#         for posicion in posiciones
#     }

# Ctrl + K, luego Ctrl + C
# Para quitar los comentarios: Ctrl + K, luego Ctrl + U