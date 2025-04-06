from abc import ABC, abstractmethod

class SearchAlgorithm(ABC):
    def __init__(self, name):
        self.name = name
        self.description = description

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
        """Devuelve todas las posiciones donde se puede colocar un bloque."""
        block_h, block_w = len(block), len(block[0])
        moves = []
        for i in range(self.grid_size - block_h + 1):
            for j in range(self.grid_size - block_w + 1):
                if self.can_place_block(block, i, j):
                    moves.append((i, j))
        return moves

    def can_place_block(self, block, x, y):
        """Verifica si se puede colocar un bloque en (x, y)."""
        block_h, block_w = len(block), len(block[0])
        for i in range(block_h):
            for j in range(block_w):
                if block[i][j] == 1 and self.board[x + i][y + j] == 1:
                    return False  # No se puede colocar sobre otro bloque
        return True
