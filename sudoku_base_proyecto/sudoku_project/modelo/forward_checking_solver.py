class ForwardCheckingSolver:
    """
    Resolvedor por backtracking con forward checking.

    Sigue la idea del algoritmo del enunciado:
    1. Selecciona una variable no asignada.
    2. Prueba valores de su dominio.
    3. Propaga restricciones a los vecinos.
    4. Retrocede si alguna variable queda sin dominio.
    """

    def __init__(self, sudoku):
        self.sudoku = sudoku
        self.dominios = self._inicializar_dominios()

    def resolver(self) -> bool:
        """Intenta resolver el Sudoku modificando el tablero actual."""
        if not self._dominios_consistentes():
            return False
        return self._backtrack()

    def _inicializar_dominios(self) -> dict[tuple[int, int], set[int]]:
        """Construye el dominio inicial de cada celda vacia."""
        dominios = {}
        for fila in range(self.sudoku.N):
            for col in range(self.sudoku.N):
                if self.sudoku.grid[fila][col] != 0:
                    continue
                dominios[(fila, col)] = {
                    valor
                    for valor in range(1, self.sudoku.N + 1)
                    if self.sudoku.es_valido(fila, col, valor)
                }
        return dominios

    def _dominios_consistentes(self) -> bool:
        """Verifica que ninguna variable vacia empiece sin opciones."""
        return all(self.dominios[var] for var in self.dominios)

    def _seleccionar_variable_no_asignada(self) -> tuple[int, int] | None:
        """
        Elige la siguiente variable no asignada.
        Usa MRV para que el algoritmo sea mas estable, sin salir
        de la estructura del pseudocodigo pedido.
        """
        no_asignadas = [
            var
            for var in self.dominios
            if self.sudoku.grid[var[0]][var[1]] == 0
        ]
        if not no_asignadas:
            return None
        return min(no_asignadas, key=lambda var: len(self.dominios[var]))

    def _obtener_vecinos(self, fila: int, col: int) -> set[tuple[int, int]]:
        """Retorna las variables vecinas aun no asignadas."""
        vecinos = set()

        for i in range(self.sudoku.N):
            if i != col and self.sudoku.grid[fila][i] == 0:
                vecinos.add((fila, i))
            if i != fila and self.sudoku.grid[i][col] == 0:
                vecinos.add((i, col))

        inicio_fila = (fila // self.sudoku.k) * self.sudoku.k
        inicio_col = (col // self.sudoku.k) * self.sudoku.k
        for f in range(inicio_fila, inicio_fila + self.sudoku.k):
            for c in range(inicio_col, inicio_col + self.sudoku.k):
                if (f, c) != (fila, col) and self.sudoku.grid[f][c] == 0:
                    vecinos.add((f, c))

        return vecinos

    def _forward_check(self, fila: int, col: int, valor: int) -> tuple[bool, dict]:
        """
        Elimina el valor asignado del dominio de sus vecinos.
        Retorna si la asignacion sigue siendo consistente y un registro
        de cambios para poder deshacerlos en backtracking.
        """
        cambios = {}

        for vecino in self._obtener_vecinos(fila, col):
            if valor not in self.dominios[vecino]:
                continue

            cambios[vecino] = set(self.dominios[vecino])
            self.dominios[vecino].discard(valor)

            if not self.dominios[vecino]:
                return False, cambios

        return True, cambios

    def _restaurar_dominios(self, cambios: dict[tuple[int, int], set[int]]):
        """Revierte los recortes de dominio hechos por forward checking."""
        for variable, dominio in cambios.items():
            self.dominios[variable] = dominio

    def _backtrack(self) -> bool:
        """Backtracking con comprobacion de consistencia hacia adelante."""
        variable = self._seleccionar_variable_no_asignada()

        if variable is None:
            return True

        fila, col = variable
        dominio_actual = sorted(self.dominios[variable])

        for valor in dominio_actual:
            if not self.sudoku.es_valido(fila, col, valor):
                continue

            dominio_original = set(self.dominios[variable])
            self.sudoku.grid[fila][col] = valor
            self.dominios[variable] = {valor}

            consistente, cambios = self._forward_check(fila, col, valor)
            if consistente and self._backtrack():
                return True

            self.sudoku.grid[fila][col] = 0
            self.dominios[variable] = dominio_original
            self._restaurar_dominios(cambios)

        return False
