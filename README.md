# Sudoku CSP — Documentación del Proyecto

## Índice

1. [Descripción general](#descripción-general)
2. [Requisitos e instalación](#requisitos-e-instalación)
3. [Estructura del proyecto](#estructura-del-proyecto)
4. [Explicación archivo por archivo](#explicación-archivo-por-archivo)
   - [main.py](#mainpy)
   - [constantes.py](#constantespy)
   - [modelo/sudoku.py](#modelosudokupy)
   - [modelo/csp_solver.py](#modelocsp_solverpy)
   - [modelo/fuerza_bruta.py](#modelofuerza_brutapy)
   - [modelo/forward_checking_solver.py](#modeloforward_checking_solverpy)
   - [vista/tablero.py](#vistatableropy)
   - [vista/ventana.py](#vistaventanapy)
5. [Pipeline de generación del puzzle](#pipeline-de-generación-del-puzzle)
6. [Algoritmos de resolución disponibles](#algoritmos-de-resolución-disponibles)
7. [Controles de la interfaz](#controles-de-la-interfaz)

---

## Descripción general

Este proyecto genera puzzles de Sudoku de distintos tamaños y los muestra en una interfaz visual interactiva construida con **Arcade**. El Sudoku se modela como un **Problema de Satisfacción de Restricciones (CSP)**, lo que permite combinar generación eficiente con varios algoritmos de resolución para comparación académica.

Actualmente el proyecto incluye:

- generación optimizada de tableros
- resolución por **Fuerza Bruta**
- resolución por **Backtracking**
- resolución por **Forward Checking**
- animación paso a paso para tamaños pequeños
- tablero fijo de laboratorio para pruebas en 9x9

---

## Requisitos e instalación

```bash
pip install arcade
```

Para ejecutar:

```bash
cd sudoku_base_proyecto/sudoku_project
python main.py
```

Requiere Python 3.10 o superior.

---

## Estructura del proyecto

```text
sudoku_project/
│
├── main.py
├── constantes.py
│
├── modelo/
│   ├── __init__.py
│   ├── sudoku.py
│   ├── csp_solver.py
│   ├── fuerza_bruta.py
│   ├── fuerza_bruta_metricas.py
│   └── forward_checking_solver.py
│
└── vista/
    ├── __init__.py
    ├── tablero.py
    ├── animadores.py
    └── ventana.py
```

La separación sigue el patrón **Modelo–Vista**: el modelo concentra la lógica del Sudoku y la vista maneja toda la interacción gráfica.

---

## Explicación archivo por archivo

### main.py

Punto de entrada del programa. Crea la ventana principal de Arcade, carga el menú y lanza el loop de la aplicación.

### constantes.py

Centraliza tamaños de ventana, colores, dificultades y tamaños de tablero disponibles.

- `TAMANIOS`: mapea cada etiqueta visible a su valor `k`
- `DIFICULTADES`: define el porcentaje de celdas visibles
- `TAM_CELDA_MIN`: evita que las celdas desaparezcan visualmente en tableros grandes

### modelo/sudoku.py

Es el núcleo del generador. Contiene la clase `Sudoku` y la lógica optimizada de construcción y resolución interna del tablero.

Entre sus ideas principales están:

- peers precalculados por celda
- grupos por filas, columnas y bloques
- candidatos por bitmask
- propagación tipo AC-3
- naked pairs/triples
- MRV y LCV
- backtracking optimizado

También se encarga de generar un puzzle y marcar las celdas fijas en `self.fijas`.

### modelo/csp_solver.py

Contiene `solve_sudoku_BT()`, una implementación de **backtracking puro**. Modifica el tablero directamente y devuelve `True` o `False` según encuentre solución.

Esta versión se usa como algoritmo base de comparación.

### modelo/fuerza_bruta.py

Contiene `solve_sudoku_FB()`, una heurística de **llenado aleatorio con reparación iterativa y reinicios**. Primero llena las celdas vacías con valores aleatorios, luego recorre las celdas editables para cambiar valores y reducir violaciones de restricciones. Si se atasca, reinicia desde el tablero original con otro llenado.

### modelo/forward_checking_solver.py

Contiene la clase `ForwardCheckingSolver`, que implementa:

- selección de variable no asignada
- prueba de valores del dominio
- poda de dominios vecinos
- backtracking cuando un dominio queda vacío

Es el resolvedor más fuerte entre los tres algoritmos visibles de la interfaz.

### vista/tablero.py

Dibuja el tablero y sus números. También maneja estados visuales para colorear celdas durante la resolución:

- `asignando`
- `retroceso`
- `podando`
- `resuelta`

### vista/ventana.py

Contiene las pantallas de la app:

- `PantallaMenu`
- `PantallaCargando`
- `PantallaPuzzle`

Aquí se integran los botones de resolución, el zoom, el desplazamiento, los estimativos de tiempo en tableros grandes, la gráfica de complejidad de fuerza bruta y el botón especial **Tablero ejemplo laboratorio** para 9x9.

---

## Pipeline de generación del puzzle

```text
generar()
    │
    ├─ 1. construir patrón válido base
    ├─ 2. mezclar filas, columnas, bandas y pilas
    ├─ 3. propagar restricciones con AC-3
    ├─ 4. aplicar naked subsets cuando conviene
    ├─ 5. completar con backtracking optimizado
    └─ 6. eliminar celdas según dificultad
```

Esto permite generar tableros de múltiples tamaños manteniendo buen rendimiento en la práctica.

---

## Algoritmos de resolución disponibles

### 1. Fuerza Bruta

Usa una heurística de llenado aleatorio con reparación local e intentos con reinicio. No hace backtracking ni garantiza solución; precisamente se mantiene como contraste académico para mostrar que un enfoque ingenuo puede fallar con frecuencia.

Límites actuales de intentos:

- `4x4`: 50
- `9x9`: 50
- `16x16`: 20
- `25x25` o mayores: no se ejecuta

Si falla, la interfaz muestra:

- mensaje `No se pudo resolver`
- intentos usados
- tiempo total
- mini-gráfica de tiempo vs memoria

Para tableros de `25x25` o mayores, la interfaz no lanza el algoritmo y muestra directamente un mensaje indicando que la fuerza bruta no se ejecutó para ese tamaño.

### 2. Backtracking

Usa búsqueda recursiva clásica con validación directa por celda.

Comportamiento en interfaz:

- `4x4` y `9x9`: animado paso a paso
- `16x16` en adelante: no se ejecuta; solo muestra un estimativo de tiempo

### 3. Forward Checking

Usa backtracking con poda de dominios vecinos tras cada asignación.

Comportamiento en interfaz:

- `4x4` y `9x9`: animado paso a paso
- `16x16`: se ejecuta directamente y muestra el resultado final
- `25x25` en adelante: no se ejecuta; solo muestra estimativo para ahorrar recursos

---

## Controles de la interfaz

| Acción | Control |
|---|---|
| Zoom in | Scroll arriba |
| Zoom out | Scroll abajo |
| Mover la vista | Click izquierdo + arrastrar |
| Volver al menú | Botón Menu |
| Nuevo puzzle | Botón Nuevo |
| Resolver por fuerza bruta | Botón Fuerza Bruta |
| Resolver por backtracking | Botón Backtracking |
| Resolver por forward checking | Botón Forward Checking |
| Cargar tablero fijo 9x9 | Botón Tablero ejemplo laboratorio |

---

## Tablero ejemplo laboratorio

Cuando el usuario selecciona tamaño `9x9` en el menú, aparece un botón que carga este tablero fijo:

```python
tablero = [
    [0,0,3,0,2,0,6,0,0],
    [9,0,0,3,0,5,0,0,1],
    [0,0,1,8,0,6,4,0,0],
    [0,0,8,1,0,2,9,0,0],
    [7,0,0,0,0,0,0,0,8],
    [0,0,6,7,0,8,2,0,0],
    [0,0,2,6,0,9,5,0,0],
    [8,0,0,2,0,3,0,0,9],
    [0,0,5,0,1,0,3,0,0],
]
```

Este caso sirve para demostraciones, pruebas de algoritmos y comparación visual de resolutores.
