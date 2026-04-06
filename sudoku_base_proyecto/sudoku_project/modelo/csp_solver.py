# ──────────────────────────────────────────────
#  modelo/csp_solver.py  –  Backtracking con Forward Checking
# ──────────────────────────────────────────────

# Eventos para la animación en la vista (interfaz Arcade)
ASIGNANDO     = "ASIGNANDO"     
RETROCEDIENDO = "RETROCEDIENDO" 
SOLUCIONADO   = "SOLUCIONADO"   

def backtrack_fc(sudoku, vacias: list, idx: int = 0):
    """
    Solución 3: Backtracking con Forward Checking.
    Utiliza la estructura optimizada de peers del objeto Sudoku.
    """
    # 1. Si no hay más celdas vacías, el Sudoku está resuelto [cite: 59]
    if idx == len(vacias):
        yield (SOLUCIONADO,)
        return True

    fila, col = vacias[idx] # Seleccionar variable no asignada [cite: 50]

    # 2. Intentar asignar valores del 1 al N (ej. 1 al 9)
    for valor in range(1, sudoku.N + 1):
        # Verificamos si es válido usando el método de tu sudoku.py
        if sudoku.es_valido(fila, col, valor):
            
            # Aplicar la asignación
            sudoku.grid[fila][col] = valor
            yield (ASIGNANDO, fila, col, valor)

            # 3. COMPROBACIÓN HACIA ADELANTE (Forward Checking) [cite: 52]
            # Verificamos consistencia en las variables vecinas (peers)
            if _forward_check_consistente(sudoku, vacias, idx + 1):
                
                # 4. Si es consistente, procedemos con la siguiente celda [cite: 56]
                exito = False
                for evento in backtrack_fc(sudoku, vacias, idx + 1):
                    yield evento
                    if evento[0] == SOLUCIONADO:
                        exito = True
                        break
                
                if exito:
                    return True

            # 5. Si falla la consistencia o la recursión, retrocedemos [cite: 58]
            sudoku.grid[fila][col] = 0
            yield (RETROCEDIENDO, fila, col)

    return False

def _forward_check_consistente(sudoku, vacias, siguiente_idx):
    """
    Analiza las restricciones de las celdas vecinas para prevenir 
    soluciones inválidas en el futuro[cite: 44, 45].
    """
    # Revisamos las celdas que aún faltan por llenar
    for i in range(siguiente_idx, len(vacias)):
        f_v, c_v = vacias[i]
        
        # Un dominio se vacía si no hay ningún valor que cumpla las restricciones [cite: 56]
        tiene_valor_posible = False
        for v in range(1, sudoku.N + 1):
            if sudoku.es_valido(f_v, c_v, v):
                tiene_valor_posible = True
                break
        
        # Si una celda vecina se queda sin opciones, esta rama no sirve [cite: 54, 55]
        if not tiene_valor_posible:
            return False 
            
    return True
