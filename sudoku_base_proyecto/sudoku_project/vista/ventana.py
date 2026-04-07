import math
import random
import threading
import copy
import arcade
import arcade.gui

from constantes import *
from modelo.csp_solver import solve_sudoku_BT
from modelo.forward_checking_solver import ForwardCheckingSolver
from modelo.sudoku import Sudoku
from modelo.fuerza_bruta_metricas import solve_sudoku_FB_metricas, FuerzaBrutaResultado
from vista.tablero import VistaTablero
from vista.animadores import (
    ASIGNANDO,
    PODANDO,
    RETROCEDIENDO,
    SOLUCIONADO,
    animar_backtracking,
    animar_forward_checking,
)


def _estilo(bg, hover, press=None, borde=None, font_size=12,
            font_color=(220, 230, 255)):
    if borde is None:
        borde = tuple(min(255, v + 30) for v in hover)
    if press is None:
        press = tuple(max(0, v - 40) for v in bg)

    def _e(c_bg, c_borde, c_font=font_color):
        return {
            "bg_color": c_bg,
            "border_color": c_borde,
            "border_width": 2,
            "font_color": c_font,
            "font_size": font_size,
        }

    return {
        "normal": _e(bg, borde),
        "hover": _e(hover, borde),
        "press": _e(press, (255, 255, 255)),
        "disabled": _e((45, 45, 55), (70, 70, 80), (120, 120, 130)),
    }


def _dibujar_fondo():
    for i in range(0, ANCHO_VENTANA, 60):
        arcade.draw_line(i, 0, i, ALTO_VENTANA, (20, 22, 35), 1)
    for j in range(0, ALTO_VENTANA, 60):
        arcade.draw_line(0, j, ANCHO_VENTANA, j, (20, 22, 35), 1)


TABLERO_EJEMPLO_LAB_9X9 = [
    [0, 0, 3, 0, 2, 0, 6, 0, 0],
    [9, 0, 0, 3, 0, 5, 0, 0, 1],
    [0, 0, 1, 8, 0, 6, 4, 0, 0],
    [0, 0, 8, 1, 0, 2, 9, 0, 0],
    [7, 0, 0, 0, 0, 0, 0, 0, 8],
    [0, 0, 6, 7, 0, 8, 2, 0, 0],
    [0, 0, 2, 6, 0, 9, 5, 0, 0],
    [8, 0, 0, 2, 0, 3, 0, 0, 9],
    [0, 0, 5, 0, 1, 0, 3, 0, 0],
]


class PantallaMenu(arcade.View):

    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.tamanio_sel = list(TAMANIOS.keys())[1]
        self.dificultad_sel = list(DIFICULTADES.keys())[0]
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

        y_lbl = ALTO_VENTANA - 195
        self.manager.add(arcade.gui.UILabel(
            text="Tamano del tablero", x=cx - 220, y=y_lbl,
            width=440, height=22, font_size=13, bold=True,
            text_color=COLOR_TEXTO_UI, align="center",
        ))
        nombres = list(TAMANIOS.keys())
        bw, bh, gap = 148, 36, 10
        for fi, fila_nombres in enumerate([nombres[:5], nombres[5:]]):
            total_w = len(fila_nombres) * bw + (len(fila_nombres) - 1) * gap
            sx = cx - total_w // 2
            y_btn = y_lbl - 50 - fi * (bh + 8)
            for i, nombre in enumerate(fila_nombres):
                sel = nombre == self.tamanio_sel
                bg = (55, 85, 155) if sel else (32, 38, 60)
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

        k_sel = TAMANIOS[self.tamanio_sel]
        if k_sel >= 8:
            aviso, c_av = "Tableros k>=8 pueden tardar varios segundos", (220, 160, 60)
        elif k_sel >= 6:
            aviso, c_av = "Tableros k>=6 pueden tardar 1-5 segundos", (180, 180, 80)
        else:
            aviso, c_av = "", (0, 0, 0)
        self.manager.add(arcade.gui.UILabel(
            text=aviso, x=cx - 220, y=y_lbl - 115,
            width=440, height=20, font_size=10,
            text_color=c_av, align="center",
        ))

        y2 = y_lbl - 155
        self.manager.add(arcade.gui.UILabel(
            text="Dificultad", x=cx - 220, y=y2,
            width=440, height=22, font_size=13, bold=True,
            text_color=COLOR_TEXTO_UI, align="center",
        ))
        difs = list(DIFICULTADES.keys())
        paleta = [
            (35, 155, 75),
            (175, 145, 25),
            (195, 85, 25),
            (175, 35, 35),
        ]
        colores = {nombre: paleta[i] for i, nombre in enumerate(difs)}
        bw2, gap2 = 130, 12
        sx2 = cx - (len(difs) * bw2 + (len(difs) - 1) * gap2) // 2
        for i, nombre in enumerate(difs):
            sel = nombre == self.dificultad_sel
            base = colores[nombre]
            bg = base if sel else (32, 38, 60)
            hvr = tuple(min(255, v + 45) for v in base)
            prs = tuple(max(0, v - 45) for v in base)
            btn = arcade.gui.UIFlatButton(
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
            text=f"Celdas visibles: {int(pmin * 100)}% - {int(pmax * 100)}% del tablero",
            x=cx - 220, y=y2 - 88,
            width=440, height=20, font_size=11,
            text_color=(155, 165, 195), align="center",
        ))

        btn_gen = arcade.gui.UIFlatButton(
            text="GENERAR PUZZLE",
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

        if TAMANIOS[self.tamanio_sel] == 3:
            btn_lab = arcade.gui.UIFlatButton(
                text="TABLERO EJEMPLO LABORATORIO",
                x=cx - 155, y=118, width=310, height=40,
                style=_estilo(
                    (210, 210, 210), (240, 240, 240),
                    press=(180, 180, 180), borde=(120, 120, 120),
                    font_size=13, font_color=(0, 0, 0),
                ),
            )

            @btn_lab.event("on_click")
            def _lab(ev):
                self._abrir_tablero_laboratorio()

            self.manager.add(btn_lab)

    def _ir_a_carga(self):
        k = TAMANIOS[self.tamanio_sel]
        pmin, pmax = DIFICULTADES[self.dificultad_sel]
        self.window.show_view(
            PantallaCargando(k, random.uniform(pmin, pmax), self.dificultad_sel)
        )

    def _abrir_tablero_laboratorio(self):
        sudoku = Sudoku(3)
        sudoku.grid = [fila[:] for fila in TABLERO_EJEMPLO_LAB_9X9]
        sudoku.fijas = {
            (fila, col)
            for fila in range(sudoku.N)
            for col in range(sudoku.N)
            if sudoku.grid[fila][col] != 0
        }
        self.window.show_view(PantallaPuzzle(sudoku, 0.0, "Tablero ejemplo laboratorio"))

    def on_show_view(self):
        arcade.set_background_color(COLOR_FONDO)

    def on_draw(self):
        self.clear()
        _dibujar_fondo()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()


class PantallaCargando(arcade.View):

    def __init__(self, k: int, porcentaje: float, nombre_dif: str):
        super().__init__()
        self._k = k
        self._porcentaje = porcentaje
        self._nombre_dif = nombre_dif
        self._sudoku = None
        self._listo = False
        self._angulo = 0.0

        cx, cy = ANCHO_VENTANA // 2, ALTO_VENTANA // 2
        self._txt1 = arcade.Text(
            "Generando puzzle...", cx, cy - 70,
            COLOR_TEXTO_UI, font_size=16,
            anchor_x="center", anchor_y="center",
        )
        self._txt2 = arcade.Text(
            f"Tablero {k**2}x{k**2}", cx, cy - 98,
            (140, 150, 190), font_size=12,
            anchor_x="center", anchor_y="center",
        )
        threading.Thread(target=self._generar, daemon=True).start()

    def _generar(self):
        s = Sudoku(self._k)
        s.generar(self._porcentaje)
        self._sudoku = s
        self._listo = True

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
            a1 = math.radians(self._angulo + i * 15)
            a2 = math.radians(self._angulo + i * 15 + 10.8)
            alpha = int(255 * i / 24)
            arcade.draw_arc_outline(
                cx, cy, 76, 76,
                (80 + alpha // 2, 120 + alpha // 3, 220),
                math.degrees(a1), math.degrees(a2),
                border_width=5,
            )
        self._txt1.draw()
        self._txt2.draw()


class PantallaPuzzle(arcade.View):

    ZOOM_MAX = 5.0
    ZOOM_VEL = 0.15

    def __init__(self, sudoku: Sudoku, porcentaje: float, nombre_dif: str):
        super().__init__()
        self._sudoku = sudoku
        self._porcentaje = porcentaje
        self._nombre_dif = nombre_dif

        self.vista_tablero = VistaTablero(sudoku)
        self._grid_inicial = [fila[:] for fila in sudoku.grid]
        self._solver = None
        self._tiempo_paso = 0.0
        self._intervalo_paso = 0.08
        self._fb_en_ejecucion = False
        self._fb_resultado: FuerzaBrutaResultado | None = None
        self._fb_resultado_pendiente: FuerzaBrutaResultado | None = None
        self._solver_resultado_pendiente = None
        self._estado_resolucion = ""
        self._mostrar_grafica_fb = False

        tc = self.vista_tablero.tam_celda
        N = sudoku.N
        zoom_fit = min(
            (ANCHO_VENTANA - 80) / (tc * N),
            (ALTO_VENTANA - 150) / (tc * N),
        )
        self._zoom_min = round(max(0.3, zoom_fit), 3)
        self._zoom = 1.0

        self._camara = arcade.Camera2D()
        self._camara.zoom = self._zoom

        self._drag_activo = False
        self._drag_inicio = (0, 0)
        self._pos_camara = (0.0, 0.0)

        vacias = len(sudoku.celdas_vacias())
        fijas = sudoku.N ** 2 - vacias
        self._txt_info = arcade.Text(
            f"{sudoku.N}x{sudoku.N}  ·  {nombre_dif}  ·  {fijas} pistas  ·  {vacias} vacias  ·  scroll = zoom",
            ANCHO_VENTANA // 2,
            ALTO_VENTANA - 82,
            COLOR_TEXTO_UI,
            font_size=11,
            anchor_x="center",
            anchor_y="center",
        )

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        estilo_nav = _estilo(
            (32, 38, 60), (52, 60, 100),
            press=(15, 20, 50), borde=(78, 90, 145),
        )

        btn_v = arcade.gui.UIFlatButton(
            text="<- Menu", x=10, y=ALTO_VENTANA - 44,
            width=90, height=34, style=estilo_nav,
        )

        @btn_v.event("on_click")
        def _volver(ev):
            self.manager.disable()
            self.window.show_view(PantallaMenu())

        self.manager.add(btn_v)

        btn_n = arcade.gui.UIFlatButton(
            text="Nuevo", x=ANCHO_VENTANA - 105, y=ALTO_VENTANA - 44,
            width=95, height=34, style=estilo_nav,
        )

        @btn_n.event("on_click")
        def _nuevo(ev):
            self.manager.disable()
            p = random.uniform(*DIFICULTADES[self._nombre_dif])
            self.window.show_view(PantallaCargando(self._sudoku.k, p, self._nombre_dif))

        self.manager.add(btn_n)

        btn_fb = arcade.gui.UIFlatButton(
            text="Fuerza Bruta",
            x=ANCHO_VENTANA // 2 - 220,
            y=ALTO_VENTANA - 44,
            width=120,
            height=34,
            style=estilo_nav,
        )

        @btn_fb.event("on_click")
        def _resolver_fb(ev):
            self._iniciar_fuerza_bruta()

        self.manager.add(btn_fb)

        btn_bt = arcade.gui.UIFlatButton(
            text="Backtracking",
            x=ANCHO_VENTANA // 2 - 90,
            y=ALTO_VENTANA - 44,
            width=140,
            height=34,
            style=estilo_nav,
        )

        @btn_bt.event("on_click")
        def _resolver_bt(ev):
            if self._usa_animacion():
                self._iniciar_animacion(animar_backtracking)
            else:
                self._mostrar_estimativo_backtracking()

        self.manager.add(btn_bt)

        btn_fc = arcade.gui.UIFlatButton(
            text="Forward Checking",
            x=ANCHO_VENTANA // 2 + 60,
            y=ALTO_VENTANA - 44,
            width=170,
            height=34,
            style=estilo_nav,
        )

        @btn_fc.event("on_click")
        def _resolver_fc(ev):
            if self._usa_animacion():
                self._iniciar_animacion(animar_forward_checking)
            elif self._sudoku.N >= 25:
                self._mostrar_estimativo_forward_checking()
            else:
                self._iniciar_solver_directo("forward checking")

        self.manager.add(btn_fc)

    def _restaurar_puzzle(self):
        self._sudoku.grid = [fila[:] for fila in self._grid_inicial]
        self.vista_tablero.limpiar_estados()
        self.vista_tablero._rebuild_textos()

    def _usa_animacion(self) -> bool:
        return self._sudoku.N < 16

    def _max_intentos_fuerza_bruta(self) -> int:
        if self._sudoku.N == 4:
            return 2000
        if self._sudoku.N == 9:
            return 5000
        if self._sudoku.N == 16:
            return 500
        if self._sudoku.N == 25:
            return 200
        return 200

    def _estimativo_backtracking(self) -> str:
        if self._sudoku.N == 16:
            return "Estimado Backtracking 16x16: entre 5 y 30 segundos"
        if self._sudoku.N == 25:
            return "Estimado Backtracking 25x25: decenas de segundos o varios minutos"
        return (
            f"Estimado Backtracking {self._sudoku.N}x{self._sudoku.N}: "
            "tiempo muy alto, no recomendado"
        )

    def _estimativo_forward_checking(self) -> str:
        if self._sudoku.N == 25:
            return "Estimado Forward Checking 25x25: varios segundos"
        return (
            f"Estimado Forward Checking {self._sudoku.N}x{self._sudoku.N}: "
            "tiempo alto, no se ejecuta para ahorrar recursos"
        )

    def _limpiar_estado_solver(self):
        self._estado_resolucion = ""
        self._mostrar_grafica_fb = False
        self._fb_resultado = None
        self._fb_resultado_pendiente = None
        self._solver_resultado_pendiente = None
        self._fb_en_ejecucion = False

    def _iniciar_animacion(self, solver_factory):
        self._restaurar_puzzle()
        self._limpiar_estado_solver()
        self._solver = solver_factory(self._sudoku)
        self._tiempo_paso = 0.0

    def _resolver_fuerza_bruta_worker(self, sudoku_copia: Sudoku, max_intentos: int):
        self._fb_resultado_pendiente = solve_sudoku_FB_metricas(sudoku_copia, max_intentos=max_intentos)

    def _resolver_directo_worker(self, sudoku_copia: Sudoku, algoritmo: str):
        if algoritmo == "backtracking":
            resuelto = solve_sudoku_BT(sudoku_copia)
        else:
            resuelto = ForwardCheckingSolver(sudoku_copia).resolver()
        self._solver_resultado_pendiente = (algoritmo, resuelto, copy.deepcopy(sudoku_copia.grid))

    def _iniciar_fuerza_bruta(self):
        self._restaurar_puzzle()
        self._solver = None
        self._limpiar_estado_solver()
        self._fb_en_ejecucion = True
        max_intentos = self._max_intentos_fuerza_bruta()
        self._estado_resolucion = f"Ejecutando fuerza bruta ({max_intentos} intentos maximo)..."

        sudoku_copia = Sudoku(self._sudoku.k)
        sudoku_copia.grid = copy.deepcopy(self._grid_inicial)
        sudoku_copia.fijas = set(self._sudoku.fijas)

        hilo = threading.Thread(
            target=self._resolver_fuerza_bruta_worker,
            args=(sudoku_copia, max_intentos),
            daemon=True,
        )
        hilo.start()

    def _iniciar_solver_directo(self, algoritmo: str):
        self._restaurar_puzzle()
        self._solver = None
        self._limpiar_estado_solver()
        self._estado_resolucion = f"Ejecutando {algoritmo}..."

        sudoku_copia = Sudoku(self._sudoku.k)
        sudoku_copia.grid = copy.deepcopy(self._grid_inicial)
        sudoku_copia.fijas = set(self._sudoku.fijas)

        hilo = threading.Thread(
            target=self._resolver_directo_worker,
            args=(sudoku_copia, algoritmo),
            daemon=True,
        )
        hilo.start()

    def _mostrar_estimativo_backtracking(self):
        self._restaurar_puzzle()
        self._solver = None
        self._limpiar_estado_solver()
        self._estado_resolucion = self._estimativo_backtracking()

    def _mostrar_estimativo_forward_checking(self):
        self._restaurar_puzzle()
        self._solver = None
        self._limpiar_estado_solver()
        self._estado_resolucion = self._estimativo_forward_checking()

    def _aplicar_resultado_fuerza_bruta(self, resultado: FuerzaBrutaResultado):
        self._fb_en_ejecucion = False
        self._fb_resultado = resultado
        self._fb_resultado_pendiente = None
        self.vista_tablero.limpiar_estados()

        if resultado.resuelto:
            self._sudoku.grid = copy.deepcopy(resultado.grid_final)
            self._mostrar_grafica_fb = False
            self._estado_resolucion = (
                f"Resuelto en {resultado.intentos_usados} intentos y "
                f"{resultado.tiempo_total:.3f} s"
            )
            for fila in range(self._sudoku.N):
                for col in range(self._sudoku.N):
                    if (fila, col) not in self._sudoku.fijas and self._sudoku.grid[fila][col] != 0:
                        self.vista_tablero.marcar(fila, col, "resuelta")
        else:
            self._restaurar_puzzle()
            self._mostrar_grafica_fb = True
            self._estado_resolucion = (
                f"No se pudo resolver. Intentos: {resultado.intentos_usados}  ·  "
                f"Tiempo: {resultado.tiempo_total:.3f} s"
            )

        self.vista_tablero._rebuild_textos()

    def _aplicar_resultado_solver_directo(self, algoritmo: str, resuelto: bool, grid_final: list[list[int]]):
        self._solver_resultado_pendiente = None
        self.vista_tablero.limpiar_estados()

        if resuelto:
            self._sudoku.grid = copy.deepcopy(grid_final)
            self._estado_resolucion = f"{algoritmo.title()} resuelto"
            for fila in range(self._sudoku.N):
                for col in range(self._sudoku.N):
                    if (fila, col) not in self._sudoku.fijas and self._sudoku.grid[fila][col] != 0:
                        self.vista_tablero.marcar(fila, col, "resuelta")
        else:
            self._restaurar_puzzle()
            self._estado_resolucion = f"No se pudo resolver con {algoritmo}"

        self.vista_tablero._rebuild_textos()

    def _aplicar_evento_visual(self, evento):
        self.vista_tablero.limpiar_estados()

        if evento[0] == ASIGNANDO:
            _, fila, col, _ = evento
            self.vista_tablero.marcar(fila, col, "asignando")
            self.vista_tablero._rebuild_textos()

        elif evento[0] == PODANDO:
            _, fila, col = evento
            self.vista_tablero.marcar(fila, col, "podando")

        elif evento[0] == RETROCEDIENDO:
            _, fila, col = evento
            self.vista_tablero.marcar(fila, col, "retroceso")
            self.vista_tablero._rebuild_textos()

        elif evento[0] == SOLUCIONADO:
            for fila in range(self._sudoku.N):
                for col in range(self._sudoku.N):
                    if (fila, col) not in self._sudoku.fijas and self._sudoku.grid[fila][col] != 0:
                        self.vista_tablero.marcar(fila, col, "resuelta")
            self.vista_tablero._rebuild_textos()
            self._solver = None

    def _dibujar_estado_solver(self):
        if not self._estado_resolucion:
            return

        color = (0, 0, 0)
        arcade.draw_lrbt_rectangle_filled(
            180, ANCHO_VENTANA - 180, ALTO_VENTANA - 122, ALTO_VENTANA - 94, (245, 245, 245)
        )
        texto = arcade.Text(
            self._estado_resolucion,
            ANCHO_VENTANA // 2,
            ALTO_VENTANA - 108,
            color,
            font_size=11,
            anchor_x="center",
            anchor_y="center",
        )
        texto.draw()

    def _dibujar_grafica_fuerza_bruta(self):
        if not self._mostrar_grafica_fb or not self._fb_resultado:
            return

        x0, y0 = ANCHO_VENTANA - 300, 70
        ancho, alto = 250, 150
        arcade.draw_lrbt_rectangle_filled(x0, x0 + ancho, y0, y0 + alto, (245, 245, 245))
        arcade.draw_lrbt_rectangle_outline(x0, x0 + ancho, y0, y0 + alto, (90, 105, 150), 2)

        titulo = arcade.Text("Complejidad observada", x0 + ancho / 2, y0 + alto - 14,
                             (0, 0, 0), font_size=10, anchor_x="center", anchor_y="center")
        titulo.draw()

        margen_izq = 34
        margen_der = 14
        margen_inf = 26
        margen_sup = 28
        gx0 = x0 + margen_izq
        gy0 = y0 + margen_inf
        gx1 = x0 + ancho - margen_der
        gy1 = y0 + alto - margen_sup

        arcade.draw_line(gx0, gy0, gx1, gy0, (150, 160, 190), 1)
        arcade.draw_line(gx0, gy0, gx0, gy1, (150, 160, 190), 1)

        tiempos = self._fb_resultado.muestras_tiempo or [0.0]
        memorias = self._fb_resultado.muestras_memoria or [0.0]
        max_t = max(tiempos[-1], 0.001)
        max_m = max(max(memorias), 1.0)

        puntos = []
        for tiempo, memoria in zip(tiempos, memorias):
            px = gx0 + ((tiempo / max_t) * (gx1 - gx0))
            py = gy0 + ((memoria / max_m) * (gy1 - gy0))
            puntos.append((px, py))

        if len(puntos) >= 2:
            arcade.draw_line_strip(puntos, (90, 210, 255), 2)
        elif len(puntos) == 1:
            arcade.draw_circle_filled(puntos[0][0], puntos[0][1], 2, (90, 210, 255))

        etiqueta_x = arcade.Text("Tiempo", x0 + ancho / 2, y0 + 8,
                                 (0, 0, 0), font_size=9, anchor_x="center")
        etiqueta_x.draw()
        etiqueta_y = arcade.Text("Memoria", x0 + 8, y0 + alto / 2,
                                 (0, 0, 0), font_size=9, rotation=90, anchor_x="center")
        etiqueta_y.draw()

        unidad_mem = "KB"
        valor_mem = max_m
        if max_m >= 1024.0:
            unidad_mem = "MB"
            valor_mem = max_m / 1024.0

        arcade.Text(f"0", gx0, gy0 - 12, (0, 0, 0), font_size=8, anchor_x="center").draw()
        arcade.Text(f"{max_t:.2f}s", gx1, gy0 - 12, (0, 0, 0), font_size=8, anchor_x="center").draw()
        arcade.Text(f"{valor_mem:.2f} {unidad_mem}", gx0 - 4, gy1, (0, 0, 0), font_size=8,
                    anchor_x="right", anchor_y="center").draw()

    def on_update(self, dt):
        if self._fb_resultado_pendiente is not None:
            self._aplicar_resultado_fuerza_bruta(self._fb_resultado_pendiente)

        if self._solver_resultado_pendiente is not None:
            self._aplicar_resultado_solver_directo(*self._solver_resultado_pendiente)

        if self._solver:
            self._tiempo_paso += dt
            if self._tiempo_paso >= self._intervalo_paso:
                self._tiempo_paso = 0.0
                try:
                    evento = next(self._solver)
                    self._aplicar_evento_visual(evento)
                except StopIteration:
                    self._solver = None
                    self.vista_tablero.limpiar_estados()
                    self.vista_tablero._rebuild_textos()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self._zoom = max(
            self._zoom_min,
            min(self.ZOOM_MAX, self._zoom + scroll_y * self.ZOOM_VEL)
        )
        self._camara.zoom = self._zoom

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._drag_activo = True
            self._drag_inicio = (x, y)
            self._pos_camara = tuple(self._camara.position)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._drag_activo = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self._drag_activo:
            return
        ix, iy = self._drag_inicio
        cx, cy = self._pos_camara
        self._camara.position = (
            cx - (x - ix) / self._zoom,
            cy - (y - iy) / self._zoom,
        )

    def on_show_view(self):
        arcade.set_background_color(COLOR_FONDO)

    def on_draw(self):
        self.clear()
        _dibujar_fondo()

        with self._camara.activate():
            self.vista_tablero.dibujar()

        self._txt_info.draw()
        self._dibujar_estado_solver()
        self._dibujar_grafica_fuerza_bruta()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()


