from abc import ABC, abstractmethod

class SearchAlgorithm(ABC):
    def __init__(self, name):
        self.name = name

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
