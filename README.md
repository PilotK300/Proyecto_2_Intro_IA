Sudoku CSP — Documentación del Proyecto
📌 Índice

Descripción general 

Requisitos e instalación


Estructura del proyecto 

Explicación archivo por archivo

Pipeline de generación del puzzle


Optimizaciones implementadas 

Controles de la interfaz


Dónde implementar el Solucionador 

📖 Descripción general
Este proyecto genera puzzles de Sudoku de distintos tamaños (desde 4×4 hasta 100×100) y los muestra en una interfaz visual interactiva construida con la librería Arcade de Python. El Sudoku se modela como un Problema de Satisfacción de Restricciones (CSP) , lo que permite aplicar algoritmos clásicos de IA para la generación eficiente de tableros.
+3

🛠 Requisitos e instalación
Requiere Python 3.10 o superior.

Bash
pip install arcade
Para ejecutar:

Bash
cd sudoku_project
python main.py
📂 Estructura del proyecto
La separación sigue el patrón Modelo–Vista. El modelo gestiona la lógica y algoritmos, mientras la vista se encarga exclusivamente de la representación gráfica.

Plaintext
sudoku_project/
├── main.py                # Punto de entrada — lanza el menú
├── constantes.py          # Colores, tamaños y dificultades
├── modelo/
│   ├── __init__.py
│   ├── sudoku.py          # Clase Sudoku: generación y lógicas bitmask
│   └── csp_solver.py      # Backtracking paso a paso para animación [cite: 65]
└── vista/
    ├── __init__.py
    ├── tablero.py         # Dibuja la grilla y números [cite: 66]
    └── ventana.py         # Maneja pantallas (Menú, Puzzle, etc.)
🔍 Explicación de Módulos Clave
modelo/sudoku.py
Es el núcleo del proyecto. Contiene la lógica de resolución y generación:

Bitmask: Los candidatos se representan como enteros para acelerar las operaciones entre 5 y 10 veces.


AC-3: Propaga restricciones de arco para resolver gran parte del tablero antes de adivinar.
+2


Forward Checking: Detecta contradicciones inmediatamente tras asignar un valor, evitando ramas inútiles.
+1


Heurística MRV: Elige la celda con "Menos Valores Restantes" para podar el árbol de búsqueda.

modelo/csp_solver.py
Implementado como un generador de Python (yield). Emite eventos en cada paso (asignar, retroceder, solucionar) para permitir que la vista anime el proceso en tiempo real.
+3

⚙️ Optimizaciones Implementadas
Para cumplir con el análisis de rendimiento solicitado, se integraron las siguientes técnicas:

Optimización	Función	Beneficio
Bitmask	Representación numérica	Velocidad de procesamiento superior a sets
AC-3	Consistencia de arco	Resuelve el 60-80% del tablero sin backtracking
MRV	Heurística de selección	Reduce drásticamente la profundidad de búsqueda
Forward Checking	Poda anticipada	
Evita explorar subárboles sin solución

Backtracking Iterativo	Pila explícita	Evita errores de recursión en tableros de 100x100
🎮 Controles de la interfaz
Acción	Control
Zoom In/Out	Scroll del mouse
Mover Tablero	Click izquierdo + Arrastrar
Nuevo Puzzle	Botón ↺ Nuevo
Menú	Botón ← Menú
🚀 Dónde implementar el Solucionador
Siguiendo las instrucciones del proyecto, el desarrollo debe centralizarse en modelo/csp_solver.py:


Fuerza Bruta: Implementar solve_sudoku_FB probando combinaciones directas.
+1


Backtracking Básico: Refinar la función backtrack con la lógica recursiva estándar.
+1


Forward Checking: Integrar la eliminación de dominios en variables vecinas dentro del flujo de backtracking.
+1
