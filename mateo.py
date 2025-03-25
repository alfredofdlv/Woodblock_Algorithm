import heapq
from copy import deepcopy
import math

# ==========================
# Representación de piezas
# ==========================
# Definición de las 3 piezas (offsets relativos a (0,0))
piece_2x2 = [(0, 0), (0, 1), (1, 0), (1, 1)]
piece_2x1 = [(0, 0), (1, 0)]
piece_1x2 = [(0, 0), (0, 1)]

BASE_PIECES = [piece_2x2, piece_2x1, piece_1x2]

def rotate_offsets(offsets):
    """
    Rota 90° en sentido horario: (r, c) -> (c, -r),
    luego normaliza para que el offset mínimo sea (0,0).
    """
    rotated = [(c, -r) for (r, c) in offsets]
    min_r = min(r for (r, c) in rotated)
    min_c = min(c for (r, c) in rotated)
    normalized = [(r - min_r, c - min_c) for (r, c) in rotated]
    return sorted(normalized)

def generate_orientations(piece):
    """
    Genera todas las orientaciones únicas (rotaciones) de la pieza.
    """
    orientations = set()
    current = sorted(piece)
    for _ in range(4):
        current = rotate_offsets(current)
        orientations.add(tuple(current))
    return [list(o) for o in orientations]

# Precalcular orientaciones para cada pieza
PIECES_WITH_ORIENTATIONS = []
for p in BASE_PIECES:
    orients = generate_orientations(p)
    PIECES_WITH_ORIENTATIONS.append(orients)

# ==========================
# Definición del nodo
# ==========================
class Node:
    def __init__(self, board, diamonds, score, g=0, h=0, parent=None):
        self.board = board              # Matriz 5x5 de 0/1 (bloques)
        self.diamonds = diamonds        # Matriz 5x5 de 0/1 (diamantes "fijos")
        self.score = score              # Diamantes acumulados (por limpieza de línea)
        self.g = g                      # Número de piezas usadas hasta el momento
        self.h = h                      # Heurística
        self.f = g + h
        self.parent = parent            # Para reconstruir la solución

    def __lt__(self, other):
        return self.f < other.f

# ==========================
# Funciones de utilidades
# ==========================
def print_state(node):
    print(f"Score: {node.score}, Piezas usadas: {node.g}")
    print("Board:")
    for row in node.board:
        print(row)
    print("Diamonds:")
    for row in node.diamonds:
        print(row)
    print("-" * 20)

def board_to_tuple(board):
    return tuple(tuple(row) for row in board)

def state_key(node):
    # La clave del estado se forma a partir de board y diamonds y score.
    return (board_to_tuple(node.board), board_to_tuple(node.diamonds), node.score)

# ==========================
# Función de limpieza de líneas
# ==========================
def remove_complete_lines(board, diamonds):
    """
    Verifica si hay filas o columnas completas.
    Si una fila/columna está completamente llena (con 1 en board),
    se "limpia": se ponen a 0 en board y en diamonds, y se suman los diamantes
    que había en esa línea.
    Retorna (new_board, new_diamonds, diamonds_collected).
    """
    rows_to_clear = [i for i in range(5) if all(board[i][j] == 1 for j in range(5))]
    cols_to_clear = [j for j in range(5) if all(board[i][j] == 1 for i in range(5))]

    diamonds_collected = 0
    new_board = deepcopy(board)
    new_diamonds = deepcopy(diamonds)
    
    # Limpiar filas
    for i in rows_to_clear:
        for j in range(5):
            if new_diamonds[i][j] == 1:
                diamonds_collected += 1
            new_board[i][j] = 0
            new_diamonds[i][j] = 0

    # Limpiar columnas
    for j in cols_to_clear:
        for i in range(5):
            # Evitamos contar dos veces si ya se limpió en fila
            if new_diamonds[i][j] == 1:
                diamonds_collected += 1
            new_board[i][j] = 0
            new_diamonds[i][j] = 0

    return new_board, new_diamonds, diamonds_collected

# ==========================
# Funciones de colocación de piezas
# ==========================
def can_place(board, piece_orientation, r0, c0):
    """
    Verifica si la pieza (definida por sus offsets) se puede colocar
    en (r0, c0) sin salirse del tablero y sin superponerse a bloques existentes.
    """
    for (dr, dc) in piece_orientation:
        r = r0 + dr
        c = c0 + dc
        if r < 0 or r >= 5 or c < 0 or c >= 5:
            return False
        if board[r][c] == 1:
            return False
    return True

def place_piece(board, piece_orientation, r0, c0):
    """
    Coloca la pieza en el board (copia) marcando con 1 las celdas ocupadas.
    Retorna el nuevo board.
    """
    new_board = deepcopy(board)
    for (dr, dc) in piece_orientation:
        r = r0 + dr
        c = c0 + dc
        new_board[r][c] = 1
    return new_board

# ==========================
# Heurística
# ==========================
def heuristic(score):
    """
    Objetivo: conseguir al menos 3 diamantes.
    Suponiendo que en el mejor caso cada pieza aporta 1 diamante,
    una heurística muy simple es:
         h = max(0, 3 - score)
    """
    return max(0, 3 - score)

# ==========================
# Generación de sucesores
# ==========================
def generate_successors(node):
    successors = []
    # Para cada tipo de pieza (2x2, 2x1, 1x2) y cada orientación:
    for piece in PIECES_WITH_ORIENTATIONS:
        for orientation in piece:
            # Recorrer cada celda del tablero para ver dónde se puede colocar
            for r in range(5):
                for c in range(5):
                    if can_place(node.board, orientation, r, c):
                        new_board = place_piece(node.board, orientation, r, c)
                        # Tras colocar, se limpian filas/columnas completas y se recogen diamantes.
                        new_board, new_diamonds, collected = remove_complete_lines(new_board, node.diamonds)
                        new_score = node.score + collected
                        new_g = node.g + 1  # Se ha usado una pieza más
                        new_h = heuristic(new_score)
                        new_node = Node(new_board, new_diamonds, new_score, g=new_g, h=new_h, parent=node)
                        successors.append(new_node)
    return successors

# ==========================
# Prueba de meta
# ==========================
def is_goal(node):
    return node.score >= 3

# ==========================
# Algoritmo A*
# ==========================
def a_star_search(initial_board, initial_diamonds):
    init_score = 0
    start_node = Node(initial_board, initial_diamonds, init_score, g=0, h=heuristic(init_score))
    open_list = []
    heapq.heappush(open_list, start_node)
    closed_set = set()

    while open_list:
        current = heapq.heappop(open_list)
        # Si se alcanza el objetivo, se devuelve el camino de solución
        if is_goal(current):
            return reconstruct_path(current)
        
        key = state_key(current)
        if key in closed_set:
            continue
        closed_set.add(key)
        
        for child in generate_successors(current):
            child_key = state_key(child)
            if child_key not in closed_set:
                heapq.heappush(open_list, child)
    
    return None

def reconstruct_path(node):
    path = []
    while node:
        path.append(node)
        node = node.parent
    path.reverse()
    return path

# ==========================
# Ejemplo de uso con el tablero dado
# ==========================
def main():
    # Tablero inicial (bloques)
    initial_board = [
        [1,1,0,0,0],
        [1,0,0,1,0],
        [1,0,0,1,1],
        [0,0,0,0,1],
        [0,0,1,0,0]
    ]
    # Matriz de diamantes (fijos en el tablero)
    initial_diamonds = [
        [0,1,0,0,0],
        [0,0,0,1,0],
        [1,0,0,0,0],
        [0,0,0,0,1],
        [0,0,1,0,0]
    ]
    
    solution_path = a_star_search(initial_board, initial_diamonds)
    
    if solution_path is None:
        print("No se encontró solución.")
    else:
        print("¡Solución encontrada!")
        for i, node in enumerate(solution_path):
            print(f"\nPaso {i}:")
            print_state(node)

if __name__ == "__main__":
    main()