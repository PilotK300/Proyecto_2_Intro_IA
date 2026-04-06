# ──────────────────────────────────────────────
#  vista/tablero.py
# ──────────────────────────────────────────────
import arcade
from constantes import *


class VistaTablero:

    MARGEN_X   = 40
    MARGEN_Y_INF = 20
    MARGEN_Y_SUP = 70

    def __init__(self, sudoku):
        self.sudoku  = sudoku
        self.estados: dict[tuple, str] = {}

        ax = ANCHO_VENTANA - 2 * self.MARGEN_X
        ay = ALTO_VENTANA  - self.MARGEN_Y_SUP - self.MARGEN_Y_INF

        # Tamaño de celda que cabe en la ventana — sin mínimo artificial
        self.tam_celda = min(ax // sudoku.N, ay // sudoku.N)
        self.tam_celda = max(self.tam_celda, TAM_CELDA_MIN)

        self.tablero_px = self.tam_celda * sudoku.N
        self.ox = (ANCHO_VENTANA - self.tablero_px) // 2
        self.oy = self.MARGEN_Y_INF + self.MARGEN_Y_SUP // 2

        self.font_size = max(5, min(self.tam_celda // 2 - 1, 28))
        self._rebuild_textos()

    def celda_en_px(self, fila, col):
        tc = self.tam_celda
        x  = self.ox + col * tc + tc / 2
        y  = self.oy + (self.sudoku.N - 1 - fila) * tc + tc / 2
        return x, y

    def _rebuild_textos(self):
        self._textos: dict[tuple, arcade.Text] = {}
        for fila in range(self.sudoku.N):
            for col in range(self.sudoku.N):
                valor = self.sudoku.grid[fila][col]
                if valor == 0:
                    continue
                cx, cy = self.celda_en_px(fila, col)
                color  = (
                    COLOR_TEXTO_FIJO
                    if (fila, col) in self.sudoku.fijas
                    else (255, 255, 255)
                )
                self._textos[(fila, col)] = arcade.Text(
                    str(valor), cx, cy, color,
                    font_size=self.font_size,
                    anchor_x="center", anchor_y="center",
                    bold=((fila, col) in self.sudoku.fijas),
                )

    def marcar(self, fila, col, estado):
        self.estados[(fila, col)] = estado

    def limpiar_estado(self, fila, col):
        self.estados.pop((fila, col), None)

    def dibujar(self):
        N  = self.sudoku.N
        k  = self.sudoku.k
        tc = self.tam_celda
        ox = self.ox
        oy = self.oy

        for fila in range(N):
            for col in range(N):
                x = ox + col * tc
                y = oy + (N - 1 - fila) * tc
                estado = self.estados.get((fila, col))
                if (fila, col) in self.sudoku.fijas:
                    color = COLOR_CELDA_FIJA
                elif estado == "asignando":
                    color = (40, 180, 80)
                elif estado == "retroceso":
                    color = (200, 60, 50)
                elif estado == "resuelta":
                    color = (180, 200, 255)
                else:
                    color = COLOR_CELDA_VACIA
                arcade.draw_lrbt_rectangle_filled(x, x + tc, y, y + tc, color)

        for i in range(N + 1):
            gruesa = i % k == 0
            grosor = 3 if gruesa else 1
            color  = COLOR_LINEA_GRUESA if gruesa else COLOR_LINEA_FINA
            yy = oy + i * tc
            arcade.draw_line(ox, yy, ox + N * tc, yy, color, grosor)
            xx = ox + i * tc
            arcade.draw_line(xx, oy, xx, oy + N * tc, color, grosor)

        for txt in self._textos.values():
            txt.draw()
