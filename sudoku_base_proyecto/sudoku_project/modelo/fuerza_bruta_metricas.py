import random
import time
import tracemalloc
from dataclasses import dataclass

from modelo.fuerza_bruta import (
    _contar_conflictos_celda,
    _contar_conflictos_totales,
    _llenar_aleatorio,
)


@dataclass
class FuerzaBrutaResultado:
    resuelto: bool
    intentos_usados: int
    tiempo_total: float
    muestras_tiempo: list[float]
    muestras_memoria: list[float]
    grid_final: list[list[int]]


def solve_sudoku_FB_metricas(sudoku, max_intentos: int = 500) -> FuerzaBrutaResultado:
    """
    Llenado aleatorio con reparacion iterativa y medicion de tiempo/memoria.
    """
    editables = sudoku.celdas_vacias()
    base_grid = [fila[:] for fila in sudoku.grid]

    if not editables:
        return FuerzaBrutaResultado(
            resuelto=True,
            intentos_usados=0,
            tiempo_total=0.0,
            muestras_tiempo=[0.0],
            muestras_memoria=[0.0],
            grid_final=base_grid,
        )

    inicio = time.perf_counter()
    muestras_tiempo: list[float] = []
    muestras_memoria: list[float] = []
    max_pases = max(sudoku.N * 4, len(editables) * 2)
    tracemalloc.start()

    try:
        def registrar_muestra():
            tiempo_actual = time.perf_counter() - inicio
            memoria_actual, memoria_pico = tracemalloc.get_traced_memory()
            muestras_tiempo.append(tiempo_actual)
            muestras_memoria.append(max(memoria_actual, memoria_pico) / 1024.0)

        def reparar_intento() -> bool:
            mejor_conflicto = _contar_conflictos_totales(sudoku, editables)
            registrar_muestra()

            if mejor_conflicto == 0:
                return True

            for _ in range(max_pases):
                hubo_mejora = False

                for fila, col in editables:
                    valor_actual = sudoku.grid[fila][col]
                    conflicto_actual = _contar_conflictos_celda(
                        sudoku, fila, col, valor_actual
                    )

                    if conflicto_actual == 0:
                        continue

                    mejores_valores = []
                    mejor_puntaje = conflicto_actual

                    for valor in range(1, sudoku.N + 1):
                        sudoku.grid[fila][col] = valor
                        puntaje = _contar_conflictos_celda(sudoku, fila, col, valor)

                        if puntaje < mejor_puntaje:
                            mejor_puntaje = puntaje
                            mejores_valores = [valor]
                        elif puntaje == mejor_puntaje:
                            mejores_valores.append(valor)

                    if mejores_valores:
                        sudoku.grid[fila][col] = random.choice(mejores_valores)
                        if mejor_puntaje < conflicto_actual:
                            hubo_mejora = True
                    else:
                        sudoku.grid[fila][col] = valor_actual

                    registrar_muestra()

                conflictos = _contar_conflictos_totales(sudoku, editables)
                if conflictos == 0:
                    return True

                if conflictos < mejor_conflicto:
                    mejor_conflicto = conflictos
                    hubo_mejora = True

                if not hubo_mejora:
                    return False

            return False

        for intento in range(1, max_intentos + 1):
            sudoku.grid = [fila[:] for fila in base_grid]
            _llenar_aleatorio(sudoku, editables)

            if reparar_intento():
                if not muestras_tiempo:
                    registrar_muestra()
                return FuerzaBrutaResultado(
                    resuelto=True,
                    intentos_usados=intento,
                    tiempo_total=muestras_tiempo[-1],
                    muestras_tiempo=muestras_tiempo,
                    muestras_memoria=muestras_memoria,
                    grid_final=[fila[:] for fila in sudoku.grid],
                )
    finally:
        tracemalloc.stop()

    if not muestras_tiempo:
        muestras_tiempo = [time.perf_counter() - inicio]
        muestras_memoria = [0.0]

    sudoku.grid = [fila[:] for fila in base_grid]
    return FuerzaBrutaResultado(
        resuelto=False,
        intentos_usados=max_intentos,
        tiempo_total=muestras_tiempo[-1],
        muestras_tiempo=muestras_tiempo,
        muestras_memoria=muestras_memoria,
        grid_final=base_grid,
    )

