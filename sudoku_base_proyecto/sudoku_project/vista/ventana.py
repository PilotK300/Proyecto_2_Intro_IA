# ──────────────────────────────────────────────
#  vista/ventana.py
# ──────────────────────────────────────────────
import math
import random
import threading
import arcade
import arcade.gui

from constantes    import *
from modelo.sudoku import Sudoku
from vista.tablero import VistaTablero
from modelo.csp_solver import backtrack, ASIGNANDO, RETROCEDIENDO, SOLUCIONADO


# ── Helper de estilos Arcade 3.x ──────────────────────────────────────

def _estilo(bg, hover, press=None, borde=None, font_size=12,
            font_color=(220, 230, 255)):
    if borde is None:
        borde = tuple(min(255, v + 30) for v in hover)
    if press is None:
        press = tuple(max(0, v - 40) for v in bg)

    def _e(c_bg, c_borde, c_font=font_color):
        return {
            "bg_color":     c_bg,
            "border_color": c_borde,
            "border_width": 2,
            "font_color":   c_font,
            "font_size":    font_size,
        }
    return {
        "normal":   _e(bg,           borde),
        "hover":    _e(hover,         borde),
        "press":    _e(press,  (255, 255, 255)),
        "disabled": _e((45, 45, 55), (70, 70, 80), (120, 120, 130)),
    }


def _dibujar_fondo():
    for i in range(0, ANCHO_VENTANA, 60):
        arcade.draw_line(i, 0, i, ALTO_VENTANA, (20, 22, 35), 1)
    for j in range(0, ALTO_VENTANA, 60):
        arcade.draw_line(0, j, ANCHO_VENTANA, j, (20, 22, 35), 1)


# ══════════════════════════════════════════════
#  PANTALLA 1 – Menú
# ══════════════════════════════════════════════
class PantallaMenu(arcade.View):

    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.tamanio_sel    = "9×9   (k=3)"
        self.dificultad_sel = "Fácil"
        self._construir_ui()

    def _construir_ui(self):
        self.manager.clear()
        cx = ANCHO_VENTANA // 2

        self.manager.add(arcade.gui.UILabel(
            text="SUDOKU CSP", x=cx - 200, y=ALTO_VENTANA - 95,
            width=400, height=55, font_size=38, bold=True,
            text_color=arcade.color.LAVENDER_BLUE, align="center",
        ))
        self.manager.add(arcade.gui.UILabel(
            text="Generador de puzzles", x=cx - 200, y=ALTO_VENTANA - 132,
            width=400, height=26, font_size=13,
            text_color=(140, 150, 200), align="center",
        ))

        # ── Tamaño ───────────────────────────────────────────────────
        y_lbl = ALTO_VENTANA - 195
        self.manager.add(arcade.gui.UILabel(
            text="Tamaño del tablero", x=cx - 220, y=y_lbl,
            width=440, height=22, font_size=13, bold=True,
            text_color=COLOR_TEXTO_UI, align="center",
        ))
        nombres = list(TAMANIOS.keys())
        bw, bh, gap = 148, 36, 10
        for fi, fila_nombres in enumerate([nombres[:5], nombres[5:]]):
            total_w = len(fila_nombres) * bw + (len(fila_nombres) - 1) * gap
            sx      = cx - total_w // 2
            y_btn   = y_lbl - 50 - fi * (bh + 8)
            for i, nombre in enumerate(fila_nombres):
                sel = nombre == self.tamanio_sel
                bg  = (55, 85, 155) if sel else (32, 38, 60)
                btn = arcade.gui.UIFlatButton(
                    text=nombre,
                    x=sx + i * (bw + gap), y=y_btn,
                    width=bw, height=bh,
                    style=_estilo(bg, (75, 110, 190),
                                  press=(20, 50, 110),
                                  borde=(95, 125, 210), font_size=11),
                )
                nc = nombre
                @btn.event("on_click")
                def _t(ev, n=nc):
                    self.tamanio_sel = n
                    self._construir_ui()
                self.manager.add(btn)

        # Aviso
        k_sel = TAMANIOS[self.tamanio_sel]
        if k_sel >= 8:
            aviso, c_av = "⚠ Tableros k≥8 pueden tardar varios segundos", (220, 160, 60)
        elif k_sel >= 6:
            aviso, c_av = "⏳ Tableros k≥6 pueden tardar 1-5 segundos", (180, 180, 80)
        else:
            aviso, c_av = "", (0, 0, 0)
        self.manager.add(arcade.gui.UILabel(
            text=aviso, x=cx - 220, y=y_lbl - 115,
            width=440, height=20, font_size=10,
            text_color=c_av, align="center",
        ))

        # ── Dificultad ───────────────────────────────────────────────
        y2 = y_lbl - 155
        self.manager.add(arcade.gui.UILabel(
            text="Dificultad", x=cx - 220, y=y2,
            width=440, height=22, font_size=13, bold=True,
            text_color=COLOR_TEXTO_UI, align="center",
        ))
        colores = {
            "Fácil":   (35, 155,  75),
            "Medio":   (175, 145,  25),
            "Difícil": (195,  85,  25),
            "Experto": (175,  35,  35),
        }
        difs = list(DIFICULTADES.keys())
        bw2, gap2 = 130, 12
        sx2 = cx - (len(difs) * bw2 + (len(difs) - 1) * gap2) // 2
        for i, nombre in enumerate(difs):
            sel  = nombre == self.dificultad_sel
            base = colores[nombre]
            bg   = base if sel else (32, 38, 60)
            hvr  = tuple(min(255, v + 45) for v in base)
            prs  = tuple(max(0,   v - 45) for v in base)
            btn  = arcade.gui.UIFlatButton(
                text=nombre,
                x=sx2 + i * (bw2 + gap2), y=y2 - 52,
                width=bw2, height=38,
                style=_estilo(bg, hvr, press=prs, borde=base),
            )
            nc = nombre
            @btn.event("on_click")
            def _d(ev, n=nc):
                self.dificultad_sel = n
                self._construir_ui()
            self.manager.add(btn)

        pmin, pmax = DIFICULTADES[self.dificultad_sel]
        self.manager.add(arcade.gui.UILabel(
            text=f"Celdas visibles: {int(pmin*100)}% – {int(pmax*100)}% del tablero",
            x=cx - 220, y=y2 - 88,
            width=440, height=20, font_size=11,
            text_color=(155, 165, 195), align="center",
        ))

        btn_gen = arcade.gui.UIFlatButton(
            text="▶  GENERAR PUZZLE",
            x=cx - 125, y=55, width=250, height=52,
            style=_estilo(
                (35, 155, 75), (55, 195, 95),
                press=(10, 100, 45), borde=(75, 215, 115),
                font_size=17, font_color=(255, 255, 255),
            ),
        )
        @btn_gen.event("on_click")
        def _g(ev):
            self._ir_a_carga()
        self.manager.add(btn_gen)

    def _ir_a_carga(self):
        k          = TAMANIOS[self.tamanio_sel]
        pmin, pmax = DIFICULTADES[self.dificultad_sel]
        self.window.show_view(
            PantallaCargando(k, random.uniform(pmin, pmax), self.dificultad_sel)
        )

    def on_show_view(self):
        arcade.set_background_color(COLOR_FONDO)

    def on_draw(self):
        self.clear()
        _dibujar_fondo()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()


# ══════════════════════════════════════════════
#  PANTALLA 1.5 – Cargando
# ══════════════════════════════════════════════
class PantallaCargando(arcade.View):

    def __init__(self, k: int, porcentaje: float, nombre_dif: str):
        super().__init__()
        self._k          = k
        self._porcentaje = porcentaje
        self._nombre_dif = nombre_dif
        self._sudoku     = None
        self._listo      = False
        self._angulo     = 0.0

        cx, cy = ANCHO_VENTANA // 2, ALTO_VENTANA // 2
        self._txt1 = arcade.Text(
            "Generando puzzle\u2026", cx, cy - 70,
            COLOR_TEXTO_UI, font_size=16,
            anchor_x="center", anchor_y="center",
        )
        self._txt2 = arcade.Text(
            f"Tablero {k**2}\xd7{k**2}", cx, cy - 98,
            (140, 150, 190), font_size=12,
            anchor_x="center", anchor_y="center",
        )
        threading.Thread(target=self._generar, daemon=True).start()

    def _generar(self):
        s = Sudoku(self._k)
        s.generar(self._porcentaje)
        self._sudoku = s
        self._listo  = True

    def on_update(self, dt):
        self._angulo = (self._angulo + 180 * dt) % 360
        if self._listo:
            self.window.show_view(
                PantallaPuzzle(self._sudoku, self._porcentaje, self._nombre_dif)
            )

    def on_draw(self):
        self.clear()
        _dibujar_fondo()
        cx, cy = ANCHO_VENTANA // 2, ALTO_VENTANA // 2
        for i in range(24):
            a1    = math.radians(self._angulo + i * 15)
            a2    = math.radians(self._angulo + i * 15 + 10.8)
            alpha = int(255 * i / 24)
            arcade.draw_arc_outline(
                cx, cy, 76, 76,
                (80 + alpha // 2, 120 + alpha // 3, 220),
                math.degrees(a1), math.degrees(a2),
                border_width=5,
            )
        self._txt1.draw()
        self._txt2.draw()


# ══════════════════════════════════════════════
#  PANTALLA 2 – Puzzle + zoom con scroll
# ══════════════════════════════════════════════
class PantallaPuzzle(arcade.View):

    ZOOM_MAX = 5.0
    ZOOM_VEL = 0.15

    def __init__(self, sudoku: Sudoku, porcentaje: float, nombre_dif: str):
        super().__init__()
        self._sudoku     = sudoku
        self._porcentaje = porcentaje
        self._nombre_dif = nombre_dif

        self.vista_tablero = VistaTablero(sudoku)

        # Guarda el algoritmo (variable del agente)
        self._solver = None

        # Zoom inicial: el que hace que el tablero llene la ventana
        tc = self.vista_tablero.tam_celda
        N  = sudoku.N
        zoom_fit = min(
            (ANCHO_VENTANA - 80) / (tc * N),
            (ALTO_VENTANA  - 90) / (tc * N),
        )
        self._zoom_min = round(max(0.3, zoom_fit), 3)
        self._zoom     = 1.0   # siempre arranca en 1:1

        self._camara       = arcade.Camera2D()
        self._camara.zoom  = self._zoom

        # Estado del drag (click + arrastrar para mover)
        self._drag_activo = False
        self._drag_inicio = (0, 0)
        self._pos_camara  = (0.0, 0.0)

        # Info
        vacias = len(sudoku.celdas_vacias())
        fijas  = sudoku.N ** 2 - vacias
        self._txt_info = arcade.Text(
            f"{sudoku.N}×{sudoku.N}  ·  {nombre_dif}  ·  "
            f"{fijas} pistas  ·  {vacias} vacías  ·  🖱 scroll = zoom",
            ANCHO_VENTANA // 2, ALTO_VENTANA - 22,
            COLOR_TEXTO_UI, font_size=11,
            anchor_x="center", anchor_y="center",
        )

        # Botones
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        estilo_nav = _estilo(
            (32, 38, 60), (52, 60, 100),
            press=(15, 20, 50), borde=(78, 90, 145),
        )
        btn_v = arcade.gui.UIFlatButton(
            text="← Menú", x=10, y=ALTO_VENTANA - 44,
            width=90, height=34, style=estilo_nav,
        )
        @btn_v.event("on_click")
        def _volver(ev):
            self.manager.disable()
            self.window.show_view(PantallaMenu())
        self.manager.add(btn_v)

        btn_n = arcade.gui.UIFlatButton(
            text="↺ Nuevo", x=ANCHO_VENTANA - 105, y=ALTO_VENTANA - 44,
            width=95, height=34, style=estilo_nav,
        )
        @btn_n.event("on_click")
        def _nuevo(ev):
            self.manager.disable()
            p = random.uniform(*DIFICULTADES[self._nombre_dif])
            self.window.show_view(
                PantallaCargando(self._sudoku.k, p, self._nombre_dif)
            )
        self.manager.add(btn_n)

        """
        btn_resolver = arcade.gui.UIFlatButton(
            text="Resolver",
            x=ANCHO_VENTANA // 2 - 60,
            y=20,
            width=120,
            height=40,
        )
        """
        btn_fb = arcade.gui.UIFlatButton(
            text="Fuerza Bruta",
            x=ANCHO_VENTANA // 2 - 140,
            y=20,
            width=120,
            height=40,
         )
        #Botón para resolver con fuerza bruta
        @btn_fb.event("on_click")
        def _resolver_fb(ev):
            print("Usando Fuerza Bruta")
            from modelo.fuerza_bruta import solve_sudoku_FB
            solve_sudoku_FB(self._sudoku)
            self.vista_tablero._rebuild_textos()

        self.manager.add(btn_fb)

        btn_bt = arcade.gui.UIFlatButton(
            text="Backtracking",
            x=ANCHO_VENTANA // 2 + 20,
            y=20,
            width=140,
            height=40,
        )

        @btn_bt.event("on_click")
        def _resolver_bt(ev):
            print("Usando Backtracking")
            vacias = self._sudoku.celdas_vacias()
            self._solver = backtrack(self._sudoku, vacias)

        self.manager.add(btn_bt)


        """
        @btn_resolver.event("on_click")
        def _resolver(ev):
            vacias = self._sudoku.celdas_vacias()
            self._solver = backtrack(self._sudoku, vacias)

        self.manager.add(btn_resolver)

        """
    def on_update(self, dt):
        if self._solver:
            try:
                evento = next(self._solver)

                if evento[0] == ASIGNANDO:
                    _, f, c, v = evento
                    self.vista_tablero.marcar(f, c, "asignando")
                    self.vista_tablero._rebuild_textos()

                elif evento[0] == RETROCEDIENDO:
                    _, f, c = evento
                    self.vista_tablero.marcar(f, c, "retroceso")

                elif evento[0] == SOLUCIONADO:
                    print("Sudoku resuelto")
                    self._solver = None

            except StopIteration:
                self._solver = None

        # ── zoom ─────────────────────────────────────────────────────────

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self._zoom = max(
            self._zoom_min,
            min(self.ZOOM_MAX, self._zoom + scroll_y * self.ZOOM_VEL)
        )
        self._camara.zoom = self._zoom

    # ── drag para mover ──────────────────────────────────────────────

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._drag_activo = True
            self._drag_inicio = (x, y)
            self._pos_camara  = tuple(self._camara.position)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._drag_activo = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self._drag_activo:
            return
        ix, iy   = self._drag_inicio
        cx, cy   = self._pos_camara
        # Dividir por zoom para que el arrastre sea 1:1 con el cursor
        self._camara.position = (
            cx - (x - ix) / self._zoom,
            cy - (y - iy) / self._zoom,
        )

    # ── dibujo ────────────────────────────────────────────────────────

    def on_show_view(self):
        arcade.set_background_color(COLOR_FONDO)

    def on_draw(self):
        self.clear()
        _dibujar_fondo()

        with self._camara.activate():
            self.vista_tablero.dibujar()

        self._txt_info.draw()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()
