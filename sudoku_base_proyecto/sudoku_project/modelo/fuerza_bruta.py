import random


def _contar_conflictos_celda(sudoku, fila: int, col: int, valor: int) -> int:
    conflictos = 0
    k = sudoku.k
    inicio_fila = (fila // k) * k
    inicio_col = (col // k) * k

    for c in range(sudoku.N):
        if c != col and sudoku.grid[fila][c] == valor:
            conflictos += 1

    for f in range(sudoku.N):
        if f != fila and sudoku.grid[f][col] == valor:
            conflictos += 1

    for f in range(inicio_fila, inicio_fila + k):
        for c in range(inicio_col, inicio_col + k):
            if (f, c) != (fila, col) and sudoku.grid[f][c] == valor:
                conflictos += 1

    return conflictos


def _contar_conflictos_totales(sudoku, editables: list[tuple[int, int]]) -> int:
    return sum(
        _contar_conflictos_celda(sudoku, fila, col, sudoku.grid[fila][col])
        for fila, col in editables
    )


def _llenar_aleatorio(sudoku, editables: list[tuple[int, int]]):
    editables_por_fila: dict[int, list[int]] = {}
    for fila, col in editables:
        editables_por_fila.setdefault(fila, []).append(col)

    for fila, columnas in editables_por_fila.items():
        usados = {sudoku.grid[fila][col] for col in range(sudoku.N) if sudoku.grid[fila][col] != 0}
        faltantes = [valor for valor in range(1, sudoku.N + 1) if valor not in usados]
        random.shuffle(faltantes)

        for indice, col in enumerate(columnas):
            if indice < len(faltantes):
                sudoku.grid[fila][col] = faltantes[indice]
            else:
                sudoku.grid[fila][col] = random.randint(1, sudoku.N)


def _reparar_por_pases(sudoku, editables: list[tuple[int, int]], max_pases: int) -> bool:
    if not editables:
        return True

    mejor_conflicto = _contar_conflictos_totales(sudoku, editables)
    if mejor_conflicto == 0:
        return True

    for _ in range(max_pases):
        hubo_mejora = False

        for fila, col in editables:
            valor_actual = sudoku.grid[fila][col]
            conflicto_actual = _contar_conflictos_celda(sudoku, fila, col, valor_actual)

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

        conflictos = _contar_conflictos_totales(sudoku, editables)
        if conflictos == 0:
            return True

        if conflictos < mejor_conflicto:
            mejor_conflicto = conflictos
            hubo_mejora = True

        if not hubo_mejora:
            return False

    return False


def solve_sudoku_FB(sudoku, max_intentos: int = 500) -> bool:
    """
    Llenado aleatorio con reparacion iterativa y reinicios.

    En cada intento llena las celdas vacias con valores aleatorios, revisa
    restricciones y luego cambia valores celda por celda para reducir
    violaciones. Si se atasca, reinicia desde cero con otro llenado.
    """
    editables = sudoku.celdas_vacias()
    base_grid = [fila[:] for fila in sudoku.grid]

    if not editables:
        return True

    max_pases = max(sudoku.N * 4, len(editables) * 2)

    for _ in range(max_intentos):
        sudoku.grid = [fila[:] for fila in base_grid]
        _llenar_aleatorio(sudoku, editables)

        if _reparar_por_pases(sudoku, editables, max_pases):
            return True

    sudoku.grid = [fila[:] for fila in base_grid]
    return False

