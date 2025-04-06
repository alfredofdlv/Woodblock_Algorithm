from blind_search import DFS, BFS, UniformCostSearch, IterativeDeepeningSearch
from informed_search import AStarSearch, GreedySearch, WeightedAStarSearch
import random
import numpy as np
import matplotlib.pyplot as plt
import time
import pandas as pd
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed


def generate_board(grid_size=5, max_blocks=8, max_diamonds=5):
        """
        Genera un tablero (board) y un arreglo de diamantes (diamonds) para el juego,
        favoreciendo la creación de pequeñas formaciones (clusters) juntas.
        
        Parámetros:
        grid_size: tamaño del tablero (por defecto 5)
        max_blocks: número máximo de celdas con bloques (por defecto 5)
        max_diamonds: número máximo de diamantes (por defecto 3)
        
        Devuelve:
        board, diamonds: dos listas de listas (grid_size x grid_size) con valores 0 o 1.
        """
        board = [[0] * grid_size for _ in range(grid_size)]
        diamonds = [[0] * grid_size for _ in range(grid_size)]

        cluster_patterns = [
            [(0, 0)],                               
            [(0, 0), (0, 1), (1, 0), (1, 1)],         
            [(0, 0), (0, 1)],                       
            [(0, 0), (1, 0)],                        
            [(0, 0), (0, 1), (0, 2)],                  
            [(0, 0), (1, 0), (2, 0)]                  
        ]
        
        blocks_placed = 0
        attempts = 0
        while blocks_placed < max_blocks and attempts < 20:
            attempts += 1
            pattern = random.choice(cluster_patterns)
            if len(pattern) > max_blocks - blocks_placed:
                continue
            max_x = grid_size - max(p[0] for p in pattern)
            max_y = grid_size - max(p[1] for p in pattern)
            if max_x <= 0 or max_y <= 0:
                continue
            x = random.randint(0, max_x - 1)
            y = random.randint(0, max_y - 1)
            can_place = True
            for dx, dy in pattern:
                if board[x + dx][y + dy] == 1:
                    can_place = False
                    break
            if can_place:
                
                for dx, dy in pattern:
                    board[x + dx][y + dy] = 1
                    blocks_placed += 1
                    if blocks_placed >= max_blocks:
                        break

        
        diamond_count = 0
        
        block_positions = [(i, j) for i in range(grid_size) for j in range(grid_size) if board[i][j] == 1]
        random.shuffle(block_positions)
        for pos in block_positions:
            if diamond_count < max_diamonds:
                
                if random.random() < 0.5:
                    i, j = pos
                    diamonds[i][j] = 1
                    diamond_count += 1
            else:
                break

        return board, diamonds
  
def run_game(search_algo, board, diamonds):
    """
    Runs the game by repeatedly invoking the search algorithm until a goal state is reached.
    Returns the total number of moves executed and the elapsed time.
    """
    move_count = 0
    current_board = copy.deepcopy(board)
    current_diamonds = copy.deepcopy(diamonds)
    start_time = time.time()
    
    while not search_algo.is_goal(current_diamonds):
        default_block = [[1, 1, 1]]  # used for generating moves
        possible_moves = search_algo.possible_moves(default_block)
        best_move = search_algo.get_best_move(possible_moves, current_board, current_diamonds)
        if best_move is None:
            print("No solution found. Terminating game.")
            break
        block, x, y = best_move
        current_board, current_diamonds = search_algo.apply_move(current_board, current_diamonds, (x, y), block)
        move_count += 1
        
    elapsed_time = time.time() - start_time
    return move_count, elapsed_time

num_iterations = 10

algorithms = {
    "DFS": DFS,
    "BFS": BFS,
    "UCS": UniformCostSearch,
    "It. Deep": IterativeDeepeningSearch,
    "A*": AStarSearch,
    "A* weighted": WeightedAStarSearch,
    "Greedy": GreedySearch,
}

results = {name: {"moves": [], "time": []} for name in algorithms.keys()}

base_board, base_diamonds = generate_board(grid_size=5, max_blocks=8, max_diamonds=5)
futures = {}
with ThreadPoolExecutor(max_workers=len(algorithms)) as executor:
    for name, algo_class in algorithms.items():
        for i in range(num_iterations):

            if name == "A* weighted":
                algo_instance = algo_class("A* weighted", copy.deepcopy(base_board), copy.deepcopy(base_diamonds), w=2.0)
            else:
                algo_instance = algo_class(copy.deepcopy(base_board), copy.deepcopy(base_diamonds))


            future = executor.submit(run_game, algo_instance, base_board, base_diamonds)
            futures[future] = name


    for future in as_completed(futures):
        name = futures[future]
        moves, elapsed = future.result()
        results[name]["moves"].append(moves)
        results[name]["time"].append(elapsed)
        print(f"{name} iteration: moves={moves}, time={elapsed:.2f} seconds")

avg_times = {name: sum(results[name]["time"]) / num_iterations for name in results}
avg_moves = {name: sum(results[name]["moves"]) / num_iterations for name in results}

informed = {"A*", "Greedy", "A* weighted"}
blind = {"DFS", "BFS", "UCS", "Iterative Deepening"}

colors = []
labels = []
for name in avg_times.keys():
    if name in informed:
        colors.append("salmon")  
        labels.append("Informed Search")
    else:
        colors.append("skyblue")  
        labels.append("Blind Search")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

bars1 = ax1.bar(avg_times.keys(), avg_times.values(), color=colors)
ax1.set_xlabel('Algorithm')
ax1.set_ylabel('Average Time (s)')
ax1.set_title('Average Execution Time')

bars2 = ax2.bar(avg_moves.keys(), avg_moves.values(), color=colors)
ax2.set_xlabel('Algorithm')
ax2.set_ylabel('Average Moves')
ax2.set_title('Average Number of Moves')

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='skyblue', label='Blind Search'),
    Patch(facecolor='salmon', label='Informed Search')
]
ax1.legend(handles=legend_elements)
ax2.legend(handles=legend_elements)

plt.tight_layout()
plt.show()
