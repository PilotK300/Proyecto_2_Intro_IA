# ──────────────────────────────────────────────
#  constantes.py
# ──────────────────────────────────────────────

# Ventana base (se agranda dinámicamente para tableros grandes)
ANCHO_VENTANA  = 900
ALTO_VENTANA   = 820
TITULO_VENTANA = "Sudoku CSP"

# Tamaño mínimo de celda (px) — solo para cálculo de zoom inicial
TAM_CELDA_MIN  = 6

# Paleta de colores
COLOR_FONDO        = (15,  17,  26)
COLOR_LINEA_FINA   = (50,  55,  80)
COLOR_LINEA_GRUESA = (120, 130, 180)
COLOR_CELDA_FIJA   = (60,  90, 160)
COLOR_CELDA_VACIA  = (25,  28,  42)
COLOR_TEXTO_FIJO   = (220, 230, 255)
COLOR_TEXTO_UI     = (200, 210, 240)

# Dificultad → rango de porcentaje de celdas visibles
DIFICULTADES = {
    "Fácil":   (0.50, 0.62),
    "Medio":   (0.39, 0.48),
    "Difícil": (0.32, 0.38),
    "Experto": (0.27, 0.31),
}

# Tamaños disponibles  k → N=k²
TAMANIOS = {
    "4×4   (k=2)":   2,
    "9×9   (k=3)":   3,
    "16×16 (k=4)":   4,
    "25×25 (k=5)":   5,
    "36×36 (k=6)":   6,
    "49×49 (k=7)":   7,
    "64×64 (k=8)":   8,
    "81×81 (k=9)":   9,
    "100×100 (k=10)": 10,
}
