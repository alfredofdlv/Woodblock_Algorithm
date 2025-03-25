import heapq
from copy import deepcopy

# --------------------------------------------------
# Estructura para manejar el nodo en A*
# --------------------------------------------------
class Node:
    def __init__(self, board_blocks, board_diamonds, remaining_diamonds, parent=None, g=0, h=0):
        self.board_blocks = board_blocks
        self.board_diamonds = board_diamonds
        self.remaining_diamonds = remaining_diamonds
        self.parent = parent  # Para reconstruir la solución
        self.g = g            # Coste real desde el inicio
        self.h = h            # Heurística
        self.f = g + h        # f = g + h

    def __lt__(self, other):
        # Permite comparar nodos en la priority queue (heapq)
        return self.f < other.f


# --------------------------------------------------
# Función para contar espacios libres en el tablero
# (bloques y diamantes juntos o separados según tu lógica).
# --------------------------------------------------
def count_empty_spaces(board_blocks, board_diamonds):
    """
    Retorna el número de celdas que están vacías 
    (ni bloque ni diamante).
    """
    empty_count = 0
    for i in range(5):
        for j in range(5):
            if board_blocks[i][j] == 0 and board_diamonds[i][j] == 0:
                empty_count += 1
    return empty_count


# --------------------------------------------------
# Ejemplo de función heurística
# --------------------------------------------------
def heuristic(board_blocks, board_diamonds, remaining_diamonds):
    """
    Heurística simple que combina:
      - # de diamantes restantes
      - # de espacios libres
    Ajusta alpha y beta según tu preferencia.
    """
    alpha = 5  # Pondera la importancia de colocar diamantes
    beta = 1   # Pondera la importancia de rellenar espacios
    
    # Cuenta cuántos espacios vacíos hay
    empty_count = count_empty_spaces(board_blocks, board_diamonds)
    
    # Heurística = alpha * (#diamantes) + beta * (#espacios)
    return alpha * remaining_diamonds + beta * empty_count


# --------------------------------------------------
# Verifica si un diamante (o bloque) se puede colocar 
# en una posición (i, j) dada.
# --------------------------------------------------
def can_place_diamond(board_blocks, board_diamonds, i, j):
    """
    En este ejemplo, consideramos que un diamante ocupa 
    solo 1 celda (simplificado). Si tu juego maneja 
    formas mayores, tendrás que verificar todas las 
    celdas que ocupa la forma.
    """
    # Debe estar dentro de los límites
    if i < 0 or i >= 5 or j < 0 or j >= 5:
        return False
    
    # La posición debe estar libre (sin bloque y sin diamante)
    if board_blocks[i][j] == 0 and board_diamonds[i][j] == 0:
        return True
    return False


# --------------------------------------------------
# Genera los sucesores de un nodo, colocando 
# el siguiente diamante en todas las posiciones posibles.
# --------------------------------------------------
def generate_successors(current_node):
    successors = []
    
    # Si no quedan diamantes por colocar, no hay sucesores
    if current_node.remaining_diamonds == 0:
        return successors
    
    # Intentar colocar un diamante en cada celda posible
    for i in range(5):
        for j in range(5):
            if can_place_diamond(current_node.board_blocks, current_node.board_diamonds, i, j):
                # Copiamos tableros para no alterar el actual
                new_board_blocks = deepcopy(current_node.board_blocks)
                new_board_diamonds = deepcopy(current_node.board_diamonds)
                
                # Colocamos el diamante (1)
                new_board_diamonds[i][j] = 1
                
                # Creamos el nuevo nodo
                new_remaining_diamonds = current_node.remaining_diamonds - 1
                g_new = current_node.g + 1  # coste de la acción = 1 (colocar diamante)
                h_new = heuristic(new_board_blocks, new_board_diamonds, new_remaining_diamonds)
                
                successor = Node(
                    board_blocks=new_board_blocks,
                    board_diamonds=new_board_diamonds,
                    remaining_diamonds=new_remaining_diamonds,
                    parent=current_node,
                    g=g_new,
                    h=h_new
                )
                successors.append(successor)
    
    return successors

def is_goal_state(node):
    """
    Retorna True si no quedan diamantes por colocar.
    """
    return node.remaining_diamonds == 0

def board_to_tuple(board_blocks, board_diamonds, remaining_diamonds):
    """
    Convierte la información del estado en una tupla hasheable,
    para poder guardarlo en 'visited' o 'closed set'.
    """
    blocks_tuple = tuple(tuple(row) for row in board_blocks)
    diamonds_tuple = tuple(tuple(row) for row in board_diamonds)
    return (blocks_tuple, diamonds_tuple, remaining_diamonds)


def a_star_search(initial_board_blocks, initial_board_diamonds, initial_diamonds):
    """
    Implementa la búsqueda A* para el juego de Wood Block en un tablero 5x5.
    Retorna el nodo objetivo y/o la secuencia de movimientos.
    """
    # Nodo inicial
    h0 = heuristic(initial_board_blocks, initial_board_diamonds, initial_diamonds)
    start_node = Node(
        board_blocks=initial_board_blocks,
        board_diamonds=initial_board_diamonds,
        remaining_diamonds=initial_diamonds,
        parent=None,
        g=0,
        h=h0
    )
    
    # Estructuras para A*
    open_list = []
    heapq.heappush(open_list, start_node)
    
    closed_set = set()
    
    while open_list:
        current_node = heapq.heappop(open_list)
        
        # Verificar si es estado objetivo
        if is_goal_state(current_node):
            # Reconstruir la ruta
            return reconstruct_path(current_node)
        
        # Añadir al closed_set
        state_key = board_to_tuple(current_node.board_blocks, current_node.board_diamonds, current_node.remaining_diamonds)
        if state_key in closed_set:
            continue
        closed_set.add(state_key)
        
        # Expandir sucesores
        successors = generate_successors(current_node)
        for succ in successors:
            succ_key = board_to_tuple(succ.board_blocks, succ.board_diamonds, succ.remaining_diamonds)
            if succ_key not in closed_set:
                heapq.heappush(open_list, succ)
    
    # Si se vacía la open_list sin encontrar solución
    return None


def reconstruct_path(goal_node):
    """
    Reconstruye la secuencia de estados (o acciones) desde el nodo objetivo
    hasta la raíz (nodo inicial).
    """
    path = []
    current = goal_node
    while current is not None:
        path.append(current)
        current = current.parent
    path.reverse()
    return path

def main():
    # Tableros iniciales 5x5
    # Ejemplo: Sin bloques ocupados y sin diamantes
    initial_board_blocks = [
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0]
    ]
    initial_board_diamonds = [
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0]
    ]
    # Supongamos que queremos colocar 3 diamantes
    initial_diamonds = 3

    solution_path = a_star_search(initial_board_blocks, initial_board_diamonds, initial_diamonds)

    if solution_path is not None:
        print("¡Solución encontrada!")
        for idx, node in enumerate(solution_path):
            print(f"\nPaso {idx}:")
            print("Diamantes restantes:", node.remaining_diamonds)
            print("Tablero (bloques):")
            for row in node.board_blocks:
                print(row)
            print("Tablero (diamantes):")
            for row in node.board_diamonds:
                print(row)
    else:
        print("No se encontró solución.")


if __name__ == "__main__":
    main()