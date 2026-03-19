# ──────────────────────────────────────────────
#  main.py  –  Entry point
# ──────────────────────────────────────────────
import arcade
from constantes       import ANCHO_VENTANA, ALTO_VENTANA, TITULO_VENTANA
from vista.ventana    import PantallaMenu


def main():
    ventana = arcade.Window(ANCHO_VENTANA, ALTO_VENTANA, TITULO_VENTANA)
    menu    = PantallaMenu()
    ventana.show_view(menu)
    arcade.run()


if __name__ == "__main__":
    main()
