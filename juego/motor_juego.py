from typing import List, Dict, Optional, Generator
from juego.jugadores import (tirar_dado, mover_jugador, consumir_turno_perdido, debe_perder_turno)
from juego.tablero import (obtener_efecto_casilla, esta_en_fin)
from juego.premios_castigos import (aplicar_efecto, aplicar_p1)
from juego.reglas import (actualizar_jugador, verificar_competencia, obtener_rival, resolver_competencia)
from juego.logger import registrar_log


# --------------------------------------------------
# Generador de turnos
# --------------------------------------------------

def generar_turnos(
    jugadores: List[Dict]
) -> Generator[int, None, None]:
    """
    Genera indefinidamente los índices de los jugadores.
    Utiliza yield.
    """
    indice = 0

    while True:
        yield indice
        indice = (indice + 1) % len(jugadores)


# --------------------------------------------------
# Búsqueda de jugadores
# --------------------------------------------------

def obtener_jugador_por_color(
    jugadores: List[Dict],
    color: str
) -> Optional[Dict]:
    """
    Busca un jugador según su color.
    Función pura.
    """
    return next(
        (
            jugador
            for jugador in jugadores
            if jugador["color"] == color
        ),
        None
    )


# --------------------------------------------------
# Premio P1
# --------------------------------------------------

def resolver_p1(
    jugadores: List[Dict],
    color_objetivo: str
) -> List[Dict]:
    """
    Aplica P1 al jugador del color seleccionado.
    Función pura.
    """
    jugador_objetivo = obtener_jugador_por_color(
        jugadores,
        color_objetivo
    )

    if jugador_objetivo is None:
        return jugadores.copy()

    jugador_actualizado = aplicar_p1(
        jugador_objetivo
    )

    return actualizar_jugador(
        jugadores,
        jugador_actualizado
    )


# --------------------------------------------------
# Competencia
# --------------------------------------------------

@registrar_log
def competir_recursivamente(
    jugadores: List[Dict],
    jugador1: Dict,
    jugador2: Dict
) -> List[Dict]:
    """
    Realiza una competencia entre dos jugadores.

    Si ambos obtienen el mismo valor,
    vuelve a ejecutar la función recursivamente.
    """

    dado1 = tirar_dado()
    dado2 = tirar_dado()

    print(
        f"Competencia: "
        f"{jugador1['nombre']} sacó {dado1} - "
        f"{jugador2['nombre']} sacó {dado2}"
    )

    if dado1 == dado2:
        print("Empate. Se vuelve a tirar.")

        return competir_recursivamente(
            jugadores,
            jugador1,
            jugador2
        )

    return resolver_competencia(
        jugadores,
        jugador1,
        jugador2,
        dado1,
        dado2
    )


def procesar_competencia(
    jugadores: List[Dict],
    jugador_actual: Dict
) -> List[Dict]:
    """
    Comprueba si el jugador actual comparte
    posición con otro jugador.
    """

    if not verificar_competencia(
        jugadores,
        jugador_actual
    ):
        return jugadores

    rival = obtener_rival(
        jugadores,
        jugador_actual
    )

    if rival is None:
        return jugadores

    return competir_recursivamente(
        jugadores,
        jugador_actual,
        rival
    )


# --------------------------------------------------
# Premios y castigos
# --------------------------------------------------
# Aca usamos recursividad para procesar efectos encadenados, cae en casilla -> aplica efecto -> lo movio? -> sigue procesando.

def procesar_efecto(
    jugadores: List[Dict],
    tablero: List[Dict],
    jugador: Dict,
    color_objetivo_p1: Optional[str] = None
) -> Dict:
    """
    Comprueba si el jugador cayó en una casilla especial,
    aplica su efecto y procesa posibles efectos encadenados.

    Devuelve el estado actualizado y metadatos necesarios
    para informar lo ocurrido durante el turno.
    """

    efecto = obtener_efecto_casilla(
        tablero,
        jugador["posicion"]
    )

    if efecto is None:
        return {
            "jugadores": jugadores,
            "jugador": jugador,
            "efecto": None,
            "dado_extra": None,
            "efectos_encadenados": []
        }

    # P1 afecta a otro jugador y no mueve al jugador actual.
    if efecto == "P1":

        jugadores_actualizados = jugadores

        if color_objetivo_p1 is not None:
            jugadores_actualizados = resolver_p1(
                jugadores,
                color_objetivo_p1
            )

        jugador_final = obtener_jugador_por_color(
            jugadores_actualizados,
            jugador["color"]
        )

        return {
            "jugadores": jugadores_actualizados,
            "jugador": jugador_final,
            "efecto": efecto,
            "dado_extra": None,
            "efectos_encadenados": []
        }

    dado_extra = None

    if efecto == "P2":
        dado_extra = tirar_dado()

        jugador_actualizado = aplicar_efecto(
            jugador,
            efecto,
            dado_extra
        )

    else:
        jugador_actualizado = aplicar_efecto(
            jugador,
            efecto
        )

    jugadores_actualizados = actualizar_jugador(
        jugadores,
        jugador_actualizado
    )

    # Si llegó a FIN debido al efecto,
    # el turno termina inmediatamente.
    if esta_en_fin(
        jugador_actualizado["posicion"]
    ):
        return {
            "jugadores": jugadores_actualizados,
            "jugador": jugador_actualizado,
            "efecto": efecto,
            "dado_extra": dado_extra,
            "efectos_encadenados": []
        }

    # Si el efecto no movió al jugador, no corresponde
    # comprobar nuevamente la misma casilla.
    # Esto evita reprocesar P1 o C1 indefinidamente.
    if (
        jugador_actualizado["posicion"]
        == jugador["posicion"]
    ):
        return {
            "jugadores": jugadores_actualizados,
            "jugador": jugador_actualizado,
            "efecto": efecto,
            "dado_extra": dado_extra,
            "efectos_encadenados": []
        }

    # Como el efecto movio al jugador, se verifica
    # recursivamente la nueva casilla.
    resultado_encadenado = procesar_efecto(
        jugadores_actualizados,
        tablero,
        jugador_actualizado,
        color_objetivo_p1
    )

    efectos_encadenados = []

    if resultado_encadenado["efecto"] is not None:
        efectos_encadenados = [
            resultado_encadenado["efecto"],
            *resultado_encadenado[
                "efectos_encadenados"
            ]
        ]

    return {
        "jugadores":
            resultado_encadenado["jugadores"],

        "jugador":
            resultado_encadenado["jugador"],

        "efecto":
            efecto,

        "dado_extra":
            (
                dado_extra
                if dado_extra is not None
                else resultado_encadenado["dado_extra"]
            ),

        "efectos_encadenados":
            efectos_encadenados
    }

# --------------------------------------------------
# Ejecución de turno
# --------------------------------------------------

@registrar_log
def ejecutar_turno(
    jugadores: List[Dict],
    tablero: List[Dict],
    indice_jugador: int,
    color_objetivo_p1: Optional[str] = None
) -> Dict:
    """
    Ejecuta un turno completo y devuelve
    información sobre su resultado.
    """

    jugador = jugadores[indice_jugador]

    color_jugador = jugador["color"]
    posicion_inicial = jugador["posicion"]

    # ----------------------------------------------
    # Turno perdido
    # ----------------------------------------------

    if debe_perder_turno(jugador):

        jugador_actualizado = consumir_turno_perdido(
            jugador
        )

        jugadores_actualizados = actualizar_jugador(
            jugadores,
            jugador_actualizado
        )

        return {
            "jugadores": jugadores_actualizados,
            "jugador": jugador_actualizado,
            "dado": None,
            "posicion_inicial": posicion_inicial,
            "posicion_despues_dado": posicion_inicial,
            "posicion_final":
                jugador_actualizado["posicion"],
            "pierde_turno": True,
            "ganador": False,
            "efecto": None,
            "dado_extra": None,
            "efectos_encadenados": [],
            "hubo_competencia": False
        }

    # ----------------------------------------------
    # Tirada normal
    # ----------------------------------------------

    dado = tirar_dado()

    jugador_actualizado = mover_jugador(
        jugador,
        dado
    )

    posicion_despues_dado = (
        jugador_actualizado["posicion"]
    )

    jugadores_actualizados = actualizar_jugador(
        jugadores,
        jugador_actualizado
    )

    # ----------------------------------------------
    # Llego a FIN?
    # ----------------------------------------------

    if esta_en_fin(
        jugador_actualizado["posicion"]
    ):

        return {
            "jugadores": jugadores_actualizados,
            "jugador": jugador_actualizado,
            "dado": dado,
            "posicion_inicial": posicion_inicial,
            "posicion_despues_dado":
                posicion_despues_dado,
            "posicion_final":
                jugador_actualizado["posicion"],
            "pierde_turno": False,
            "ganador": True,
            "efecto": None,
            "dado_extra": None,
            "efectos_encadenados": [],
            "hubo_competencia": False
        }

    # ----------------------------------------------
    # Premio o castigo
    # ----------------------------------------------

    resultado_efecto = procesar_efecto(
        jugadores_actualizados,
        tablero,
        jugador_actualizado,
        color_objetivo_p1
    )

    jugadores_actualizados = (
        resultado_efecto["jugadores"]
    )

    jugador_actualizado = (
        resultado_efecto["jugador"]
    )

    efecto = resultado_efecto["efecto"]

    dado_extra = resultado_efecto["dado_extra"]

    efectos_encadenados = (
        resultado_efecto["efectos_encadenados"]
    )

    # ----------------------------------------------
    # Llego a FIN por premio?
    # ----------------------------------------------

    if esta_en_fin(
        jugador_actualizado["posicion"]
    ):

        return {
            "jugadores": jugadores_actualizados,
            "jugador": jugador_actualizado,
            "dado": dado,
            "posicion_inicial": posicion_inicial,
            "posicion_despues_dado":
                posicion_despues_dado,
            "posicion_final":
                jugador_actualizado["posicion"],
            "pierde_turno": False,
            "ganador": True,
            "efecto": efecto,
            "dado_extra": dado_extra,
            "efectos_encadenados":
                efectos_encadenados,
            "hubo_competencia": False
        }

    # ----------------------------------------------
    # Competencia
    # ----------------------------------------------

    hubo_competencia = verificar_competencia(
        jugadores_actualizados,
        jugador_actualizado
    )

    jugadores_actualizados = procesar_competencia(
        jugadores_actualizados,
        jugador_actualizado
    )

    # Una competencia puede haber movido al jugador.
    # Se lo vuelve a recuperar mediante su color.
    jugador_final = obtener_jugador_por_color(
        jugadores_actualizados,
        color_jugador
    )

    return {
        "jugadores": jugadores_actualizados,
        "jugador": jugador_final,
        "dado": dado,
        "posicion_inicial": posicion_inicial,
        "posicion_despues_dado":
            posicion_despues_dado,
        "posicion_final": jugador_final["posicion"],
        "pierde_turno": False,
        "ganador": jugador_final["ganador"],
        "efecto": efecto,
        "dado_extra": dado_extra,
        "efectos_encadenados":
            efectos_encadenados,
        "hubo_competencia": hubo_competencia
    }