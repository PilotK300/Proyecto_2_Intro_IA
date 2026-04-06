Sudoku CSP — Documentación del Proyecto
Índice
Descripción general
Requisitos e instalación
Estructura del proyecto
Explicación archivo por archivo
main.py
constantes.py
modelo/sudoku.py
modelo/csp_solver.py
vista/tablero.py
vista/ventana.py
Pipeline de generación del puzzle
Optimizaciones implementadas
Controles de la interfaz
Dónde implementar el Solucionador
Descripción general
Este proyecto genera puzzles de Sudoku de distintos tamaños (4×4 hasta 100×100) y los muestra en una interfaz visual interactiva construida con la librería Arcade de Python. El Sudoku se modela como un Problema de Satisfacción de Restricciones (CSP), lo que permite aplicar algoritmos clásicos de IA para la generación eficiente de tableros.

Requisitos e instalación
pip install arcade
Para ejecutar:

cd sudoku_project
python main.py
Requiere Python 3.10 o superior.

Estructura del proyecto
sudoku_project/
│
├── main.py               # Punto de entrada — crea la ventana y lanza el menú
├── constantes.py         # Valores globales: colores, tamaños, dificultades
│
├── modelo/
│   ├── __init__.py
│   ├── sudoku.py         # Clase Sudoku: generación con todas las optimizaciones
│   └── csp_solver.py     # Generador de backtracking paso a paso (para animación)
│
└── vista/
    ├── __init__.py
    ├── tablero.py        # Dibuja la grilla del Sudoku en pantalla
    └── ventana.py        # Pantallas: Menú, Cargando, Puzzle
La separación sigue el patrón Modelo–Vista. El modelo no sabe nada de gráficos y la vista no sabe nada de algoritmos.

Explicación archivo por archivo
main.py
Punto de entrada del programa. Crea la ventana de Arcade con las dimensiones definidas en constantes.py, instancia la primera pantalla (PantallaMenu) y lanza el loop principal de Arcade.

ventana = arcade.Window(ANCHO_VENTANA, ALTO_VENTANA, TITULO_VENTANA)
menu    = PantallaMenu()
ventana.show_view(menu)
arcade.run()
No contiene lógica — su único rol es arrancar la aplicación.

constantes.py
Centraliza todos los valores que se usan en más de un archivo: dimensiones de la ventana, colores de la paleta, rangos de dificultad y el diccionario de tamaños disponibles.

TAMANIOS mapea el texto del botón al valor de k, donde el tablero es de tamaño k² × k²:

TAMANIOS = {
    "9×9   (k=3)":    3,
    "25×25 (k=5)":    5,
    "100×100 (k=10)": 10,
    ...
}
DIFICULTADES define el porcentaje de celdas visibles para cada nivel. Un porcentaje más bajo significa más celdas eliminadas y por tanto mayor dificultad:

DIFICULTADES = {
    "Fácil":   (0.50, 0.62),   # 50–62% de celdas visibles
    "Experto": (0.27, 0.31),   # solo 27–31% visibles
}
TAM_CELDA_MIN es el tamaño mínimo en píxeles de cada celda. Para tableros grandes donde las celdas no caben en la ventana, el zoom permite ver el detalle.

modelo/sudoku.py
Es el núcleo del proyecto. Contiene la clase Sudoku y las funciones auxiliares de bitmask. Toda la lógica de generación del puzzle vive aquí.

Funciones de bitmask
Los candidatos de cada celda se representan como un entero donde cada bit corresponde a un valor posible. Esto reemplaza los set de Python y hace las operaciones entre 5 y 10 veces más rápidas:

# Candidatos {1, 3, 5} como bitmask:
# bit 1 activo = valor 1 posible
# bit 3 activo = valor 3 posible
# bit 5 activo = valor 5 posible
mask = 0b101010  # = 42 en decimal

def _contar(mask):
    return bin(mask).count('1')    # cuántos candidatos quedan

def _valores(mask):
    # extrae la lista de valores activos iterando bit a bit
    ...

def _unico(mask):
    return mask.bit_length()       # valor cuando solo queda 1 candidato
_construir_peers()
Precalcula, para cada celda (r, c), la lista de todas las celdas que comparten fila, columna o bloque con ella. Se llama una sola vez en __init__ y se reutiliza en cada paso del algoritmo, evitando recalcular la misma información miles de veces.

_construir_grupos()
Construye la lista de todos los grupos del tablero: N filas + N columnas + N bloques. Se usa en el algoritmo de Naked pairs/triples para buscar restricciones implícitas.

_candidatos_iniciales()
Crea la matriz de candidatos en formato bitmask a partir del estado actual del grid. Para cada celda ya asignada, elimina ese valor de los candidatos de todos sus peers.

_ac3()
Implementa el algoritmo AC-3 (Arc Consistency 3). Funciona con una cola: busca todas las celdas vacías con un solo candidato, las asigna directamente, y propaga esa asignación a sus peers. Si un peer queda con un solo candidato, se encola también. El proceso se repite en cadena hasta que no haya más singletons. Devuelve False si detecta una contradicción (dominio vacío).

Se llama una sola vez antes del backtracking, no en cada paso recursivo. Esto es clave para la velocidad.

_naked_subsets()
Implementa Naked pairs y Naked triples. Para cada grupo (fila, columna o bloque), busca subconjuntos de 2 o 3 celdas cuya unión de candidatos tenga exactamente 2 o 3 valores. Cuando los encuentra, esos valores se pueden eliminar de todas las demás celdas del grupo sin adivinar nada. Devuelve -1 (contradicción), 0 (sin cambios) o 1 (hubo cambios).

_forward_check()
Después de asignar un valor en el backtracking, verifica inmediatamente si algún peer quedó con cero candidatos. Si sí, retrocede al instante sin explorar el subárbol. Con bitmask esta verificación es una comparación de entero contra cero, prácticamente sin costo.

_mrv()
Selecciona la celda vacía con el menor número de candidatos restantes (Minimum Remaining Values). Devuelve None si el tablero está completo, o (-1, -1) como señal de contradicción.

_backtrack_iterativo()
Backtracking sin recursión. Usa una pila explícita en el heap de Python en vez del call stack. Cada elemento de la pila guarda el estado completo de un nivel de decisión: qué celda se eligió, qué valores quedan por probar, y un snapshot de los candidatos y el grid para poder restaurar si hay que retroceder.

La razón de hacerlo iterativo es que Python tiene un límite de recursión (~1000 frames por defecto), que se agota fácilmente en tableros grandes.

_llenar_diagonal()
Llena los k bloques que están en la diagonal principal del tablero (esquina superior izquierda a esquina inferior derecha) con permutaciones aleatorias de 1 a N. Estos bloques no comparten filas ni columnas entre sí, por lo que se pueden llenar sin verificar ninguna restricción entre ellos. Esto da un punto de partida con N² celdas ya asignadas de forma válida.

generar(porcentaje_visible)
Orquesta el pipeline completo en un bucle while True que reintenta si algo falla:

Reinicia el grid
Llena la diagonal
Ejecuta AC-3 + Naked pairs en bucle hasta estabilizar
Ejecuta el backtracking iterativo para lo que queda
Elimina celdas aleatoriamente según el porcentaje de dificultad
Guarda las posiciones fijas en self.fijas
modelo/csp_solver.py
Contiene la función backtrack() implementada como un generador de Python (usa yield). Esta versión del backtracking emite un evento en cada paso — cuando asigna un valor, cuando retrocede, y cuando termina — para que la vista pueda animarlo en tiempo real.

Actualmente no se usa en la versión principal del proyecto (que solo muestra el puzzle sin resolver), pero está disponible para implementar la animación del solucionador.

# Eventos emitidos:
(ASIGNANDO,    fila, col, valor)   # prueba un valor
(RETROCEDIENDO, fila, col)         # deshace una asignación
(SOLUCIONADO,)                     # tablero completo
vista/tablero.py
La clase VistaTablero se encarga exclusivamente de dibujar el tablero en pantalla. No contiene lógica de Sudoku.

En __init__ calcula el tamaño de celda que cabe en la ventana con los márgenes reservados para el HUD, y construye un objeto arcade.Text por cada celda con valor. Esto es importante: arcade.Text se crea una sola vez y se llama .draw() en cada frame, en vez de usar arcade.draw_text() que recrearía el objeto 60 veces por segundo causando caída de rendimiento.

El método dibujar() tiene tres pasos en orden: fondo de celdas, líneas de grilla, y números encima.

Las celdas fijas (pistas dadas) se muestran en azul. Las celdas vacías en gris oscuro. Los estados asignando, retroceso y resuelta están preparados para la futura animación del solucionador.

vista/ventana.py
Contiene las tres pantallas de la aplicación, cada una como una subclase de arcade.View.

PantallaMenu — menú principal con selección de tamaño, dificultad y botón de generar. Los botones se reconstruyen cada vez que cambia una selección para actualizar el color del botón activo. El estado de selección vive en __init__ (no dentro de _construir_ui) para que no se resetee en cada reconstrucción.

PantallaCargando — pantalla de transición que muestra un spinner animado mientras el Sudoku se genera en un hilo separado (threading.Thread). Esto evita que la ventana se congele durante la generación, especialmente importante para tableros grandes.

PantallaPuzzle — muestra el tablero generado. Usa arcade.Camera2D para implementar zoom con la rueda del mouse y desplazamiento con click + arrastrar. El tablero se dibuja dentro del contexto de la cámara (with self._camara.activate()) mientras los botones y el HUD se dibujan fuera, de forma que no se ven afectados por el zoom.

def on_draw(self):
    with self._camara.activate():
        self.vista_tablero.dibujar()   # ← con zoom y desplazamiento
    self.manager.draw()                # ← sin zoom, siempre en su lugar
Pipeline de generación del puzzle
generar()
    │
    ├─ 1. _llenar_diagonal()
    │      Llena k bloques diagonales con shuffle puro.
    │      Sin backtracking, sin verificación entre bloques.
    │
    ├─ 2. bucle AC-3 + Naked pairs
    │      │
    │      ├─ _ac3()           → propaga singletons en cadena
    │      └─ _naked_subsets() → elimina candidatos por pares/triples
    │         repetir hasta que no haya más cambios
    │
    ├─ 3. _backtrack_iterativo()
    │      Para lo que no se pudo resolver con propagación:
    │      MRV elige la celda más restringida,
    │      Forward Checking detecta contradicciones temprano,
    │      pila explícita evita RecursionError.
    │
    └─ 4. Eliminar celdas
           Borrar aleatoriamente hasta alcanzar el porcentaje de dificultad.
Optimizaciones implementadas
Optimización	Qué hace	Beneficio
Bloques diagonales	Llena k bloques sin backtracking	Punto de partida con N² celdas válidas gratis
Bitmask	Candidatos como enteros en vez de sets	5–10x más rápido en todas las operaciones
AC-3	Propaga singletons en cadena antes del backtracking	Resuelve 60–80% del tablero sin adivinar
Naked pairs/triples	Elimina candidatos por restricciones implícitas	Reduce más el espacio antes del backtracking
MRV	Elige la celda con menos candidatos	Poda el árbol de búsqueda drásticamente
Forward Checking	Detecta contradicción antes de bajar en el árbol	Evita explorar subárboles inútiles
Backtracking iterativo	Pila explícita en vez de recursión	Evita RecursionError en tableros grandes
Tiempos aproximados de generación en Python puro:

Tablero	Tiempo
9×9	< 0.01s
25×25	~0.2s
36×36	~0.5–2s
49×49	~2–8s
64×64+	varios segundos o minutos
Controles de la interfaz
Acción	Control
Zoom in	Scroll arriba
Zoom out	Scroll abajo
Mover la vista	Click izquierdo + arrastrar
Volver al menú	Botón ← Menú
Nuevo puzzle	Botón ↺ Nuevo
Dónde implementar el Solucionador
El archivo modelo/csp_solver.py ya contiene el esqueleto del solucionador como generador. Para integrar la animación del solucionador en la interfaz, los cambios irían en estos lugares:

1. modelo/csp_solver.py — mejorar el backtracking del solucionador con las mismas optimizaciones del generador (MRV, Forward Checking, bitmask). Actualmente usa backtracking simple sin heurísticas.

2. vista/ventana.py — agregar una nueva pantalla PantallaSolucionador similar a PantallaPuzzle pero con un on_update que consume un paso del generador por frame:

def on_update(self, dt):
    for _ in range(self.pasos_por_frame):
        try:
            evento = next(self.solver_gen)
            self._procesar_evento(evento)
        except StopIteration:
            self.resuelto = True
3. vista/tablero.py — los estados asignando, retroceso y resuelta ya están implementados en dibujar(). Solo hay que llamar a marcar(fila, col, estado) desde _procesar_evento para que las celdas cambien de color en tiempo real.

4. PantallaPuzzle — agregar un botón ▶ Resolver que instancie PantallaSolucionador pasándole el puzzle actual.

El flujo completo quedaría:

Menú → Generar → PantallaPuzzle
                      │
                      └─ [▶ Resolver] → PantallaSolucionador
                                             │
                                             ├─ csp_solver.backtrack() como generador
                                             ├─ on_update() consume pasos por frame
                                             └─ tablero.marcar() colorea en tiempo real
La separación actual del código hace que este cambio sea localizado — el modelo no necesita modificarse para soportar la animación, solo la vista.
