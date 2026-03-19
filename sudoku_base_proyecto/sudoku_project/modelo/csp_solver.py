# ──────────────────────────────────────────────
#  modelo/csp_solver.py  –  Backtracking como generador
# ──────────────────────────────────────────────


# Eventos que emite el generador
ASIGNANDO   = "ASIGNANDO"    # prueba un valor
RETROCEDIENDO = "RETROCEDIENDO"  # deshace una asignación
SOLUCIONADO = "SOLUCIONADO"  # tablero completo


def backtrack(sudoku, vacias: list, idx: int = 0):
    """
    Generador que resuelve el Sudoku paso a paso.
    En cada paso hace `yield` de una tupla que describe
    la acción realizada, para que la vista pueda animarla.

    Tuplas emitidas:
        (ASIGNANDO,    fila, col, valor)
        (RETROCEDIENDO, fila, col)
        (SOLUCIONADO,)
    """
    if idx == len(vacias):
        yield (SOLUCIONADO,)
        return

    fila, col = vacias[idx]

    for valor in range(1, sudoku.N + 1):
        if sudoku.es_valido(fila, col, valor):
            sudoku.grid[fila][col] = valor
            yield (ASIGNANDO, fila, col, valor)

            # Continuar con la siguiente celda vacía
            solucionado = False
            for evento in backtrack(sudoku, vacias, idx + 1):
                yield evento
                if evento[0] == SOLUCIONADO:
                    solucionado = True
                    break
            if solucionado:
                return

            # Deshacer
            sudoku.grid[fila][col] = 0
            yield (RETROCEDIENDO, fila, col)

    # Sin valor válido → el llamador retrocederá
