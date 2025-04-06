import copy
import heapq
from abc import ABC, abstractmethod
from algorithms import SearchAlgorithm



class GreedySearch(SearchAlgorithm):
    """
    Estrategia Greedy: en cada paso, se escoge el movimiento que
    maximiza la "ganancia" inmediata, sin mirar más allá.
    Podemos reutilizar la evaluación local de 'evaluate_move'.
    """
    def evaluate_move(self, board, diamonds, block, move):
        """
        Se basa en cuántos diamantes destruye y cuántos espacios
        vacíos quedan (parecido a la 'evaluate_move' de main.py).
        """
        new_board, new_diamonds = self.apply_move(board, diamonds, move, block)

        # Diamantes destruidos (diferencia de diamantes)
        original_count = sum(sum(r) for r in diamonds)
        new_count = sum(sum(r) for r in new_diamonds)
        destroyed = original_count - new_count

        # Espacios vacíos
        empty_spaces = sum(row.count(0) for row in new_board)

        # Buscamos maximizar (destroyed - #espacios vacíos)
        # Ajusta la fórmula a tus necesidades
        return destroyed - (25 - empty_spaces)
    
    def get_best_move(self, blocks):
        """
        Recorre todas las jugadas posibles (para cada block, cada posición)
        y devuelve la que tenga mayor evaluación inmediata.
        """
        best_score = float('-inf')
        best_action = None

        for block in self.blocks:
            moves = self.possible_moves(block)
            for move in moves:
                score = self.evaluate_move(self.board, self.diamonds, block, move)
                if score > best_score:
                    best_score = score
                    best_action = (block, move[0], move[1])

        return best_action


class AStarSearch(SearchAlgorithm):
    """
    Búsqueda A*: Se trata de encontrar una secuencia de jugadas
    que lleve a eliminar todos los diamantes con el menor costo
    (menor cantidad de pasos, por ejemplo).
    - g(n): número de movimientos hasta 'n'
    - h(n): heurística (por ejemplo, número de diamantes restantes)
    """
    def evaluate_move(self, move):
        """
        Este método no se usa directamente en la planificación A*
        (lo hacemos en la expansión con open/closed).
        Lo mantenemos para cumplir con la interfaz.
        """
        return 0

    def heuristic(self, diamonds):
        """
        Heurística: estimación de cuántos movimientos faltan.
        Un ejemplo sencillo: la cantidad de diamantes que quedan.
        """
        return sum(sum(row) for row in diamonds)

    def get_best_move(self, blocks):
        """
        Realiza una búsqueda A* para encontrar un plan que elimine
        todos los diamantes. Luego devuelve el primer movimiento
        de ese plan.
        """
        import heapq

        start_board = copy.deepcopy(self.board)
        start_diamonds = copy.deepcopy(self.diamonds)
        start_state = self.hash_state(start_board, start_diamonds)

        # La cola de prioridad A* guardará tuplas de la forma:
        # (f, g, (board, diamonds), path)
        # donde 'path' es la secuencia de (block, x, y) hasta ahora.
        open_heap = []
        g_start = 0
        h_start = self.heuristic(start_diamonds)
        f_start = g_start + h_start
        heapq.heappush(open_heap, (f_start, g_start, (start_board, start_diamonds), []))

        closed_set = set()

        while open_heap:
            f, g, (board_current, diamonds_current), path = heapq.heappop(open_heap)

            if self.is_goal(diamonds_current):
                # Si ya no hay diamantes, retornamos el primer movimiento
                if path:
                    return path[0]  # (block, x, y)
                else:
                    return None  # No se requirió ningún movimiento

            state_id = self.hash_state(board_current, diamonds_current)
            if state_id in closed_set:
                continue

            closed_set.add(state_id)

            # Expansión: probar colocar cualquiera de los 'blocks'
            for block in self.blocks:
                pmoves = self.possible_moves(block)
                for move in pmoves:
                    new_board, new_diamonds = self.apply_move(board_current, diamonds_current, move, block)
                    new_state_id = self.hash_state(new_board, new_diamonds)
                    if new_state_id in closed_set:
                        continue

                    g_new = g + 1
                    h_new = self.heuristic(new_diamonds)
                    f_new = g_new + h_new
                    new_path = path + [(block, move[0], move[1])]
                    heapq.heappush(open_heap, (f_new, g_new, (new_board, new_diamonds), new_path))

        # Si el heap se vacía sin encontrar meta, no hay plan
        return None


class WeightedAStarSearch(SearchAlgorithm):
    """
    A* Weighted: f(n) = g(n) + w * h(n)
    Favorece estados con menor heurística cuando w > 1.
    """
    def __init__(self, name, board, diamonds, w=1.5, description="Weighted A*"):
        super().__init__(name, board, diamonds, description)
        self.w = w  # Peso para la heurística

    def evaluate_move(self, move):
        return 0  # No se usa directamente

    def heuristic(self, diamonds):
        """
        Heurística similar: número de diamantes restantes.
        Ajusta a tu preferencia.
        """
        return sum(sum(row) for row in diamonds)

    def get_best_move(self, blocks):
        import heapq

        start_board = copy.deepcopy(self.board)
        start_diamonds = copy.deepcopy(self.diamonds)
        start_state = self.hash_state(start_board, start_diamonds)

        # La cola de prioridad con tuplas (f, g, (board, diamonds), path)
        open_heap = []
        g_start = 0
        h_start = self.heuristic(start_diamonds)
        f_start = g_start + self.w * h_start
        heapq.heappush(open_heap, (f_start, g_start, (start_board, start_diamonds), []))

        closed_set = set()

        while open_heap:
            f, g, (board_current, diamonds_current), path = heapq.heappop(open_heap)

            if self.is_goal(diamonds_current):
                if path:
                    return path[0]
                else:
                    return None

            state_id = self.hash_state(board_current, diamonds_current)
            if state_id in closed_set:
                continue

            closed_set.add(state_id)

            for block in self.blocks:
                pmoves = self.possible_moves(block)
                for move in pmoves:
                    new_board, new_diamonds = self.apply_move(board_current, diamonds_current, move, block)
                    new_state_id = self.hash_state(new_board, new_diamonds)
                    if new_state_id in closed_set:
                        continue

                    g_new = g + 1
                    h_new = self.heuristic(new_diamonds)
                    f_new = g_new + self.w * h_new
                    new_path = path + [(block, move[0], move[1])]
                    heapq.heappush(open_heap, (f_new, g_new, (new_board, new_diamonds), new_path))

        return None
if __name__ == "__main__":
    # Tablero de ejemplo 5x5
    board = [[0 for _ in range(5)] for _ in range(5)]
    diamonds = [[0 for _ in range(5)] for _ in range(5)]

    # Colocar algunos diamantes
    diamonds[1][2] = 1
    diamonds[2][1] = 1
    diamonds[3][3] = 1

    default_block = [[1, 1, 1]]

    print("\n=== GREEDY SEARCH ===")
    greedy = GreedySearch("Greedy", board, diamonds)
    possible_moves = greedy.possible_moves(default_block)
    print("Possible moves:", possible_moves)
    best = greedy.get_best_move(greedy.blocks)
    if best:
        block, x, y = best
        print(f"Greedy best move: Place block {block} at ({x}, {y})")
    else:
        print("No greedy solution found.")

    print("\n=== A* SEARCH ===")
    astar = AStarSearch("A*", board, diamonds)
    best = astar.get_best_move(astar.blocks)
    if best:
        block, x, y = best
        print(f"A* best move: Place block {block} at ({x}, {y})")
    else:
        print("No A* solution found.")

    print("\n=== WEIGHTED A* SEARCH ===")
    weighted_astar = WeightedAStarSearch("A* Weighted", board, diamonds, w=1.5)
    best = weighted_astar.get_best_move(weighted_astar.blocks)
    if best:
        block, x, y = best
        print(f"Weighted A* best move: Place block {block} at ({x}, {y})")
    else:
        print("No Weighted A* solution found.")
