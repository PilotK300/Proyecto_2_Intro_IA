def solve_sudoku_BT(sudoku) -> bool:
    """
    Resuelve el Sudoku por backtracking puro.
    Modifica el tablero directamente.
    """
    vacias = sudoku.celdas_vacias()

    def resolver(idx: int) -> bool:
        if idx == len(vacias):
            return True

        fila, col = vacias[idx]

        for valor in range(1, sudoku.N + 1):
            if sudoku.es_valido(fila, col, valor):
                sudoku.grid[fila][col] = valor

                if resolver(idx + 1):
                    return True

                sudoku.grid[fila][col] = 0

        return False

    return resolver(0)
