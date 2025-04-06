import copy
from collections import deque
import random
import heapq
from abc import ABC, abstractmethod

from algorithms import SearchAlgorithm

class BFS(SearchAlgorithm):
    def __init__(self, board, diamonds, name="Breadth-First Search"):
        super().__init__(name, board, diamonds, "Uninformed search algorithm using BFS.")

    def evaluate_move(self, move):
        # In uninformed search, all moves are equally valid.
        return 0

    def get_best_move(self, possible_moves, board, diamonds):
        """
        Perform a breadth-first search over the state space starting from the given board
        and diamond configuration. The algorithm considers all three block pieces:
          - Horizontal block of 3: [[1,1,1]]
          - Vertical block of 3: [[1],[1],[1]]
          - Square block of 2x2: [[1,1],[1,1]]
        Returns the best move as a tuple (block, x, y) corresponding to the first move
        that leads to a goal state (i.e. no diamonds remain).
        """
        
        self.board = copy.deepcopy(board)
        self.diamonds = copy.deepcopy(diamonds)
        self.grid_size = len(board)
        
        initial_state = (copy.deepcopy(board), copy.deepcopy(diamonds), None)
        frontier = deque([initial_state])
        explored = set()
        
        while frontier:
            current_board, current_diamonds, first_move = frontier.popleft()
            if self.is_goal(current_diamonds):
                return first_move if first_move is not None else None
            
            state_hash = self.hash_state(current_board, current_diamonds)
            if state_hash in explored:
                continue
            explored.add(state_hash)
            
            self.board = current_board
            
            for block in self.blocks:
                moves = self.possible_moves(block)
                for move in moves:
                    new_board, new_diamonds = self.apply_move(current_board, current_diamonds, move, block)
                    next_first_move = first_move if first_move is not None else (block, move[0], move[1])
                    frontier.append((new_board, new_diamonds, next_first_move))
        
        return None  



class DFS(SearchAlgorithm):
    def __init__(self, board, diamonds, name="Depth-First Search"):
        super().__init__(name, board, diamonds, "Uninformed search algorithm using DFS.")
    
    def evaluate_move(self, move):
        return 0

    def get_best_move(self, possible_moves, board, diamonds):
        """
        Perform a depth-first search over the state space starting from the given board
        and diamond configuration. This DFS explores the state space using all three block pieces:
          - Horizontal block of 3: [[1,1,1]]
          - Vertical block of 3:   [[1],[1],[1]]
          - Square block of 2x2:    [[1,1],[1,1]]
        Returns the best move as a tuple (block, x, y) corresponding to the first move
        (from the initial state) that leads to a goal state (i.e. no diamonds remain).
        """
        self.board = copy.deepcopy(board)
        self.diamonds = copy.deepcopy(diamonds)
        self.grid_size = len(board)
        
       
        initial_state = (copy.deepcopy(board), copy.deepcopy(diamonds), None)
        stack = [initial_state]
        explored = set()
        
        while stack:
            current_board, current_diamonds, first_move = stack.pop()
            if self.is_goal(current_diamonds):
                return first_move if first_move is not None else None

            state_hash = self.hash_state(current_board, current_diamonds)
            if state_hash in explored:
                continue
            explored.add(state_hash)
            
            self.board = current_board 
            for block in self.blocks:
                moves = self.possible_moves(block)
                for move in moves:
                    new_board, new_diamonds = self.apply_move(current_board, current_diamonds, move, block)
                    next_first_move = first_move if first_move is not None else (block, move[0], move[1])
                    stack.append((new_board, new_diamonds, next_first_move))
        return None

class UniformCostSearch(SearchAlgorithm):
    def __init__(self, board, diamonds, name="Uniform Cost Search"):
        super().__init__(name, board, diamonds, "Search algorithm that expands the least costly nodes first.")

    def evaluate_move(self, move):
        # For uniform cost search, assume each move costs 1.
        return 1

    def get_best_move(self, possible_moves, board, diamonds):
        """
        Perform a uniform cost search over the state space starting from the given board
        and diamond configuration. The algorithm considers all three block pieces:
          - Horizontal block of 3: [[1, 1, 1]]
          - Vertical block of 3:   [[1], [1], [1]]
          - Square block of 2x2:    [[1, 1], [1, 1]]
        Returns the best move as a tuple (block, x, y) corresponding to the first move
        from the initial state that leads to a goal state (i.e., no diamonds remain).
        """
        
        self.board = copy.deepcopy(board)
        self.diamonds = copy.deepcopy(diamonds)
        self.grid_size = len(board)
        
        initial_state = (0, 0, copy.deepcopy(board), copy.deepcopy(diamonds), None)
        frontier = []
        heapq.heappush(frontier, initial_state)
        explored = set()
        node_counter = 1  
        
        while frontier:
            cost, _, current_board, current_diamonds, first_move = heapq.heappop(frontier)
            if self.is_goal(current_diamonds):
                return first_move if first_move is not None else None
            
            state_hash = self.hash_state(current_board, current_diamonds)
            if state_hash in explored:
                continue
            explored.add(state_hash)
            
            self.board = current_board
            for block in self.blocks:
                moves = self.possible_moves(block)
                for move in moves:
                    new_board, new_diamonds = self.apply_move(current_board, current_diamonds, move, block)
                    next_cost = cost + 1  
                    next_first_move = first_move if first_move is not None else (block, move[0], move[1])
                    heapq.heappush(frontier, (next_cost, node_counter, new_board, new_diamonds, next_first_move))
                    node_counter += 1
        return None
    
class IterativeDeepeningSearch(SearchAlgorithm):
    def __init__(self, board, diamonds, name="Iterative Deepening Search"):
        super().__init__(name, board, diamonds, "Uninformed search algorithm using iterative deepening DFS.")

    def evaluate_move(self, board, diamonds, block, move):
        # Not used directly in IDS.
        return 0


    def get_best_move(self, possible_moves, board, diamonds, max_depth=50):
        """
        Perform an iterative deepening search over the state space.
        The search considers all three block pieces and returns the best move as a tuple
        (block, x, y) corresponding to the first move of the found solution.
        """
        self.board = copy.deepcopy(board)
        self.diamonds = copy.deepcopy(diamonds)
        self.grid_size = len(board)
        
        for depth_limit in range(1, max_depth + 1):
            result = self.depth_limited_search(board, diamonds, depth_limit, [])
            if result is not None:
                return result[0]
        return None

    def depth_limited_search(self, board, diamonds, limit, path):
        if self.is_goal(diamonds):
            return path
        if limit == 0:
            return None
        for block in self.blocks:
            moves = self.possible_moves(block)
            for move in moves:
                new_board, new_diamonds = self.apply_move(board, diamonds, move, block)
                new_path = path + [(block, move[0], move[1])]
                result = self.depth_limited_search(new_board, new_diamonds, limit - 1, new_path)
                if result is not None:
                    return result
        return None
