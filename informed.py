import copy
import heapq
from abc import ABC, abstractmethod
from algorithms import SearchAlgorithm
import numpy as np


class GreedySearch(SearchAlgorithm):
    """
    Estrategia Greedy: en cada paso, se escoge el movimiento que
    maximiza la "ganancia" inmediata, sin mirar más allá.
    Podemos reutilizar la evaluación local de 'evaluate_move'.
    """
    def evaluate_move(self, board, diamonds, block, move):
        """
        Evaluate a move by applying it and computing a heuristic value.
        Here, we use a simple heuristic: the number of remaining diamonds.
        Lower values are better.
        """
        new_board, new_diamonds = self.apply_move(board, diamonds, move, block)
        # Heuristic: count remaining diamonds.
        h = sum(sum(row) for row in new_diamonds)
        return h

    def get_best_move(self, possible_moves, board, diamonds):
        """
        Perform a Greedy Best-First Search over the state space starting from the given board
        and diamond configuration. The algorithm considers all three block pieces.
        It returns the best move as a tuple (block, x, y) corresponding to the first move
        (from the initial state) that leads to a goal state (i.e., no diamonds remain), based
        on the heuristic value.
        """
        # Update instance variables.
        self.board = copy.deepcopy(board)
        self.diamonds = copy.deepcopy(diamonds)
        self.grid_size = len(board)
        
        # Initialize the priority queue (min-heap).
        # Each state: (heuristic_value, node_id, current_board, current_diamonds, first_move)
        # first_move is (block, x, y) taken from the initial state.
        node_counter = 0
        initial_state = (self.evaluate_move(board, diamonds, self.blocks[0], (0,0)),
                         node_counter,
                         copy.deepcopy(board),
                         copy.deepcopy(diamonds),
                         None)
        node_counter += 1
        frontier = []
        heapq.heappush(frontier, initial_state)
        explored = set()
        
        while frontier:
            h, _, current_board, current_diamonds, first_move = heapq.heappop(frontier)
            if self.is_goal(current_diamonds):
                return first_move if first_move is not None else None

            state_hash = self.hash_state(current_board, current_diamonds)
            if state_hash in explored:
                continue
            explored.add(state_hash)
            
            # Update self.board for generating moves.
            self.board = current_board
            
            for block in self.blocks:
                moves = self.possible_moves(block)
                for move in moves:
                    new_board, new_diamonds = self.apply_move(current_board, current_diamonds, move, block)
                    new_h = self.evaluate_move(current_board, current_diamonds, block, move)
                    next_first_move = first_move if first_move is not None else (block, move[0], move[1])
                    heapq.heappush(frontier, (new_h, node_counter, new_board, new_diamonds, next_first_move))
                    node_counter += 1
        return None


class AStarSearch(SearchAlgorithm):
    """
    Búsqueda A*: Se trata de encontrar una secuencia de jugadas
    que lleve a eliminar todos los diamantes con el menor costo
    (menor cantidad de pasos, por ejemplo).
    - g(n): número de movimientos hasta 'n'
    - h(n): heurística (por ejemplo, número de diamantes restantes)
    """
    def evaluate_move(self, board, diamonds, block, move):
        new_board, new_diamonds = self.apply_move(board, diamonds, move, block)
        # Simple heuristic: count the number of remaining diamonds.
        return sum(sum(row) for row in new_diamonds)
    
    def heuristic(self, diamonds):
        """Heuristic: number of remaining diamonds."""
        return sum(sum(row) for row in diamonds)
    
    def get_best_move(self, possible_moves, board, diamonds):
        """
        Perform an A* search over the state space starting from the given board
        and diamond configuration. The algorithm considers all three block pieces:
        - Horizontal block of 3: [[1, 1, 1]]
        - Vertical block of 3:   [[1], [1], [1]]
        - Square block of 2x2:    [[1, 1], [1, 1]]
        Returns the best move as a tuple (block, x, y) corresponding to the first move
        that leads to a goal state (i.e., no diamonds remain).
        """
        self.board = copy.deepcopy(board)
        self.diamonds = copy.deepcopy(diamonds)
        self.grid_size = len(board)
    
        
        start_board = copy.deepcopy(board)
        start_diamonds = copy.deepcopy(diamonds)
        g_start = 0
        h_start = self.heuristic(start_diamonds)
        f_start = g_start + h_start
        
        # Priority queue: each entry is (f, g, state_hash, current_board, current_diamonds, path)
        # where path is a sequence of moves, each of the form (block, x, y).
        open_heap = []
        start_hash = self.hash_state(start_board, start_diamonds)
        heapq.heappush(open_heap, (f_start, g_start, start_hash, start_board, start_diamonds, []))
        
        closed_set = set()
        node_counter = 0  # Not strictly needed now.
        
        while open_heap:
            f, g, state_hash, current_board, current_diamonds, path = heapq.heappop(open_heap)
            
            if self.is_goal(current_diamonds):
                return path[0] if path else None
            
            if state_hash in closed_set:
                continue
            closed_set.add(state_hash)
            
            self.board = current_board  # Update for move generation.
            
            for block in self.blocks:
                moves = self.possible_moves(block)
                for move in moves:
                    new_board, new_diamonds = self.apply_move(current_board, current_diamonds, move, block)
                    new_state_hash = self.hash_state(new_board, new_diamonds)
                    if new_state_hash in closed_set:
                        continue
                    g_new = g + 1
                    h_new = self.heuristic(new_diamonds)
                    f_new = g_new + h_new
                    new_path = path + [(block, move[0], move[1])]
                    heapq.heappush(open_heap, (f_new, g_new, node_counter, new_board, new_diamonds, new_path))
                    node_counter += 1

        
        return None




class WeightedAStarSearch(SearchAlgorithm):
    """
    Weighted A*: f(n) = g(n) + w * h(n)
    Favours states with a lower heuristic value when w > 1.
    """
    def __init__(self, name, board, diamonds, w=1.5, description="Weighted A*"):
        super().__init__(name, board, diamonds, description)
        self.w = w  # Weight for the heuristic
        # Define available block pieces if not already set.
        self.blocks = [
            [[1, 1, 1]],      # Horizontal block of 3
            [[1], [1], [1]],   # Vertical block of 3
            [[1, 1], [1, 1]]   # Square block of 2x2
        ]

    def evaluate_move(self, board, diamonds, block, move):
        # This method is not used directly in our implementation.
        return 0

    def heuristic(self, diamonds):
        """
        Heuristic: number of remaining diamonds.
        """
        return sum(sum(row) for row in diamonds)

    def get_best_move(self, possible_moves, board, diamonds):
        """
        Perform a Weighted A* search over the state space starting from the given board
        and diamond configuration. The search considers all three block pieces.
        Returns the best move as a tuple (block, x, y) corresponding to the first move
        in the plan that leads to a goal state (i.e. no diamonds remain).
        """
        self.board = copy.deepcopy(board)
        self.diamonds = copy.deepcopy(diamonds)
        self.grid_size = len(board)
        
        start_board = copy.deepcopy(board)
        start_diamonds = copy.deepcopy(diamonds)
        g_start = 0
        h_start = self.heuristic(start_diamonds)
        f_start = g_start + self.w * h_start
        start_state_hash = self.hash_state(start_board, start_diamonds)
        
        # Priority queue with tuples: (f, g, state_hash, (board, diamonds), path)
        open_heap = []
        heapq.heappush(open_heap, (f_start, g_start, start_state_hash, (start_board, start_diamonds), []))
        closed_set = set()
        
        while open_heap:
            f, g, state_hash, (current_board, current_diamonds), path = heapq.heappop(open_heap)
            
            if self.is_goal(current_diamonds):
                return path[0] if path else None
            
            if state_hash in closed_set:
                continue
            closed_set.add(state_hash)
            
            self.board = current_board  # Update for move generation.
            for block in self.blocks:
                pmoves = self.possible_moves(block)
                for move in pmoves:
                    new_board, new_diamonds = self.apply_move(current_board, current_diamonds, move, block)
                    new_state_hash = self.hash_state(new_board, new_diamonds)
                    if new_state_hash in closed_set:
                        continue
                    
                    g_new = g + 1
                    h_new = self.heuristic(new_diamonds)
                    f_new = g_new + self.w * h_new
                    new_path = path + [(block, move[0], move[1])]
                    heapq.heappush(open_heap, (f_new, g_new, new_state_hash, (new_board, new_diamonds), new_path))
        
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
