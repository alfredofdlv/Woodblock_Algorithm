import copy
import heapq
from abc import ABC, abstractmethod
from algorithms import SearchAlgorithm
import numpy as np


class GreedySearch(SearchAlgorithm):
    """
    Greedy Strategy: at each step, the move that maximizes the immediate
    "gain" is chosen, without looking further ahead.
    We can reuse the local evaluation from 'evaluate_move'.
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
        self.board = copy.deepcopy(board)
        self.diamonds = copy.deepcopy(diamonds)
        self.grid_size = len(board)
        

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
    A* Search: The goal is to find a sequence of moves
    that removes all diamonds with the lowest cost
    (e.g., the smallest number of steps).
    - g(n): number of moves to reach 'n'
    - h(n): heuristic (e.g., number of remaining diamonds)
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
        

        open_heap = []
        start_hash = self.hash_state(start_board, start_diamonds)
        heapq.heappush(open_heap, (f_start, g_start, start_hash, start_board, start_diamonds, []))
        
        closed_set = set()
        node_counter = 0  
        
        while open_heap:
            f, g, state_hash, current_board, current_diamonds, path = heapq.heappop(open_heap)
            
            if self.is_goal(current_diamonds):
                return path[0] if path else None
            
            if state_hash in closed_set:
                continue
            closed_set.add(state_hash)
            
            self.board = current_board 
            
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
    def __init__(self, name, board, diamonds, description="Weighted A*",w = 1.5):
        super().__init__(name, board, diamonds, description)
        self.w = w  # Weight for the heuristic

    def evaluate_move(self, board, diamonds, block, move):
        
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
            
            self.board = current_board  
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
