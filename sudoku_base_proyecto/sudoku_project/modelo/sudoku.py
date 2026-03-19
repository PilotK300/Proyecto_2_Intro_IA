# ──────────────────────────────────────────────
#  modelo/sudoku.py
#  Optimizaciones:
#    1. Bloques diagonales
#    2. AC-3 una vez
#    3. Naked pairs/triples
#    4. MRV + Forward Checking
#    5. Bitmask para candidatos
#    6. Backtracking ITERATIVO (sin recursión → sin RecursionError)
# ──────────────────────────────────────────────
import random
from collections import deque
from itertools import combinations
import sys

# Aumentar límite solo como seguridad extra, pero el backtracking
# ya es iterativo y no lo necesita
sys.setrecursionlimit(10000)


# ── utilidades bitmask ────────────────────────────────────────────────

def _contar(mask: int) -> int:
    return bin(mask).count('1')

def _valores(mask: int) -> list[int]:
    vals = []
    m = mask
    while m:
        lsb = m & (-m)
        vals.append(lsb.bit_length())
        m &= m - 1
    return vals

def _unico(mask: int) -> int:
    return mask.bit_length()


class Sudoku:

    def __init__(self, k: int):
        self.k = k
        self.N = k * k
        self.grid:  list[list[int]]      = [[0] * self.N for _ in range(self.N)]
        self.fijas: set[tuple[int, int]] = set()
        self._peers      = self._construir_peers()
        self._grupos     = self._construir_grupos()
        self._todos_mask = (1 << (self.N + 1)) - 2  # bits 1..N

    # ── peers y grupos ────────────────────────────────────────────────

    def _construir_peers(self):
        N, k = self.N, self.k
        peers = [[[] for _ in range(N)] for _ in range(N)]
        for r in range(N):
            for c in range(N):
                sr, sc = (r // k) * k, (c // k) * k
                visto = set()
                for x in range(N):
                    if x != c: visto.add((r, x))
                    if x != r: visto.add((x, c))
                for br in range(sr, sr + k):
                    for bc in range(sc, sc + k):
                        if (br, bc) != (r, c):
                            visto.add((br, bc))
                peers[r][c] = list(visto)
        return peers

    def _construir_grupos(self):
        N, k = self.N, self.k
        grupos = []
        for r in range(N):
            grupos.append([(r, c) for c in range(N)])
        for c in range(N):
            grupos.append([(r, c) for r in range(N)])
        for br in range(0, N, k):
            for bc in range(0, N, k):
                grupos.append([
                    (br + dr, bc + dc)
                    for dr in range(k) for dc in range(k)
                ])
        return grupos

    # ── candidatos iniciales ──────────────────────────────────────────

    def _candidatos_iniciales(self) -> list[list[int]]:
        cands = [[self._todos_mask] * self.N for _ in range(self.N)]
        for r in range(self.N):
            for c in range(self.N):
                if self.grid[r][c] != 0:
                    cands[r][c] = 0
                    bit = 1 << self.grid[r][c]
                    for pr, pc in self._peers[r][c]:
                        cands[pr][pc] &= ~bit
        return cands

    # ── AC-3 ─────────────────────────────────────────────────────────

    def _ac3(self, cands: list[list[int]]) -> bool:
        cola = deque(
            (r, c)
            for r in range(self.N)
            for c in range(self.N)
            if self.grid[r][c] == 0 and _contar(cands[r][c]) == 1
        )
        while cola:
            r, c = cola.popleft()
            if self.grid[r][c] != 0 or _contar(cands[r][c]) != 1:
                continue
            valor           = _unico(cands[r][c])
            self.grid[r][c] = valor
            bit             = 1 << valor
            cands[r][c]     = 0
            for pr, pc in self._peers[r][c]:
                if not (cands[pr][pc] & bit):
                    continue
                cands[pr][pc] &= ~bit
                if self.grid[pr][pc] != 0:
                    continue
                if cands[pr][pc] == 0:
                    return False
                if _contar(cands[pr][pc]) == 1:
                    cola.append((pr, pc))
        return True

    # ── Naked pairs / triples ─────────────────────────────────────────

    def _naked_subsets(self, cands: list[list[int]]) -> int:
        """
        Retorna: -1 contradicción | 0 sin cambios | 1 hubo cambios
        """
        cambio = False
        for grupo in self._grupos:
            vacias = [
                (r, c) for r, c in grupo
                if self.grid[r][c] == 0 and cands[r][c] != 0
            ]
            for size in (2, 3):
                if len(vacias) < size:
                    continue
                for subset in combinations(vacias, size):
                    union_mask = 0
                    for r, c in subset:
                        union_mask |= cands[r][c]
                    if _contar(union_mask) != size:
                        continue
                    for r, c in vacias:
                        if (r, c) in subset:
                            continue
                        antes = cands[r][c]
                        cands[r][c] &= ~union_mask
                        if cands[r][c] != antes:
                            cambio = True
                        if cands[r][c] == 0 and self.grid[r][c] == 0:
                            return -1
        return 1 if cambio else 0

    # ── Forward Checking ──────────────────────────────────────────────

    def _forward_check(self, cands, fila, col) -> bool:
        for pr, pc in self._peers[fila][col]:
            if self.grid[pr][pc] == 0 and cands[pr][pc] == 0:
                return False
        return True

    # ── Selección MRV ────────────────────────────────────────────────

    def _mrv(self, cands) -> tuple | None:
        """Devuelve la celda vacía con menos candidatos, o None si completo."""
        mejor   = None
        mejor_n = self.N + 1
        for r in range(self.N):
            for c in range(self.N):
                if self.grid[r][c] == 0:
                    n = _contar(cands[r][c])
                    if n == 0:
                        return (-1, -1)   # señal de contradicción
                    if n < mejor_n:
                        mejor_n = n
                        mejor   = (r, c)
                        if n == 1:
                            break
            if mejor_n == 1:
                break
        return mejor  # None = completo

    # ── Backtracking ITERATIVO ────────────────────────────────────────

    def _backtrack_iterativo(self, cands: list[list[int]]) -> bool:
        """
        Backtracking sin recursión.
        Usa una pila explícita de estados:
          cada frame = (fila, col, valores_restantes, snap_cands, snap_grid)
        """

        def snapshot(r, c):
            coords = set(self._peers[r][c])
            coords.add((r, c))
            return (
                {(cr, cc): cands[cr][cc]     for cr, cc in coords},
                {(cr, cc): self.grid[cr][cc] for cr, cc in coords},
            )

        def restaurar(sc, sg):
            for (r, c), val in sc.items():
                cands[r][c]     = val
                self.grid[r][c] = sg[(r, c)]

        pila = []  # stack de frames

        while True:
            # Elegir siguiente celda con MRV
            celda = self._mrv(cands)

            if celda is None:
                # Tablero completo
                return True

            if celda == (-1, -1):
                # Contradicción en este nivel → retroceder
                if not pila:
                    return False
                fila, col, valores_rest, sc, sg = pila.pop()
                restaurar(sc, sg)
                # Continuar con los valores restantes del frame anterior
                celda    = (fila, col)
                sc_nuevo, sg_nuevo = snapshot(fila, col)
            else:
                fila, col = celda
                valores   = _valores(cands[fila][col])
                random.shuffle(valores)
                valores_rest = valores
                sc_nuevo, sg_nuevo = snapshot(fila, col)

            # Intentar valores de este nivel
            avanzado = False
            while valores_rest:
                v = valores_rest.pop(0)

                restaurar(sc_nuevo, sg_nuevo)
                sc_nuevo, sg_nuevo = snapshot(fila, col)

                # Asignar v
                self.grid[fila][col] = v
                bit = 1 << v
                for pr, pc in self._peers[fila][col]:
                    cands[pr][pc] &= ~bit
                cands[fila][col] = 0

                # Forward check
                if self._forward_check(cands, fila, col):
                    # Empujar frame con los valores restantes y bajar
                    pila.append((fila, col, valores_rest, sc_nuevo, sg_nuevo))
                    avanzado = True
                    break
                # Si forward check falla, restaurar y probar siguiente v
                restaurar(sc_nuevo, sg_nuevo)
                sc_nuevo, sg_nuevo = snapshot(fila, col)

            if not avanzado:
                # Agotamos todos los valores de este nivel → retroceder
                if not pila:
                    return False
                fila, col, valores_rest, sc, sg = pila.pop()
                restaurar(sc, sg)
                # Reinsertar en pila para que el while externo lo procese
                # con los valores restantes
                pila.append((fila, col, valores_rest, snapshot(fila, col)[0], snapshot(fila, col)[1]))

    # ── bloques diagonales ────────────────────────────────────────────

    def _llenar_diagonal(self):
        for b in range(self.k):
            valores = list(range(1, self.N + 1))
            random.shuffle(valores)
            sr, sc = b * self.k, b * self.k
            idx = 0
            for r in range(sr, sr + self.k):
                for c in range(sc, sc + self.k):
                    self.grid[r][c] = valores[idx]
                    idx += 1

    # ── API pública ───────────────────────────────────────────────────

    def generar(self, porcentaje_visible: float):
        while True:
            self.grid = [[0] * self.N for _ in range(self.N)]

            # 1. Bloques diagonales
            self._llenar_diagonal()

            # 2. AC-3 + Naked pairs en bucle
            cands = self._candidatos_iniciales()
            ok = True
            while True:
                if not self._ac3(cands):
                    ok = False; break
                res = self._naked_subsets(cands)
                if res == -1:
                    ok = False; break
                if res == 0:
                    break   # estabilizado

            if not ok:
                continue

            # 3. Backtracking iterativo
            if not self._backtrack_iterativo(cands):
                continue

            break  # éxito

        # 4. Eliminar celdas
        total      = self.N * self.N
        celdas_vis = round(total * porcentaje_visible)
        celdas_vis = max(celdas_vis, round(total * 0.17))
        a_eliminar = total - celdas_vis

        posiciones = [(r, c) for r in range(self.N) for c in range(self.N)]
        random.shuffle(posiciones)
        for r, c in posiciones[:a_eliminar]:
            self.grid[r][c] = 0

        self.fijas = {
            (r, c)
            for r in range(self.N)
            for c in range(self.N)
            if self.grid[r][c] != 0
        }

    def celdas_vacias(self) -> list[tuple[int, int]]:
        return [
            (r, c)
            for r in range(self.N)
            for c in range(self.N)
            if self.grid[r][c] == 0
        ]
