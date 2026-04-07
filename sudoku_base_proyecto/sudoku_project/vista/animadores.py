import random

ASIGNANDO = "ASIGNANDO"
PODANDO = "PODANDO"
RETROCEDIENDO = "RETROCEDIENDO"
SOLUCIONADO = "SOLUCIONADO"


def animar_fuerza_bruta(sudoku, max_intentos: int = 200):
    """Generador visual para fuerza bruta aleatoria con reinicios."""
    vacias = sudoku.celdas_vacias()
    base_grid = [fila[:] for fila in sudoku.grid]

    if not vacias:
        yield (SOLUCIONADO,)
        return

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
            yield (ASIGNANDO, fila, col, valor)

        if not fallo and not sudoku.celdas_vacias():
            yield (SOLUCIONADO,)
            return

        for fila, col in reversed(asignadas):
            sudoku.grid[fila][col] = 0
            yield (RETROCEDIENDO, fila, col)

    sudoku.grid = [fila[:] for fila in base_grid]


def animar_backtracking(sudoku):
    """Generador visual para backtracking."""
    vacias = sudoku.celdas_vacias()

    def resolver(idx: int):
        if idx == len(vacias):
            yield (SOLUCIONADO,)
            return True

        fila, col = vacias[idx]

        for valor in range(1, sudoku.N + 1):
            if sudoku.es_valido(fila, col, valor):
                sudoku.grid[fila][col] = valor
                yield (ASIGNANDO, fila, col, valor)

                solucionado = yield from resolver(idx + 1)
                if solucionado:
                    return True

                sudoku.grid[fila][col] = 0
                yield (RETROCEDIENDO, fila, col)

        return False

    yield from resolver(0)


def animar_forward_checking(sudoku):
    """Generador visual para forward checking con backtracking."""
    dominios = _inicializar_dominios(sudoku)
    if not all(dominios[var] for var in dominios):
        return

    def resolver():
        variable = _seleccionar_variable_no_asignada(sudoku, dominios)
        if variable is None:
            yield (SOLUCIONADO,)
            return True

        fila, col = variable
        dominio_actual = sorted(dominios[variable])

        for valor in dominio_actual:
            if not sudoku.es_valido(fila, col, valor):
                continue

            dominio_original = set(dominios[variable])
            sudoku.grid[fila][col] = valor
            dominios[variable] = {valor}
            yield (ASIGNANDO, fila, col, valor)

            consistente, cambios = _forward_check(sudoku, dominios, fila, col, valor)
            for vecino in cambios:
                yield (PODANDO, vecino[0], vecino[1])

            if consistente:
                solucionado = yield from resolver()
                if solucionado:
                    return True

            sudoku.grid[fila][col] = 0
            dominios[variable] = dominio_original
            _restaurar_dominios(dominios, cambios)
            yield (RETROCEDIENDO, fila, col)

        return False

    yield from resolver()


def _inicializar_dominios(sudoku) -> dict[tuple[int, int], set[int]]:
    dominios = {}
    for fila in range(sudoku.N):
        for col in range(sudoku.N):
            if sudoku.grid[fila][col] != 0:
                continue
            dominios[(fila, col)] = {
                valor
                for valor in range(1, sudoku.N + 1)
                if sudoku.es_valido(fila, col, valor)
            }
    return dominios


def _seleccionar_variable_no_asignada(sudoku, dominios) -> tuple[int, int] | None:
    no_asignadas = [
        var
        for var in dominios
        if sudoku.grid[var[0]][var[1]] == 0
    ]
    if not no_asignadas:
        return None
    return min(no_asignadas, key=lambda var: len(dominios[var]))


def _obtener_vecinos(sudoku, fila: int, col: int) -> set[tuple[int, int]]:
    vecinos = set()

    for i in range(sudoku.N):
        if i != col and sudoku.grid[fila][i] == 0:
            vecinos.add((fila, i))
        if i != fila and sudoku.grid[i][col] == 0:
            vecinos.add((i, col))

    inicio_fila = (fila // sudoku.k) * sudoku.k
    inicio_col = (col // sudoku.k) * sudoku.k
    for f in range(inicio_fila, inicio_fila + sudoku.k):
        for c in range(inicio_col, inicio_col + sudoku.k):
            if (f, c) != (fila, col) and sudoku.grid[f][c] == 0:
                vecinos.add((f, c))

    return vecinos


def _forward_check(sudoku, dominios, fila: int, col: int, valor: int) -> tuple[bool, dict]:
    cambios = {}

    for vecino in _obtener_vecinos(sudoku, fila, col):
        if valor not in dominios[vecino]:
            continue

        cambios[vecino] = set(dominios[vecino])
        dominios[vecino].discard(valor)

        if not dominios[vecino]:
            return False, cambios

    return True, cambios


def _restaurar_dominios(dominios, cambios: dict[tuple[int, int], set[int]]):
    for variable, dominio in cambios.items():
        dominios[variable] = dominio
