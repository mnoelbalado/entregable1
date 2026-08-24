"""
Interfaz gráfica del juego utilizando Pygame.

La interfaz se ocupa de entrada, dibujo y presentación del estado.
La lógica de movimientos, efectos, competencias y ganador permanece
centralizada en motor_juego.py.
"""

from typing import Dict, List, Optional, Tuple

import random
import pygame

from juego.jugadores import crear_jugador
from juego.motor_juego import ejecutar_turno, generar_turnos, resolver_p1
from juego.tablero import CASILLAS_ESPECIALES, crear_tablero


# --------------------------------------------------
# Configuración visual
# --------------------------------------------------

ANCHO = 1250
ALTO = 750
TAM_CASILLA = 58
ORIGEN_X = 90
ORIGEN_Y = 60
PANEL_X = 720
PAUSA_SIMULACION_MS = 1100

COLORES_JUGADORES = [
    "rojo",
    "azul",
    "verde",
    "amarillo"
]

COLORES_PYGAME = {
    "rojo": (220, 55, 55),
    "azul": (55, 105, 220),
    "verde": (45, 165, 85),
    "amarillo": (235, 195, 45)
}

COLORES_CASILLA = {
    "INICIO": (210, 245, 210),
    "FIN": (210, 225, 250),
    "PREMIO": (255, 232, 195),
    "CASTIGO": (250, 205, 205),
    "NORMAL": (250, 250, 250)
}

DESCRIPCIONES_EFECTOS = {
    "P1": "Elige un rival para que pierda un turno.",
    "P2": "Tira nuevamente y avanza.",
    "P3": "Avanza 2 casillas.",
    "C1": "Pierde 1 turno.",
    "C2": "Retrocede 3 casillas."
}

# --------------------------------------------------
# Estados de la aplicación
# --------------------------------------------------

ESTADO_MODO = "modo"
ESTADO_CANTIDAD = "cantidad"
ESTADO_NOMBRES = "nombres"
ESTADO_JUEGO = "juego"
ESTADO_SELECCION_P1 = "seleccion_p1"
ESTADO_GANADOR = "ganador"

MODO_INTERACTIVO = "interactivo"
MODO_SIMULACION = "simulacion"


# --------------------------------------------------
# Funciones de configuración del juego
# --------------------------------------------------

def crear_jugadores_configurados(
    cantidad: int,
    nombres: Optional[List[str]] = None
) -> List[Dict]:
    """
    Crea entre 2 y 4 jugadores con colores únicos.

    Si no se reciben nombres se generan nombres automáticos,
    pensados para el modo simulación.
    """
    if cantidad not in (2, 3, 4):
        raise ValueError("La cantidad de jugadores debe ser 2, 3 o 4.")

    nombres_finales = (
        nombres
        if nombres is not None
        else [f"Jugador {indice + 1}" for indice in range(cantidad)]
    )

    if len(nombres_finales) != cantidad:
        raise ValueError("Debe existir un nombre por cada jugador.")

    return [
        crear_jugador(
            nombres_finales[indice],
            COLORES_JUGADORES[indice]
        )
        for indice in range(cantidad)
    ]


def crear_partida(
    cantidad: int,
    nombres: Optional[List[str]] = None
):
    """
    Crea el tablero, los jugadores y el generador de turnos.
    """
    tablero = crear_tablero()
    jugadores = crear_jugadores_configurados(cantidad, nombres)
    turnos = generar_turnos(jugadores)

    return tablero, jugadores, turnos


def obtener_rivales_p1(
    jugadores: List[Dict],
    color_jugador_actual: str
) -> List[Dict]:
    """
    Devuelve los jugadores que pueden ser elegidos por P1.

    El jugador que cayó en P1 se excluye mediante su color,
    que funciona como identificador único del juego.
    """
    return [
        jugador
        for jugador in jugadores
        if jugador["color"] != color_jugador_actual
    ]


def resolver_seleccion_p1(
    jugadores: List[Dict],
    resultado: Dict,
    rival: Dict
) -> Tuple[List[Dict], Dict]:
    """
    Aplica P1 delegando la modificación del estado al motor.

    La interfaz solamente selecciona el color objetivo y agrega
    metadatos de presentación al resultado del turno ya realizado.
    """
    jugadores_actualizados = resolver_p1(
        jugadores,
        rival["color"]
    )

    resultado_actualizado = {
        **resultado,
        "jugadores": jugadores_actualizados,
        "p1_objetivo": {
            "nombre": rival["nombre"],
            "color": rival["color"]
        }
    }

    return jugadores_actualizados, resultado_actualizado


def resolver_p1_simulacion(
    jugadores: List[Dict],
    resultado: Dict
) -> Tuple[List[Dict], Dict]:
    """
    Elige automáticamente un rival válido en modo simulación
    y aplica P1 mediante resolver_p1().
    """
    rivales = obtener_rivales_p1(
        jugadores,
        resultado["jugador"]["color"]
    )

    if not rivales:
        return jugadores, resultado

    rival_elegido = random.choice(rivales)

    return resolver_seleccion_p1(
        jugadores,
        resultado,
        rival_elegido
    )


# --------------------------------------------------
# Coordenadas del tablero
# --------------------------------------------------

def obtener_coordenadas_tablero() -> List[Tuple[int, int]]:
    """
    Devuelve las coordenadas visuales de las 36 posiciones
    del recorrido del tablero.
    """
    coordenadas = []

    # Lado izquierdo: posiciones 0 a 9
    for fila in range(9, -1, -1):
        coordenadas.append(
            (
                ORIGEN_X,
                ORIGEN_Y + fila * TAM_CASILLA
            )
        )

    # Parte superior: posiciones 10 a 18
    for columna in range(1, 10):
        coordenadas.append(
            (
                ORIGEN_X + columna * TAM_CASILLA,
                ORIGEN_Y
            )
        )

    # Lado derecho: posiciones 19 a 27
    for fila in range(1, 10):
        coordenadas.append(
            (
                ORIGEN_X + 9 * TAM_CASILLA,
                ORIGEN_Y + fila * TAM_CASILLA
            )
        )

    # Parte inferior: posiciones 28 a 35
    for columna in range(8, 0, -1):
        coordenadas.append(
            (
                ORIGEN_X + columna * TAM_CASILLA,
                ORIGEN_Y + 9 * TAM_CASILLA
            )
        )

    return coordenadas


def obtener_centro_casilla(posicion: int) -> Tuple[int, int]:
    """
    Devuelve el centro gráfico de una posición lógica del tablero.
    """
    coordenadas = obtener_coordenadas_tablero()

    if not 0 <= posicion < len(coordenadas):
        raise ValueError("La posición debe estar entre 0 y 35.")

    x, y = coordenadas[posicion]

    return (
        x + TAM_CASILLA // 2,
        y + TAM_CASILLA // 2
    )


# --------------------------------------------------
# Funciones de dibujo generales
# --------------------------------------------------

def dibujar_texto(
    pantalla,
    texto: str,
    fuente,
    posicion: Tuple[int, int],
    color=(25, 25, 25)
):
    """
    Dibuja una línea de texto en la posición indicada.
    """
    superficie = fuente.render(texto, True, color)
    pantalla.blit(superficie, posicion)


def dibujar_lineas(
    pantalla,
    lineas: List[str],
    fuente,
    x: int,
    y: int,
    separacion: int = 26
):
    """
    Dibuja varias líneas de texto de forma vertical.
    """
    for indice, linea in enumerate(lineas):
        dibujar_texto(
            pantalla,
            linea,
            fuente,
            (x, y + indice * separacion)
        )


def dibujar_pantalla_centrada(
    pantalla,
    titulo: str,
    lineas: List[str],
    fuente_titulo,
    fuente
):
    """
    Dibuja una pantalla de configuración sencilla.
    """
    pantalla.fill((235, 237, 240))

    superficie_titulo = fuente_titulo.render(
        titulo,
        True,
        (25, 25, 25)
    )

    rect_titulo = superficie_titulo.get_rect(
        center=(ANCHO // 2, 180)
    )
    pantalla.blit(superficie_titulo, rect_titulo)

    for indice, linea in enumerate(lineas):
        superficie = fuente.render(
            linea,
            True,
            (35, 35, 35)
        )
        rect = superficie.get_rect(
            center=(ANCHO // 2, 280 + indice * 55)
        )
        pantalla.blit(superficie, rect)


# --------------------------------------------------
# Dibujo del tablero y fichas
# --------------------------------------------------

def obtener_tipo_visual_casilla(etiqueta: Optional[str]) -> str:
    """
    Traduce la etiqueta de una casilla a su categoría visual.
    No modifica ninguna regla del juego.
    """
    if etiqueta == "INICIO":
        return "INICIO"

    if etiqueta == "FIN":
        return "FIN"

    if etiqueta in ("P1", "P2", "P3"):
        return "PREMIO"

    if etiqueta in ("C1", "C2"):
        return "CASTIGO"

    return "NORMAL"


def dibujar_tablero(pantalla, fuente):
    """
    Dibuja visualmente las 36 casillas del recorrido.
    """
    coordenadas = obtener_coordenadas_tablero()

    for posicion, (x, y) in enumerate(coordenadas):
        etiqueta = CASILLAS_ESPECIALES.get(posicion)
        tipo_visual = obtener_tipo_visual_casilla(etiqueta)

        pygame.draw.rect(
            pantalla,
            COLORES_CASILLA[tipo_visual],
            (x, y, TAM_CASILLA, TAM_CASILLA)
        )

        pygame.draw.rect(
            pantalla,
            (35, 35, 35),
            (x, y, TAM_CASILLA, TAM_CASILLA),
            2
        )

        texto = etiqueta if etiqueta is not None else str(posicion)

        superficie_texto = fuente.render(
            texto,
            True,
            (20, 20, 20)
        )

        rect_texto = superficie_texto.get_rect(
            center=(
                x + TAM_CASILLA // 2,
                y + TAM_CASILLA // 2
            )
        )

        pantalla.blit(superficie_texto, rect_texto)


def obtener_desplazamientos_fichas(cantidad: int) -> List[Tuple[int, int]]:
    """
    Devuelve offsets gráficos para separar hasta cuatro fichas
    que se encuentren en una misma casilla.
    """
    desplazamientos = {
        1: [(0, 0)],
        2: [(-13, 0), (13, 0)],
        3: [(-13, -10), (13, -10), (0, 13)],
        4: [(-13, -13), (13, -13), (-13, 13), (13, 13)]
    }

    return desplazamientos.get(cantidad, [(0, 0)] * cantidad)


def dibujar_fichas(pantalla, jugadores: List[Dict]):
    """
    Dibuja las fichas utilizando únicamente la posición lógica
    almacenada por el motor.
    """
    jugadores_por_posicion = {}

    for jugador in jugadores:
        jugadores_por_posicion.setdefault(
            jugador["posicion"],
            []
        ).append(jugador)

    for posicion, ocupantes in jugadores_por_posicion.items():
        centro_x, centro_y = obtener_centro_casilla(posicion)
        desplazamientos = obtener_desplazamientos_fichas(
            len(ocupantes)
        )

        for jugador, (dx, dy) in zip(
            ocupantes,
            desplazamientos
        ):
            color = COLORES_PYGAME[jugador["color"]]

            pygame.draw.circle(
                pantalla,
                color,
                (centro_x + dx, centro_y + dy),
                10
            )

            pygame.draw.circle(
                pantalla,
                (20, 20, 20),
                (centro_x + dx, centro_y + dy),
                10,
                2
            )


# --------------------------------------------------
# Información del turno
# --------------------------------------------------

def describir_efecto(efecto: str) -> str:
    """
    Devuelve únicamente una descripción para mostrar en pantalla.
    No aplica efectos ni contiene lógica del motor.
    """
    return DESCRIPCIONES_EFECTOS.get(
        efecto,
        "Efecto especial."
    )


def formatear_resultado_turno(
    resultado: Optional[Dict]
) -> List[str]:
    """
    Convierte los datos devueltos por el motor en líneas de texto
    para la interfaz. No modifica el estado del juego.
    """
    if resultado is None:
        return ["La partida todavía no comenzó."]

    jugador = resultado["jugador"]

    if resultado["pierde_turno"]:
        return [
            f"{jugador['nombre']} pierde este turno.",
            f"Permanece en la casilla {resultado['posicion_final']}."
        ]

    lineas = [
        f"{jugador['nombre']} sacó {resultado['dado']}.",
        (
            "Movimiento: "
            f"{resultado['posicion_inicial']} -> "
            f"{resultado['posicion_despues_dado']}"
        )
    ]

    efecto = resultado["efecto"]

    if efecto is not None:
        lineas.append(f"Cayó en {efecto}: {describir_efecto(efecto)}")

        if efecto == "P1":
            objetivo_p1 = resultado.get("p1_objetivo")

            if objetivo_p1 is None:
                lineas.append("Esperando selección de rival.")
            else:
                lineas.append(
                    f"Eligió a {objetivo_p1['nombre']} "
                    f"({objetivo_p1['color']})."
                )
                lineas.append(
                    f"{objetivo_p1['nombre']} pierde su próximo turno."
                )

    if resultado["dado_extra"] is not None:
        lineas.append(
            f"P2: tirada adicional = {resultado['dado_extra']}."
        )

    for efecto_encadenado in resultado["efectos_encadenados"]:
        lineas.append(
            "Luego cayó en "
            f"{efecto_encadenado}: "
            f"{describir_efecto(efecto_encadenado)}"
        )

    if resultado["hubo_competencia"]:
        lineas.append("Hubo una competencia por la casilla.")

    lineas.append(
        f"Posición final: {resultado['posicion_final']}."
    )

    return lineas


def dibujar_panel_estado(
    pantalla,
    jugadores: List[Dict],
    indice_jugador: int,
    ultimo_resultado: Optional[Dict],
    modo: str,
    fuente_titulo,
    fuente
):
    """
    Dibuja el estado permanente de la partida y el último evento.
    """
    pygame.draw.rect(
        pantalla,
        (245, 246, 248),
        (PANEL_X, 35, ANCHO - PANEL_X - 25, ALTO - 70),
        border_radius=8
    )

    pygame.draw.rect(
        pantalla,
        (70, 70, 70),
        (PANEL_X, 35, ANCHO - PANEL_X - 25, ALTO - 70),
        2,
        border_radius=8
    )

    dibujar_texto(
        pantalla,
        "Estado de la partida",
        fuente_titulo,
        (PANEL_X + 20, 55)
    )

    modo_texto = (
        "Interactivo"
        if modo == MODO_INTERACTIVO
        else "Simulación"
    )

    dibujar_texto(
        pantalla,
        f"Modo: {modo_texto}",
        fuente,
        (PANEL_X + 20, 100)
    )

    jugador_turno = jugadores[indice_jugador]

    dibujar_texto(
        pantalla,
        f"Turno: {jugador_turno['nombre']} ({jugador_turno['color']})",
        fuente,
        (PANEL_X + 20, 130)
    )

    if ultimo_resultado is None:
        ultimo_dado = "-"
    else:
        ultimo_dado = (
            "-"
            if ultimo_resultado["dado"] is None
            else str(ultimo_resultado["dado"])
        )

    dibujar_texto(
        pantalla,
        f"Último dado: {ultimo_dado}",
        fuente,
        (PANEL_X + 20, 160)
    )

    dibujar_texto(
        pantalla,
        "Jugadores",
        fuente_titulo,
        (PANEL_X + 20, 205)
    )

    y_jugadores = 245

    for jugador in jugadores:
        color = COLORES_PYGAME[jugador["color"]]

        pygame.draw.circle(
            pantalla,
            color,
            (PANEL_X + 30, y_jugadores + 9),
            8
        )

        dibujar_texto(
            pantalla,
            (
                f"{jugador['nombre']} ({jugador['color']}): "
                f"casilla {jugador['posicion']} - "
                f"turnos perdidos: {jugador['turnos_perdidos']}"
            ),
            fuente,
            (PANEL_X + 48, y_jugadores)
        )

        y_jugadores += 30

    dibujar_texto(
        pantalla,
        "Último evento",
        fuente_titulo,
        (PANEL_X + 20, 385)
    )

    lineas_resultado = formatear_resultado_turno(
        ultimo_resultado
    )

    dibujar_lineas(
        pantalla,
        lineas_resultado,
        fuente,
        PANEL_X + 20,
        425,
        27
    )

    if modo == MODO_INTERACTIVO:
        dibujar_texto(
            pantalla,
            "SPACE o ENTER: tirar el dado",
            fuente,
            (PANEL_X + 20, 650)
        )
    else:
        dibujar_texto(
            pantalla,
            "La partida avanza automáticamente.",
            fuente,
            (PANEL_X + 20, 650)
        )


# --------------------------------------------------
# Pantallas de configuración
# --------------------------------------------------

def dibujar_pantalla_modo(
    pantalla,
    fuente_titulo,
    fuente
):
    dibujar_pantalla_centrada(
        pantalla,
        "Juego de Tablero",
        [
            "I - Modo interactivo",
            "S - Modo simulación",
            "ESC - Salir"
        ],
        fuente_titulo,
        fuente
    )


def dibujar_pantalla_cantidad(
    pantalla,
    modo: str,
    fuente_titulo,
    fuente
):
    modo_texto = (
        "interactivo"
        if modo == MODO_INTERACTIVO
        else "simulación"
    )

    dibujar_pantalla_centrada(
        pantalla,
        "Cantidad de jugadores",
        [
            f"Modo seleccionado: {modo_texto}",
            "Presioná 2, 3 o 4",
            "ESC - Salir"
        ],
        fuente_titulo,
        fuente
    )


def dibujar_pantalla_nombre(
    pantalla,
    indice_nombre: int,
    cantidad: int,
    texto_actual: str,
    fuente_titulo,
    fuente
):
    color = COLORES_JUGADORES[indice_nombre]

    dibujar_pantalla_centrada(
        pantalla,
        "Nombre de jugador",
        [
            (
                f"Jugador {indice_nombre + 1} de {cantidad} "
                f"- color {color}"
            ),
            f"> {texto_actual}_",
            "ENTER - confirmar   BACKSPACE - borrar"
        ],
        fuente_titulo,
        fuente
    )


def dibujar_pantalla_seleccion_p1(
    pantalla,
    jugador_actual: Dict,
    rivales: List[Dict],
    fuente_titulo,
    fuente
):
    """
    Muestra los rivales disponibles para resolver P1 mediante teclado.
    """
    lineas = [
        (
            f"{jugador_actual['nombre']} "
            f"({jugador_actual['color']}) cayó en P1."
        ),
        "Elegí un rival para que pierda un turno."
    ]

    lineas.extend(
        f"{indice + 1} - {rival['nombre']} ({rival['color']})"
        for indice, rival in enumerate(rivales)
    )

    opciones = ", ".join(
        str(indice + 1)
        for indice in range(len(rivales))
    )

    lineas.append(f"Presioná {opciones}")

    dibujar_pantalla_centrada(
        pantalla,
        "P1 - Selección de rival",
        lineas,
        fuente_titulo,
        fuente
    )


def dibujar_pantalla_ganador(
    pantalla,
    ganador: Dict,
    fuente_grande,
    fuente
):
    pantalla.fill((235, 237, 240))

    color = COLORES_PYGAME[ganador["color"]]

    superficie = fuente_grande.render(
        f"¡Ganó {ganador['nombre']}!",
        True,
        color
    )

    rect = superficie.get_rect(
        center=(ANCHO // 2, ALTO // 2 - 40)
    )
    pantalla.blit(superficie, rect)

    superficie_color = fuente.render(
        f"Color: {ganador['color']}",
        True,
        (30, 30, 30)
    )

    rect_color = superficie_color.get_rect(
        center=(ANCHO // 2, ALTO // 2 + 25)
    )
    pantalla.blit(superficie_color, rect_color)

    superficie_cierre = fuente.render(
        "Cerrá la ventana o presioná ESC para salir.",
        True,
        (30, 30, 30)
    )

    rect_cierre = superficie_cierre.get_rect(
        center=(ANCHO // 2, ALTO // 2 + 80)
    )
    pantalla.blit(superficie_cierre, rect_cierre)


# --------------------------------------------------
# Integración interfaz -> motor
# --------------------------------------------------

def realizar_turno(
    jugadores: List[Dict],
    tablero: List[Dict],
    indice_jugador: int
) -> Dict:
    """
    Ejecuta exactamente un turno a través del motor.

    P1 se invoca sin color objetivo porque la elección del rival
    se resuelve después del turno desde la interfaz, sin volver a tirar.
    """
    return ejecutar_turno(
        jugadores,
        tablero,
        indice_jugador
    )


# --------------------------------------------------
# Loop principal de Pygame
# --------------------------------------------------

def iniciar_interfaz():
    """
    Inicia la aplicación gráfica y administra sus estados.
    """
    pygame.init()

    pantalla = pygame.display.set_mode(
        (ANCHO, ALTO)
    )

    pygame.display.set_caption(
        "Entregable 1 - Juego de Tablero"
    )

    fuente = pygame.font.SysFont(None, 24)
    fuente_titulo = pygame.font.SysFont(None, 32)
    fuente_grande = pygame.font.SysFont(None, 52)

    reloj = pygame.time.Clock()

    estado = ESTADO_MODO
    modo = None
    cantidad_jugadores = None

    nombres = []
    indice_nombre = 0
    texto_nombre = ""

    tablero = None
    jugadores = []
    turnos = None
    indice_jugador = 0

    ultimo_resultado = None
    ganador = None
    ultimo_turno_simulacion = 0

    rivales_p1 = []

    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
                continue

            if evento.type != pygame.KEYDOWN:
                continue

            if evento.key == pygame.K_ESCAPE:
                ejecutando = False
                continue

            # --------------------------------------
            # Selección de modo
            # --------------------------------------
            if estado == ESTADO_MODO:
                if evento.key == pygame.K_i:
                    modo = MODO_INTERACTIVO
                    estado = ESTADO_CANTIDAD

                elif evento.key == pygame.K_s:
                    modo = MODO_SIMULACION
                    estado = ESTADO_CANTIDAD

            # --------------------------------------
            # Cantidad de jugadores
            # --------------------------------------
            elif estado == ESTADO_CANTIDAD:
                teclas_cantidad = {
                    pygame.K_2: 2,
                    pygame.K_3: 3,
                    pygame.K_4: 4
                }

                if evento.key in teclas_cantidad:
                    cantidad_jugadores = teclas_cantidad[evento.key]

                    if modo == MODO_SIMULACION:
                        tablero, jugadores, turnos = crear_partida(
                            cantidad_jugadores
                        )
                        indice_jugador = next(turnos)
                        ultimo_resultado = None
                        ultimo_turno_simulacion = pygame.time.get_ticks()
                        estado = ESTADO_JUEGO

                    else:
                        nombres = []
                        indice_nombre = 0
                        texto_nombre = ""
                        estado = ESTADO_NOMBRES

            # --------------------------------------
            # Ingreso de nombres
            # --------------------------------------
            elif estado == ESTADO_NOMBRES:
                if evento.key == pygame.K_BACKSPACE:
                    texto_nombre = texto_nombre[:-1]

                elif evento.key == pygame.K_RETURN:
                    nombre_confirmado = texto_nombre.strip()

                    if nombre_confirmado:
                        nombres.append(nombre_confirmado)
                        indice_nombre += 1
                        texto_nombre = ""

                        if indice_nombre == cantidad_jugadores:
                            tablero, jugadores, turnos = crear_partida(
                                cantidad_jugadores,
                                nombres
                            )
                            indice_jugador = next(turnos)
                            ultimo_resultado = None
                            estado = ESTADO_JUEGO

                else:
                    caracter = evento.unicode

                    if (
                        len(texto_nombre) < 20
                        and caracter
                        and (
                            caracter.isalpha()
                            or caracter == " "
                        )
                    ):
                        texto_nombre += caracter

            # --------------------------------------
            # Juego interactivo
            # --------------------------------------
            elif (
                estado == ESTADO_JUEGO
                and modo == MODO_INTERACTIVO
            ):
                if evento.key in (
                    pygame.K_SPACE,
                    pygame.K_RETURN
                ):
                    resultado = realizar_turno(
                        jugadores,
                        tablero,
                        indice_jugador
                    )

                    jugadores = resultado["jugadores"]
                    ultimo_resultado = resultado

                    if resultado["ganador"]:
                        ganador = resultado["jugador"]
                        estado = ESTADO_GANADOR

                    elif resultado["efecto"] == "P1":
                        rivales_p1 = obtener_rivales_p1(
                            jugadores,
                            resultado["jugador"]["color"]
                        )
                        estado = ESTADO_SELECCION_P1

                    else:
                        indice_jugador = next(turnos)

            # --------------------------------------
            # Selección de rival para P1
            # --------------------------------------
            elif (
                estado == ESTADO_SELECCION_P1
                and modo == MODO_INTERACTIVO
            ):
                teclas_p1 = {
                    pygame.K_1: 0,
                    pygame.K_2: 1,
                    pygame.K_3: 2
                }

                indice_rival = teclas_p1.get(evento.key)

                if (
                    indice_rival is not None
                    and indice_rival < len(rivales_p1)
                ):
                    rival_elegido = rivales_p1[indice_rival]

                    jugadores, ultimo_resultado = resolver_seleccion_p1(
                        jugadores,
                        ultimo_resultado,
                        rival_elegido
                    )

                    rivales_p1 = []
                    indice_jugador = next(turnos)
                    estado = ESTADO_JUEGO

        # ------------------------------------------
        # Simulación automática no bloqueante
        # ------------------------------------------
        if (
            ejecutando
            and estado == ESTADO_JUEGO
            and modo == MODO_SIMULACION
        ):
            ahora = pygame.time.get_ticks()

            if (
                ahora - ultimo_turno_simulacion
                >= PAUSA_SIMULACION_MS
            ):
                resultado = realizar_turno(
                    jugadores,
                    tablero,
                    indice_jugador
                )

                jugadores = resultado["jugadores"]
                ultimo_resultado = resultado
                ultimo_turno_simulacion = ahora

                if resultado["ganador"]:
                    ganador = resultado["jugador"]
                    estado = ESTADO_GANADOR

                elif resultado["efecto"] == "P1":
                    jugadores, ultimo_resultado = resolver_p1_simulacion(
                        jugadores,
                        resultado
                    )
                    indice_jugador = next(turnos)

                else:
                    indice_jugador = next(turnos)

        # ------------------------------------------
        # Dibujo según estado
        # ------------------------------------------
        if estado == ESTADO_MODO:
            dibujar_pantalla_modo(
                pantalla,
                fuente_titulo,
                fuente
            )

        elif estado == ESTADO_CANTIDAD:
            dibujar_pantalla_cantidad(
                pantalla,
                modo,
                fuente_titulo,
                fuente
            )

        elif estado == ESTADO_NOMBRES:
            dibujar_pantalla_nombre(
                pantalla,
                indice_nombre,
                cantidad_jugadores,
                texto_nombre,
                fuente_titulo,
                fuente
            )

        elif estado == ESTADO_SELECCION_P1:
            dibujar_pantalla_seleccion_p1(
                pantalla,
                ultimo_resultado["jugador"],
                rivales_p1,
                fuente_titulo,
                fuente
            )

        elif estado == ESTADO_JUEGO:
            pantalla.fill((225, 228, 232))

            dibujar_tablero(
                pantalla,
                fuente
            )

            dibujar_fichas(
                pantalla,
                jugadores
            )

            dibujar_panel_estado(
                pantalla,
                jugadores,
                indice_jugador,
                ultimo_resultado,
                modo,
                fuente_titulo,
                fuente
            )

        elif estado == ESTADO_GANADOR:
            dibujar_pantalla_ganador(
                pantalla,
                ganador,
                fuente_grande,
                fuente
            )

        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()