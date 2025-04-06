from abc import ABC, abstractmethod
import copy
from collections import deque
import random
from abc import ABC, abstractmethod

class SearchAlgorithm(ABC):
    def __init__(self, name, board, diamonds, description=""):
        self.name = name
        self.description = description
        self.grid_size = 5
        self.board = board
        self.diamonds = diamonds
        self.blocks = [
            [[1, 1, 1]],    # Horizontal block of 3
            [[1], [1], [1]], # Vertical block of 3
            [[1, 1], [1, 1]]  # Square block of 2x2
        ]

    @abstractmethod
    def evaluate_move(self, move):
        """
        Evaluate the given move.
        """
        pass

    @abstractmethod
    def get_best_move(self, possible_moves, board, diamonds):
        """
        Get the best move.
        """
        pass

    def possible_moves(self, block):
        """Return all positions where a block can be placed."""
        block_h, block_w = len(block), len(block[0])
        moves = []
        for i in range(self.grid_size - block_h + 1):
            for j in range(self.grid_size - block_w + 1):
                if self.can_place_block(block, i, j):
                    moves.append((i, j))
        return moves

    def can_place_block(self, block, x, y):
        """Check if the block can be placed on self.board at position (x, y)."""
        block_h, block_w = len(block), len(block[0])
        for i in range(block_h):
            for j in range(block_w):
                if self.board[x + i][y + j] == 1:
                    return False
        return True
    
    def is_goal(self, diamonds):
        """Goal is reached when there are no diamonds remaining."""
        return sum(sum(row) for row in diamonds) == 0

    def apply_move(self, board, diamonds, move, block):
        """
        Apply the move by placing the block on the board at the specified position.
        Returns a new board and diamond configuration. This simplified version also clears
        a row or column if it becomes completely filled.
        """
        new_board = copy.deepcopy(board)
        new_diamonds = copy.deepcopy(diamonds)
        x0, y0 = move
        block_h, block_w = len(block), len(block[0])
        
        # Place the block.
        for i in range(block_h):
            for j in range(block_w):
                if block[i][j] == 1:
                    new_board[x0 + i][y0 + j] = 1
        
        # Dummy clearance: clear any completely filled row.
        for i in range(self.grid_size):
            if all(new_board[i][j] == 1 for j in range(self.grid_size)):
                new_board[i] = [0] * self.grid_size
                new_diamonds[i] = [0] * self.grid_size
        
        # Dummy clearance: clear any completely filled column.
        for j in range(self.grid_size):
            if all(new_board[i][j] == 1 for i in range(self.grid_size)):
                for i in range(self.grid_size):
                    new_board[i][j] = 0
                    new_diamonds[i][j] = 0
        
        return new_board, new_diamonds

    def hash_state(self, board, diamonds):
        # Convert to lists if board or diamonds are numpy arrays.
        if hasattr(board, "tolist"):
            board = board.tolist()
        if hasattr(diamonds, "tolist"):
            diamonds = diamonds.tolist()
        board_tuple = tuple(tuple(row) for row in board)
        diamonds_tuple = tuple(tuple(row) for row in diamonds)
        return (board_tuple, diamonds_tuple)

