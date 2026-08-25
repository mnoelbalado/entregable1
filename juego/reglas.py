from typing import List, Dict

from juego.jugadores import retroceder_jugador


def actualizar_jugador(
    jugadores: List[Dict],
    jugador_actualizado: Dict
) -> List[Dict]:
    """
    Reemplaza un jugador dentro de la lista por su
    versión actualizada. Identificamos al jugador por su color.

    Utiliza map.
    Función pura.
    """
    return list(
        map(
            lambda jugador:
                jugador_actualizado
                if jugador["color"] == jugador_actualizado["color"]
                else jugador,
            jugadores
        )
    )


def obtener_jugadores_en_posicion(
    jugadores: List[Dict],
    posicion: int,
    jugador_actual: Dict
) -> List[Dict]:
    """
    Obtiene los demás jugadores que se encuentran
    en una determinada posición.

    Utiliza filter.
    Función pura.
    """
    return list(
        filter(
            lambda jugador:
                jugador["posicion"] == posicion
                and jugador["color"] != jugador_actual["color"],
            jugadores
        )
    )


def verificar_competencia(
    jugadores: List[Dict],
    jugador_actual: Dict
) -> bool:
    """
    Indica si el jugador actual comparte la casilla
    con otro jugador.

    Función pura.
    """
    jugadores_en_posicion = obtener_jugadores_en_posicion(
        jugadores,
        jugador_actual["posicion"],
        jugador_actual
    )

    return len(jugadores_en_posicion) > 0


def obtener_rival(
    jugadores: List[Dict],
    jugador_actual: Dict
) -> Dict | None:
    """
    Obtiene el jugador contra el cual debe competir
    el jugador actual.

    Función pura.
    """
    jugadores_en_posicion = obtener_jugadores_en_posicion(
        jugadores,
        jugador_actual["posicion"],
        jugador_actual
    )

    if not jugadores_en_posicion:
        return None

    return jugadores_en_posicion[0]


def resolver_competencia(
    jugadores: List[Dict],
    jugador1: Dict,
    jugador2: Dict,
    dado1: int,
    dado2: int
) -> List[Dict]:
    """
    Resuelve una competencia utilizando los valores
    de los dados recibidos como parámetros.

    Si hay empate, no modifica a los jugadores.
    El motor del juego deberá solicitar una nueva tirada.

    Función pura.
    """

    if dado1 == dado2:
        return [jugador.copy() for jugador in jugadores]

    if dado1 > dado2:
        perdedor = jugador2
    else:
        perdedor = jugador1

    perdedor_actualizado = retroceder_jugador(
        perdedor,
        2
    )

    jugadores_actualizados = actualizar_jugador(
        jugadores,
        perdedor_actualizado
    )

    return verificar_retroceso_adicional(
        jugadores_actualizados,
        perdedor_actualizado
    )


def verificar_retroceso_adicional(
    jugadores: List[Dict],
    perdedor: Dict
) -> List[Dict]:
    """
    Comprueba si, después de retroceder dos casillas,
    el perdedor cayó en una posición ocupada.

    En ese caso retrocede exactamente una casilla más,
    según la regla del juego.

    Función pura.
    """
    ocupantes = list(
        filter(
            lambda jugador:
                jugador["posicion"] == perdedor["posicion"]
                and jugador["color"] != perdedor["color"],
            jugadores
        )
    )

    if not ocupantes:
        return jugadores

    perdedor_actualizado = retroceder_jugador(
        perdedor,
        1
    )

    return actualizar_jugador(
        jugadores,
        perdedor_actualizado
    )