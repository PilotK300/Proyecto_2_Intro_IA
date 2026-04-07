import random
import time
import tracemalloc
from dataclasses import dataclass


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
    Fuerza bruta aleatoria con reinicios y medicion de tiempo/memoria.
    """
    vacias = sudoku.celdas_vacias()
    base_grid = [fila[:] for fila in sudoku.grid]

    if not vacias:
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
    tracemalloc.start()

    try:
        for intento in range(1, max_intentos + 1):
            sudoku.grid = [fila[:] for fila in base_grid]
            orden = vacias[:]
            random.shuffle(orden)
            fallo = False

            for fila, col in orden:
                opciones = [
                    valor
                    for valor in range(1, sudoku.N + 1)
                    if sudoku.es_valido(fila, col, valor)
                ]
                if not opciones:
                    fallo = True
                    break

                sudoku.grid[fila][col] = random.choice(opciones)

            tiempo_actual = time.perf_counter() - inicio
            memoria_actual, memoria_pico = tracemalloc.get_traced_memory()
            muestras_tiempo.append(tiempo_actual)
            muestras_memoria.append(max(memoria_actual, memoria_pico) / 1024.0)

            if not fallo and not sudoku.celdas_vacias():
                return FuerzaBrutaResultado(
                    resuelto=True,
                    intentos_usados=intento,
                    tiempo_total=tiempo_actual,
                    muestras_tiempo=muestras_tiempo,
                    muestras_memoria=muestras_memoria,
                    grid_final=[fila[:] for fila in sudoku.grid],
                )
    finally:
        tracemalloc.stop()

    if not muestras_tiempo:
        muestras_tiempo = [0.0]
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

