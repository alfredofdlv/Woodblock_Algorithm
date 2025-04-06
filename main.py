import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import time 
import random
from blind_search import DFS, BFS, UniformCostSearch, IterativeDeepeningSearch
from informed_search import GreedySearch, AStarSearch, WeightedAStarSearch


class WoodBlockAI:
    def __init__(self, grid_size=5, chosen_algorithm=None):
        """Inicializa el juego con un tamaño de tablero y un algoritmo de IA."""
        self.grid_size = grid_size
        self.board = np.zeros((grid_size, grid_size), dtype=int)
        self.diamonds = np.zeros((grid_size, grid_size), dtype=int)
        self.chosen_algorithm = chosen_algorithm
        self.ALGORITHM_NAME_MAP = {
            "BFS": BFS(self.board, self.diamonds),
            "DFS": DFS(self.board, self.diamonds),
            "UCS": UniformCostSearch(self.board, self.diamonds),  
            "Iterative Deepening" : IterativeDeepeningSearch(self.board, self.diamonds),
            "Greedy": GreedySearch("Greedy", self.board, self.diamonds),
            "A*": AStarSearch("A*", self.board, self.diamonds),
            "A* weighted": WeightedAStarSearch("A* Weighted", self.board, self.diamonds, w=1.5),
        }


    def set_board(self, board, diamonds):
        """Establece el estado inicial del tablero."""
        self.board = np.array(board)
        self.diamonds = np.array(diamonds)

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
                    return False  
        return True

    def best_move(self, blocks):
        """Encuentra la mejor jugada basada en la cantidad de diamantes destruidos."""

        search_algorithm = self.ALGORITHM_NAME_MAP.get(self.chosen_algorithm, BFS(self.board, self.diamonds))  # Default to BFS if not found  , BFS(self.board, self.diamonds)
        
        default_block = [[1, 1, 1]]
        possible_moves = search_algorithm.possible_moves(default_block)
        print("Possible moves (from initial state):", possible_moves)
        move = search_algorithm.get_best_move(possible_moves, self.board, self.diamonds)
        print(f"Best move found using {search_algorithm.name}:", move)
        return move



class AlgorithmSelectionDialog(tk.Toplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.title("Selecciona Algoritmo")
        self.callback = callback
        self.geometry("300x150")
        self.resizable(False, False)
        self.grab_set() 

        tk.Label(
            self, text="Select AI Algorithm:", font=("Helvetica", 14)
        ).pack(pady=10)

        self.algorithms = ["BFS","DFS", "UCS" ,"A*", "A* weighted", "Greedy", "Iterative Deepening"]
        self.selected_algo = tk.StringVar(self)
        self.selected_algo.set(self.algorithms[0])
        option_menu = tk.OptionMenu(self, self.selected_algo, *self.algorithms)
        option_menu.config(font=("Helvetica", 12))
        option_menu.pack(pady=5)

        tk.Button(
            self, text="Start Game", font=("Helvetica", 12), command=self.on_start
        ).pack(pady=10)

    def on_start(self):
        algo = self.selected_algo.get()
        print(f"Chosen Algorithm: {algo}")
        self.callback("IA", algo)
        self.destroy()


class WoodBlockGUI(tk.Frame):
    def __init__(self, master, game, blocks, mode="IA", cell_size=40):
        super().__init__(master)
        self.master = master
        self.game = game
        self.blocks = blocks
        self.mode = mode 
        self.grid_size = game.grid_size
        self.selected_block = None
        

        self.pack(expand=True, fill="both")

        top_frame = tk.Frame(self)
        top_frame.pack(side="top", expand=True, fill="both")

        self.canvas = tk.Canvas(top_frame, bg="white", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        self.canvas.bind("<Configure>", lambda e: self.draw_board())

        self.control_frame = tk.Frame(self)
        self.control_frame.pack(side="bottom", pady=10)

        if self.mode == "IA":
            self.move_button = tk.Button(
                self.control_frame, text="Do Best Move", command=self.make_best_move
            )
            self.move_button.pack(side="left", padx=5)
            self.auto_button = tk.Button(self.control_frame, text="Auto", command=self.start_auto_play)
            self.auto_button.pack(side="left", padx=5)
        else:
            tk.Label(self.control_frame, text="Choose a block:").pack(
                side="left", padx=5
            )
            for idx, block in enumerate(self.blocks):
                preview = self.create_block_preview(block)
                frame = tk.Frame(self.control_frame, bd=2, relief="raised")
                preview.pack(in_=frame)
                frame.pack(side="left", padx=3)
                preview.bind(
                    "<Button-1>", lambda e, b=block: self.set_selected_block(b)
                )
                frame.bind("<Button-1>", lambda e, b=block: self.set_selected_block(b))
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            self.hint_button = tk.Button(
                self.control_frame, text="Hint", command=self.show_hint
            )
            self.hint_button.pack(side="left", padx=5)

        self.reset_button = tk.Button(
            self.control_frame, text="Restart Game", command=self.reset_game
        )
        self.reset_button.pack(side="left", padx=5)
        

    def show_hint(self):
        """Muestra un hint de la mejor jugada posible."""
        
        move = self.game.best_move(self.blocks)
        if move is not None:
            block, x, y = move
            
            for i in range(len(block)):
                for j in range(len(block[0])):
                    if block[i][j] == 1:
                        x1 = self.x_offset + (y + j) * self.cell_size
                        y1 = self.y_offset + (x + i) * self.cell_size
                        x2 = x1 + self.cell_size
                        y2 = y1 + self.cell_size
                        self.canvas.create_rectangle(
                            x1, y1, x2, y2, fill="orange", outline="black"
                        )
            
            self.after(600, self.draw_board)
        else:
            print("No possible moves for hint.")

    def create_block_preview(self, block):
        """Crea un canvas pequeño que representa gráficamente el bloque."""
        preview_cell = 20
        rows = len(block)
        cols = len(block[0])
        preview = tk.Canvas(
            self.control_frame,
            width=cols * preview_cell,
            height=rows * preview_cell,
            bg="white",
        )
        for i in range(rows):
            for j in range(cols):
                x1 = j * preview_cell
                y1 = i * preview_cell
                x2 = x1 + preview_cell
                y2 = y1 + preview_cell
                if block[i][j] == 1:
                    preview.create_rectangle(
                        x1, y1, x2, y2, fill="orange", outline="black"
                    )
                else:
                    preview.create_rectangle(
                        x1, y1, x2, y2, fill="white", outline="gray"
                    )
        return preview
    
    def start_auto_play(self):
        
        self.game_over = False
        self.auto_start_time = time.time()
        self.auto_play()

    def auto_play(self):
       
        if getattr(self, 'game_over', False):
            return
        move = self.game.best_move(self.blocks)
        if move is None:
            elapsed = time.time() - self.auto_start_time
            print(f"No moves possible. Auto play finished in {elapsed:.2f} seconds")
            self.game_over = True
            return
        block, x, y = move
        self.commit_move(block, x, y)
        self.auto_timer = self.after(2500, self.auto_play)

    def set_selected_block(self, block):
        self.selected_block = block
        print("Selected block:", block)

    def on_canvas_click(self, event):
        cell_size = self.cell_size
        
        x_click = event.x - self.x_offset
        y_click = event.y - self.y_offset

        board_width = self.grid_size * cell_size
        board_height = self.grid_size * cell_size
        
        if (
            x_click < 0
            or y_click < 0
            or x_click >= board_width
            or y_click >= board_height
        ):
            return

        
        j = int(x_click // cell_size)
        i = int(y_click // cell_size)

        if self.selected_block is None:
            return

        if self.game.can_place_block(self.selected_block, i, j):
            for di in range(len(self.selected_block)):
                for dj in range(len(self.selected_block[0])):
                    if self.selected_block[di][dj] == 1:
                        self.game.board[i + di][j + dj] = 1
            self.clear_complete_lines()
            self.draw_board()
            self.check_game_over()
            self.selected_block = None
        else:
            print("Invalid movement in position:", i, j)

    
    def create_animation_preview(self, preview_cell=None):
        if preview_cell is None:
            preview_cell = self.cell_size  
        
        preview = tk.Canvas(
            self.canvas,
            width=preview_cell,
            height=preview_cell,
            bg="white",
            highlightthickness=0,
        )
        
        preview.create_rectangle(
            0, 0, preview_cell, preview_cell, fill="lightblue", outline="black"
        )
        return preview

    
    def create_single_cell_animation(self):
        
        preview = tk.Canvas(
            self.canvas,
            width=self.cell_size,
            height=self.cell_size,
            bg="white",
            highlightthickness=0,
        )
        preview.create_rectangle(
            0, 0, self.cell_size, self.cell_size, fill="lightblue", outline="black"
        )
        return preview

    def create_cell_preview(self):
        preview = tk.Canvas(
            self.canvas,
            width=self.cell_size,
            height=self.cell_size,
            bg="white",
            highlightthickness=0,
        )
        preview.create_rectangle(
            0, 0, self.cell_size, self.cell_size, fill="yellow", outline="black"
        )
        return preview

    def create_single_cell_preview(self, fill_color="lightblue"):
        preview = tk.Canvas(
            self.canvas,
            width=self.cell_size,
            height=self.cell_size,
            bg="white",
            highlightthickness=0,
        )
        preview.create_rectangle(
            0, 0, self.cell_size, self.cell_size, fill=fill_color, outline="black"
        )
        return preview

    def flash_complete_lines(self, rows, cols, flashes=4, delay=300, iteration=0):
        self.canvas.delete("flash")
        if iteration < flashes:
            if iteration < flashes - 1:
                color = "lightblue" if iteration % 2 == 0 else "white"
            else:
                color = "lightblue"
            for row in rows:
                for col in range(self.grid_size):
                    x1 = self.x_offset + col * self.cell_size
                    y1 = self.y_offset + row * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", tag="flash")
            self.canvas.tag_raise("flash")
            self.canvas.update_idletasks()
            self.animation_timer = self.after(delay, lambda: self.flash_complete_lines(rows, cols, flashes, delay, iteration + 1))
        else:
            self._clear_lines(rows, cols)

    def clear_complete_lines(self):
        print("clear_complete_lines called")
        rows_to_clear = [i for i in range(self.grid_size) if all(self.game.board[i])]
        cols_to_clear = [j for j in range(self.grid_size) if all(self.game.board[:, j])]
        print("Rows to clear:", rows_to_clear)
        print("Columns to clear:", cols_to_clear)
        if rows_to_clear or cols_to_clear:
            self.flash_complete_lines(rows_to_clear, cols_to_clear, flashes=4, delay=300)
        else:
            print("No complete lines found; checking game over.")
            self.check_game_over()

    def _clear_lines(self, rows, cols):
        print("Clearing lines for rows:", rows, "and columns:", cols)
        for row in rows:
            self.game.board[row] = np.zeros(self.grid_size, dtype=int)
            self.game.diamonds[row] = np.zeros(self.grid_size, dtype=int)
        for col in cols:
            self.game.board[:, col] = np.zeros(self.grid_size, dtype=int)
            self.game.diamonds[:, col] = np.zeros(self.grid_size, dtype=int)
        print("Board state after clearing lines:")
        print(self.game.board)
        self.draw_board()
        self.check_game_over()


    def draw_board(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cell_size = min(canvas_width / self.grid_size, canvas_height / self.grid_size)
        self.cell_size = cell_size

        board_width = self.grid_size * cell_size
        board_height = self.grid_size * cell_size
        self.x_offset = (canvas_width - board_width) / 2
        self.y_offset = (canvas_height - board_height) / 2

        if hasattr(self, "bg_image") and self.bg_image:
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1 = self.x_offset + j * cell_size
                y1 = self.y_offset + i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                if self.game.board[i][j] == 1:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2, fill="grey", outline="black"
                    )
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")
                if self.game.diamonds[i][j] == 1:
                    self.canvas.create_oval(
                        x1 + cell_size * 0.25,
                        y1 + cell_size * 0.25,
                        x2 - cell_size * 0.25,
                        y2 - cell_size * 0.25,
                        outline="blue",
                        width=2,
                    )

    def make_best_move(self):
        move = self.game.best_move(self.blocks)
        if move is not None:
            block, x, y = move
            for i in range(len(block)):
                for j in range(len(block[0])):
                    if block[i][j] == 1:
                        x1 = self.x_offset + (y + j) * self.cell_size
                        y1 = self.y_offset + (x + i) * self.cell_size
                        x2 = x1 + self.cell_size
                        y2 = y1 + self.cell_size
                        self.canvas.create_rectangle(
                            x1, y1, x2, y2, fill="orange", outline="black"
                        )
            self.after(2500, lambda: self.commit_move(block, x, y))
        else:
            print("No possible moves.")

    def commit_move(self, block, x, y):
        for i in range(len(block)):
            for j in range(len(block[0])):
                if block[i][j] == 1:
                    self.game.board[x + i][y + j] = 1
        self.clear_complete_lines()
        self.draw_board()
        self.check_game_over()

    def reset_game(self):
        board = [[0] * self.grid_size for _ in range(self.grid_size)]
        diamonds = [[0] * self.grid_size for _ in range(self.grid_size)]
        board[1][2] = board[1][3] = 1
        board[2][2] = board[2][3] = 1
        diamonds[1][3] = 1
        diamonds[2][2] = 1
        self.game.set_board(board, diamonds)
        self.draw_board()

    def check_game_over(self):
        if np.sum(self.game.diamonds) == 0:
            self.show_game_over("YOU'VE WON")
            self.game_over = True
            return True
        self.after(1500, self._check_moves)
        return False

    def _check_moves(self):
        has_moves = any(self.game.possible_moves(block) for block in self.blocks)
        if not has_moves:
            print("No possible moves left, YOU'VE LOST.")
            self.show_game_over("YOU'VE LOST")
            self.game_over = True
            return True
        return False
    
    def show_game_over(self, message):
        self.game_over = True
        if hasattr(self, "auto_timer"):
            self.after_cancel(self.auto_timer)
        if hasattr(self, "animation_timer"):
            self.after_cancel(self.animation_timer)
        
        self.canvas.delete("all")
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        overlay = tk.Frame(self.canvas, bg="white")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        message_label = tk.Label(overlay, text=message, font=("Helvetica", 28, "bold"), fg="red", bg="white")
        message_label.pack(pady=(20, 10))
        
        image_file = "assets/youwin.webp" if "WON" in message.upper() else "assets/game_ove.png"
        try:
            from PIL import Image, ImageTk
            pil_image = Image.open(image_file)
            if hasattr(Image, 'Resampling'):
                pil_image = pil_image.resize((200, 200), Image.Resampling.LANCZOS)
            else:
                pil_image = pil_image.resize((200, 200), Image.ANTIALIAS)
            self.gameover_image = ImageTk.PhotoImage(pil_image)
        except Exception as e:
            print("Error loading game over image:", e)
            self.gameover_image = None

        if self.gameover_image:
            image_label = tk.Label(overlay, image=self.gameover_image, bg="white")
            image_label.pack(pady=10)
        else:
            image_label = tk.Label(overlay, text="[Image not available]", bg="white")
            image_label.pack(pady=10)
        

    def go_home(self):
        self.master.master.show_start_screen()

class StartScreen(tk.Frame):
    def __init__(self, master, start_callback, choose_algo_callback):
        super().__init__(master)
        self.start_callback = start_callback
        self.choose_algo_callback = choose_algo_callback

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        try:
            self.orig_bg_image = Image.open("assets/background.jpg")
        except Exception as e:
            print("Error al cargar la imagen de fondo:", e)
            self.orig_bg_image = None

        self.bg_image = None  
        self.canvas.bind("<Configure>", self.update_layout)

    def update_layout(self, event):
        self.canvas.delete("all")
        width, height = event.width, event.height
        if self.orig_bg_image:
            
            if hasattr(Image, "Resampling"):
                resized = self.orig_bg_image.resize(
                    (width, height), Image.Resampling.LANCZOS
                )
            else:
                resized = self.orig_bg_image.resize((width, height), Image.ANTIALIAS)

            self.bg_image = ImageTk.PhotoImage(resized)
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        self.canvas.create_text(
            width / 2,
            height * 0.3,
            text="Woodblock AI",
            font=("Helvetica", 28, "bold"),
            fill="white",
        )
        

        btn1 = tk.Button(
            self.canvas,
            text="Play vs AI",
            font=("Helvetica", 16),
            command=self.choose_algo_callback,
            bd=0,
            relief="flat",
            bg="#333333",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
        )
        btn2 = tk.Button(
            self.canvas,
            text="Selfplayer",
            font=("Helvetica", 16),
            command=lambda: self.start_callback("Jugador"),
            bd=0,
            relief="flat",
            bg="#333333",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
        )
        self.canvas.create_window(width / 2, height * 0.5, window=btn1)
        self.canvas.create_window(width / 2, height * 0.6, window=btn2)


class GameScreen(tk.Frame):
    def __init__(self, master, mode, algorithm=None):
        super().__init__(master)
        self.master = master
        self.mode = mode
        self.algorithm = algorithm  

        grid_size = 5  
        board, diamonds = self.generate_board(grid_size = grid_size , max_blocks=8, max_diamonds=5)

        game = WoodBlockAI(grid_size, chosen_algorithm=algorithm)
        game.set_board(board, diamonds)
        blocks = [
            [[1, 1, 1]],  # Horizontal Block de 3
            [[1], [1], [1]],  # Vertical Block de 3
            [[1, 1], [1, 1]],  # Squared Block de 2x2
        ]

        if self.mode == "IA":
            print(
                f"AI Mode: Using algorithm {self.algorithm}"
            )
        self.gui = WoodBlockGUI(self, game, blocks, mode=self.mode)
        self.gui.pack()
        
        try:
            from PIL import Image, ImageTk
            pil_home = Image.open("assets/home.png")
            if hasattr(Image, 'Resampling'):
                pil_home = pil_home.resize((20, 20), Image.Resampling.LANCZOS)
            else:
                pil_home = pil_home.resize((20, 20), Image.ANTIALIAS)
            self.home_icon = ImageTk.PhotoImage(pil_home)
        except Exception as e:
            print("Error loading home icon:", e)
            self.home_icon = None

        if self.home_icon:
            home_button = tk.Button(self, image=self.home_icon, command=lambda: self.master.show_start_screen(), bd=0, bg="white", activebackground="white")
        else:
            home_button = tk.Button(self, text="Home", command=lambda: self.master.show_start_screen(), bd=0, bg="white", fg="red", font=("Helvetica", 12, "bold"))
        home_button.place(relx=0.98, rely=0.02, anchor="ne")
        
    
    def generate_board(self, grid_size=5, max_blocks=8, max_diamonds=5):
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


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wood Block Game")
        self.geometry("500x600")
        self.resizable(False, False)
        self.current_frame = None
        self.show_start_screen()

    def show_start_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = StartScreen(self, self.start_game, self.choose_algorithm)
        self.current_frame.pack(expand=True, fill="both")

    def choose_algorithm(self):
        
        AlgorithmSelectionDialog(self, self.start_game)

    def start_game(self, mode, algorithm=None):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = GameScreen(self, mode, algorithm)
        self.current_frame.pack(expand=True, fill="both")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
