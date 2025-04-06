from abc import ABC, abstractmethod

class SearchAlgorithm(ABC):
    def __init__(self, name, board, diamonds, description=""):
        self.name = name
        self.description = description
        self.grid_size = 5
        self.board = board
        self.diamonds = diamonds

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