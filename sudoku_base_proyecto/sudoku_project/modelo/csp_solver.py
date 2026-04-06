
ASIGNANDO     = "ASIGNANDO"
RETROCEDIENDO = "RETROCEDIENDO"
SOLUCIONADO   = "SOLUCIONADO"

def backtrack_fc(sudoku, vacias: list, idx: int = 0):
    """
    Solución 3: Forward Checking compatible con Bitmasks.
    """
    if idx == len(vacias):
        yield (SOLUCIONADO,)
        return True

    fila, col = vacias[idx]

    # Probamos valores del 1 al N
    for valor in range(1, sudoku.N + 1):
        if sudoku.es_valido(fila, col, valor):
            # Asignación temporal
            sudoku.grid[fila][col] = valor
            yield (ASIGNANDO, fila, col, valor)

            # --- FORWARD CHECKING ---
            # Verificamos si algún vecino se queda sin opciones
            if _forward_checking_consistente(sudoku, vacias, idx + 1):
                exito = False
                for evento in backtrack_fc(sudoku, vacias, idx + 1):
                    yield evento
                    if evento[0] == SOLUCIONADO:
                        exito = True
                        break
                if exito: return True

            # --- BACKTRACK ---
            sudoku.grid[fila][col] = 0
            yield (RETROCEDIENDO, fila, col)

    return False

def _forward_checking_consistente(sudoku, vacias, siguiente_idx):
    """
    Revisa si las celdas futuras tienen al menos un valor válido
    usando la función es_valido de la versión optimizada.
    """
    for i in range(siguiente_idx, len(vacias)):
        f_v, c_v = vacias[i]
        
        # IMPORTANTE: Solo revisamos si la celda es "vecina" 
        # (misma fila, columna o bloque) para ahorrar tiempo.
        # Pero por seguridad, verificamos que tenga al menos una opción:
        hay_opcion = False
        for v in range(1, sudoku.N + 1):
            if sudoku.es_valido(f_v, c_v, v):
                hay_opcion = True
                break
        
        if not hay_opcion:
            return False # Dominio vacío detectado
    return True
