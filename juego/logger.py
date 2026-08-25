from functools import wraps
from datetime import datetime
from typing import Callable


def registrar_log(funcion: Callable) -> Callable:
    """
    Decorador que registra la ejecución de una función.

    Muestra el nombre de la función ejecutada,
    la fecha y hora, y su resultado.
    """

    @wraps(funcion)
    def wrapper(*args, **kwargs):

        momento = datetime.now().strftime("%H:%M:%S")

        print(
            f"[{momento}] Ejecutando: {funcion.__name__}"
        )

        resultado = funcion(*args, **kwargs)

        print(
            f"[{momento}] Finalizada: {funcion.__name__}"
        )

        return resultado

    return wrapper