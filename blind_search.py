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
        # Update instance variables based on input.
        self.board = copy.deepcopy(board)
        self.diamonds = copy.deepcopy(diamonds)
        self.grid_size = len(board)
        
        # Define the available block pieces.
        blocks = [
            [[1, 1, 1]],    # Horizontal block of 3
            [[1], [1], [1]], # Vertical block of 3
            [[1, 1], [1, 1]]  # Square block of 2x2
        ]
        
        # Each state is a tuple: (current_board, current_diamonds, first_move)
        # where first_move is a tuple (block, x, y) indicating the move taken from the initial state.
        initial_state = (copy.deepcopy(board), copy.deepcopy(diamonds), None)
        frontier = deque([initial_state])
        explored = set()
        
        while frontier:
            current_board, current_diamonds, first_move = frontier.popleft()
            if self.is_goal(current_diamonds):
                # Return the recorded first move that led to the goal state.
                return first_move if first_move is not None else None
            
            state_hash = self.hash_state(current_board, current_diamonds)
            if state_hash in explored:
                continue
            explored.add(state_hash)
            
            # Update the board for move generation.
            self.board = current_board
            
            # For each block type, generate possible moves.
            for block in blocks:
                moves = self.possible_moves(block)
                for move in moves:
                    new_board, new_diamonds = self.apply_move(current_board, current_diamonds, move, block)
                    # If this is the first expansion, record the move as (block, x, y).
                    next_first_move = first_move if first_move is not None else (block, move[0], move[1])
                    frontier.append((new_board, new_diamonds, next_first_move))
        
        return None  # No solution found.



class DFS(SearchAlgorithm):
    def __init__(self, board, diamonds, name="Depth-First Search"):
        super().__init__(name, board, diamonds, "Uninformed search algorithm using DFS.")
    
    def evaluate_move(self, move):
        # In uninformed search, all moves are considered equal.
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
        
        # Each state is (current_board, current_diamonds, first_move)
        # where first_move is (block, x, y) taken from the initial state.
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
            
            self.board = current_board  # Update current board for generating moves.
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
        # Update instance variables.
        self.board = copy.deepcopy(board)
        self.diamonds = copy.deepcopy(diamonds)
        self.grid_size = len(board)
        # Each state is (cost, node_id, current_board, current_diamonds, first_move)
        # where first_move is (block, x, y) from the initial state.
        initial_state = (0, 0, copy.deepcopy(board), copy.deepcopy(diamonds), None)
        frontier = []
        heapq.heappush(frontier, initial_state)
        explored = set()
        node_counter = 1  # Unique counter to avoid ambiguous comparisons.
        
        while frontier:
            cost, _, current_board, current_diamonds, first_move = heapq.heappop(frontier)
            if self.is_goal(current_diamonds):
                return first_move if first_move is not None else None
            
            state_hash = self.hash_state(current_board, current_diamonds)
            if state_hash in explored:
                continue
            explored.add(state_hash)
            
            # Update self.board for move generation.
            self.board = current_board
            for block in self.blocks:
                moves = self.possible_moves(block)
                for move in moves:
                    new_board, new_diamonds = self.apply_move(current_board, current_diamonds, move, block)
                    next_cost = cost + 1  # Each move costs 1.
                    next_first_move = first_move if first_move is not None else (block, move[0], move[1])
                    heapq.heappush(frontier, (next_cost, node_counter, new_board, new_diamonds, next_first_move))
                    node_counter += 1
        return None
if __name__ == "__main__":
    # BFSearch algorithm example usage.
    
    # # Example initial state: a 5x5 empty board with some diamonds.
    # board = [[0 for _ in range(5)] for _ in range(5)]
    # diamonds = [[0 for _ in range(5)] for _ in range(5)]
    # # Place some diamonds arbitrarily.
    # diamonds[1][2] = 1
    # diamonds[2][1] = 1
    # diamonds[3][3] = 1

    # # For the initial state, assume the default block is a horizontal block of 3.
    # default_block = [[1, 1, 1]]
    
    # # Instantiate the BFS algorithm with the initial board and diamond configuration.
    # bfs_algo = BFS(board, diamonds)
    
    # # Generate possible moves for the default block (this is used only to trigger the method; BFS will consider all blocks).
    # possible_moves = bfs_algo.possible_moves(default_block)
    # print("Possible moves (from initial state):", possible_moves)

    # best_move = bfs_algo.get_best_move(possible_moves, board, diamonds)
    # if best_move is not None:
    #     block, x, y = best_move
    #     print(f"Best move found by {bfs_algo.name}: Place block {block} at position ({x}, {y})")
    # else:
    #     print("No solution found.")
    
    
    #DSF Search algorithm example usage.
    
    # board = [[0 for _ in range(5)] for _ in range(5)]
    # diamonds = [[0 for _ in range(5)] for _ in range(5)]
    # # Place some diamonds arbitrarily.
    # diamonds[1][2] = 1
    # diamonds[2][1] = 1
    # diamonds[3][3] = 1

    # # Instantiate the DFS algorithm with the initial board and diamond configuration.
    # dfs_algo = DFS(board, diamonds)

    # # For testing, generate possible moves for a default block (horizontal block of 3).
    # default_block = [[1, 1, 1]]
    # possible_moves = dfs_algo.possible_moves(default_block)
    # print("Possible moves (from initial state):", possible_moves)

    # best_move = dfs_algo.get_best_move(possible_moves, board, diamonds)
    # if best_move is not None:
    #     block, x, y = best_move
    #     print(f"Best move found by {dfs_algo.name}: Place block {block} at position ({x}, {y})")
    # else:
    #     print("No solution found.")
    
    board = [[0 for _ in range(5)] for _ in range(5)]
    diamonds = [[0 for _ in range(5)] for _ in range(5)]
    
    # Place some diamonds arbitrarily.
    diamonds[1][2] = 1
    diamonds[2][1] = 1
    diamonds[3][3] = 1

    # Instantiate the Uniform Cost Search algorithm with the initial board and diamond configuration.
    ucs_algo = UniformCostSearch(board, diamonds)
    
    # Generate possible moves using a default block (here used just to trigger possible_moves;
    # UniformCostSearch.get_best_move internally considers all three block types).
    default_block = [[1, 1, 1]]
    possible_moves = ucs_algo.possible_moves(default_block)
    print("Possible moves (from initial state):", possible_moves)
    
    best_move = ucs_algo.get_best_move(possible_moves, board, diamonds)
    if best_move is not None:
        block, x, y = best_move
        print(f"Best move found by {ucs_algo.name}: Place block {block} at position ({x}, {y})")
    else:
        print("No solution found.")