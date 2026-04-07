import random


def solve_sudoku_FB(sudoku, max_intentos: int = 500) -> bool:
    """
    Fuerza bruta aleatoria con reinicios.

    En cada intento llena las celdas vacias con valores validos elegidos al azar.
    Si en algun punto se queda sin opciones, reinicia el intento completo.
    Si logra llenar todo el tablero, la solucion queda escrita en ``sudoku.grid``.
    """
    vacias = sudoku.celdas_vacias()
    base_grid = [fila[:] for fila in sudoku.grid]

    if not vacias:
        return True

    for _ in range(max_intentos):
        sudoku.grid = [fila[:] for fila in base_grid]
        orden = vacias[:]
        random.shuffle(orden)
        asignadas = []
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

            valor = random.choice(opciones)
            sudoku.grid[fila][col] = valor
            asignadas.append((fila, col))

        if not fallo and not sudoku.celdas_vacias():
            return True

    sudoku.grid = [fila[:] for fila in base_grid]
    return False

