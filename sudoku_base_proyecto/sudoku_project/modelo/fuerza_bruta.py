def solve_sudoku_FB(sudoku):
    """
    Fuerza bruta: prueba todas las combinaciones posibles.
    Modifica el tablero directamente.
    
    Retorna:
        True  -> si encuentra solución
        False -> si no hay solución
    """

    vacias = sudoku.celdas_vacias()

    def resolver(idx):
        # Caso base: ya llenó todo
        if idx == len(vacias):
            return True

        fila, col = vacias[idx]

        # Probar TODOS los valores (sin inteligencia)
        for valor in range(1, sudoku.N + 1):

            if sudoku.es_valido(fila, col, valor):
                sudoku.grid[fila][col] = valor

                if resolver(idx + 1):
                    return True

                # Backtrack
                sudoku.grid[fila][col] = 0

        return False

    return resolver(0)