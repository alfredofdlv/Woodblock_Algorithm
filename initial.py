import tkinter as tk
import numpy as np
import time
import random

# Lógica del juego: WoodBlockAI
import tkinter as tk
import numpy as np
import time
import random

# Lógica del juego: WoodBlockAI
class WoodBlockAI:
    def __init__(self, grid_size=10):
        self.grid_size = grid_size
        self.board = np.zeros((grid_size, grid_size), dtype=int)
        self.diamonds = np.zeros((grid_size, grid_size), dtype=int)

    def set_board(self, board, diamonds):
        self.board = np.array(board)
        self.diamonds = np.array(diamonds)

    def possible_moves(self, block):
        block_h, block_w = len(block), len(block[0])
        moves = []
        for i in range(self.grid_size - block_h + 1):
            for j in range(self.grid_size - block_w + 1):
                if self.can_place_block(block, i, j):
                    moves.append((i, j))
        return moves

    def can_place_block(self, block, x, y):
        block_h, block_w = len(block), len(block[0])
        for i in range(block_h):
            for j in range(block_w):
                # No se permite colocar si ya hay un bloque o un diamante
                if block[i][j] == 1 and (self.board[x + i][y + j] == 1 or self.diamonds[x + i][y + j] == 1):
                    return False
        return True

    def evaluate_move(self, block, x, y):
        temp_board = self.board.copy()
        temp_diamonds = self.diamonds.copy()
        for i in range(len(block)):
            for j in range(len(block[0])):
                if block[i][j] == 1:
                    temp_board[x + i][y + j] = 1

        rows_to_clear = [i for i in range(self.grid_size) if all(temp_board[i])]
        cols_to_clear = [j for j in range(self.grid_size) if all(temp_board[:, j])]

        diamonds_destroyed = sum(np.sum(temp_diamonds[row]) for row in rows_to_clear)
        diamonds_destroyed += sum(np.sum(temp_diamonds[:, col]) for col in cols_to_clear)
        empty_spaces = np.sum(temp_board == 0)
        return diamonds_destroyed - empty_spaces

    def best_move(self, blocks):
        best_score = float('-inf')
        best_move = None
        for block in blocks:
            for (x, y) in self.possible_moves(block):
                score = self.evaluate_move(block, x, y)
                if score > best_score:
                    best_score = score
                    best_move = (block, x, y)
        print(f"Best move: {best_move}")
        return best_move

# Interfaz gráfica del juego
class WoodBlockGUI(tk.Frame):
    def __init__(self, master, game, blocks, mode="IA", cell_size=40):
        super().__init__(master)
        self.master = master
        self.game = game
        self.blocks = blocks
        self.mode = mode
        self.cell_size = cell_size
        self.grid_size = game.grid_size
        self.selected_block = None
        self.start_time = time.time()

        self.canvas = tk.Canvas(self, width=self.grid_size * cell_size, 
                                       height=self.grid_size * cell_size, bg="lightblue")
        self.canvas.pack()

        self.control_frame = tk.Frame(self)
        self.control_frame.pack(pady=10)

        if self.mode == "IA":
            self.move_button = tk.Button(self.control_frame, text="Realizar Mejor Jugada", 
                                         command=self.make_best_move)
            self.move_button.pack(side="left", padx=5)
        else:
            tk.Label(self.control_frame, text="Selecciona un bloque:").pack(side="left", padx=5)
            for idx, block in enumerate(self.blocks):
                preview = self.create_block_preview(block)
                frame = tk.Frame(self.control_frame, bd=2, relief="raised")
                preview.pack(in_=frame)
                frame.pack(side="left", padx=3)
                preview.bind("<Button-1>", lambda e, b=block: self.set_selected_block(b))
                frame.bind("<Button-1>", lambda e, b=block: self.set_selected_block(b))
            self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.reset_button = tk.Button(self.control_frame, text="Reiniciar Juego", command=self.reset_game)
        self.reset_button.pack(side="left", padx=5)

        self.draw_board()

    def create_block_preview(self, block):
        preview_cell = 20
        rows = len(block)
        cols = len(block[0])
        preview = tk.Canvas(self.control_frame, width=cols * preview_cell, height=rows * preview_cell, bg="white")
        for i in range(rows):
            for j in range(cols):
                x1 = j * preview_cell
                y1 = i * preview_cell
                x2 = x1 + preview_cell
                y2 = y1 + preview_cell
                if block[i][j] == 1:
                    preview.create_rectangle(x1, y1, x2, y2, fill="orange", outline="black")
                else:
                    preview.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")
        return preview

    def set_selected_block(self, block):
        self.selected_block = block
        print("Bloque seleccionado:", block)

    def on_canvas_click(self, event):
        if self.selected_block is None:
            return
        j = event.x // self.cell_size
        i = event.y // self.cell_size
        if self.game.can_place_block(self.selected_block, i, j):
            for di in range(len(self.selected_block)):
                for dj in range(len(self.selected_block[0])):
                    if self.selected_block[di][dj] == 1:
                        self.game.board[i + di][j + dj] = 1
            self.clear_complete_lines()
            self.draw_board()
            self.selected_block = None
            self.check_win()
        else:
            print("Movimiento inválido en la posición:", i, j)

    def clear_complete_lines(self):
        # Una celda se considera ocupada si hay un bloque o un diamante.
        rows_to_clear = [i for i in range(self.grid_size)
                         if all(self.game.board[i][j] == 1 or self.game.diamonds[i][j] == 1 
                                for j in range(self.grid_size))]
        cols_to_clear = [j for j in range(self.grid_size)
                         if all(self.game.board[i][j] == 1 or self.game.diamonds[i][j] == 1 
                                for i in range(self.grid_size))]
        for row in rows_to_clear:
            self.game.board[row] = np.zeros(self.grid_size, dtype=int)
            self.game.diamonds[row] = np.zeros(self.grid_size, dtype=int)
        for col in cols_to_clear:
            self.game.board[:, col] = np.zeros(self.grid_size, dtype=int)
            self.game.diamonds[:, col] = np.zeros(self.grid_size, dtype=int)

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # Si hay un diamante, se pinta la celda de gris y se muestra el símbolo.
                if self.game.diamonds[i][j] == 1:
                    fill_color = "grey"
                else:
                    fill_color = "grey" if self.game.board[i][j] == 1 else "white"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                if self.game.diamonds[i][j] == 1:
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="♦", fill="blue", font=("Helvetica", 20))

    def make_best_move(self):
        move = self.game.best_move(self.blocks)
        if move is not None:
            block, x, y = move
            for i in range(len(block)):
                for j in range(len(block[0])):
                    if block[i][j] == 1:
                        x1 = (y+j) * self.cell_size
                        y1 = (x+i) * self.cell_size
                        x2 = x1 + self.cell_size
                        y2 = y1 + self.cell_size
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill="orange", outline="black")
            self.after(500, lambda: self.commit_move(block, x, y))
        else:
            print("No hay movimientos posibles.")
    
    def commit_move(self, block, x, y):
        for i in range(len(block)):
            for j in range(len(block[0])):
                if block[i][j] == 1:
                    self.game.board[x + i][y + j] = 1
        self.clear_complete_lines()
        self.draw_board()
        self.check_win()

    def check_win(self):
        if np.sum(self.game.diamonds) == 0:
            elapsed_time = time.time() - self.start_time
            self.show_win_screen(elapsed_time)

    def show_win_screen(self, elapsed_time):
        win_window = tk.Toplevel(self)
        win_window.title("You WON!")
        win_window.geometry("300x150")
        msg = f"¡You WON!\nTiempo: {elapsed_time:.2f} segundos"
        label = tk.Label(win_window, text=msg, font=("Helvetica", 20))
        label.pack(padx=20, pady=20)
        tk.Button(win_window, text="Reiniciar", font=("Helvetica", 14), 
                  command=lambda: [win_window.destroy(), self.reset_game()]).pack(pady=10)

    def reset_game(self):
        board = [[0] * self.grid_size for _ in range(self.grid_size)]
        diamonds = [[0] * self.grid_size for _ in range(self.grid_size)]
        diamond_positions = random.sample(
            [(i, j) for i in range(self.grid_size) for j in range(self.grid_size)], 
            k=int(np.sum(self.game.diamonds)) if np.sum(self.game.diamonds) > 0 else 0
        )
        for (i, j) in diamond_positions:
            diamonds[i][j] = 1
        self.game.set_board(board, diamonds)
        self.start_time = time.time()
        self.draw_board()

# Las pantallas StartScreen, GameScreen y MainApp se mantienen iguales.
# (Aquí se incluye el código original de las pantallas sin cambios relevantes al problema)


# Pantalla inicial personalizada
class StartScreen(tk.Frame):
    def __init__(self, master, start_callback):
        super().__init__(master)
        self.master = master
        self.start_callback = start_callback

        # Cargar imagen de fondo
        try:
            self.bg_image = tk.PhotoImage(file="assets/background.jpg")
        except Exception as e:
            print("Error al cargar la imagen de fondo:", e)
            self.bg_image = None

        if self.bg_image:
            bg_label = tk.Label(self, image=self.bg_image)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Frame semitransparente para controles
        control_frame = tk.Frame(self, bg="lightblue", bd=5)
        control_frame.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(control_frame, text="Wood Block Game", font=("Helvetica", 24), bg="lightblue")
        title.grid(row=0, column=0, columnspan=2, pady=10)

        # Selector de grid size
        tk.Label(control_frame, text="Grid Size:", font=("Helvetica", 14), bg="lightblue").grid(row=1, column=0, padx=5, pady=5)
        self.grid_size_var = tk.IntVar(value=10)
        grid_spin = tk.Spinbox(control_frame, from_=5, to=20, width=5, textvariable=self.grid_size_var, font=("Helvetica", 14))
        grid_spin.grid(row=1, column=1, padx=5, pady=5)

        # Selector de número de diamantes
        tk.Label(control_frame, text="Diamantes:", font=("Helvetica", 14), bg="lightblue").grid(row=2, column=0, padx=5, pady=5)
        self.diamond_var = tk.IntVar(value=3)
        diamond_spin = tk.Spinbox(control_frame, from_=1, to=20, width=5, textvariable=self.diamond_var, font=("Helvetica", 14))
        diamond_spin.grid(row=2, column=1, padx=5, pady=5)

        # Botones para seleccionar modo de juego
        tk.Button(control_frame, text="Jugar contra IA", font=("Helvetica", 16), width=15,
                  command=lambda: self.start_game("IA")).grid(row=3, column=0, padx=10, pady=10)
        tk.Button(control_frame, text="Jugar tú", font=("Helvetica", 16), width=15,
                  command=lambda: self.start_game("Jugador")).grid(row=3, column=1, padx=10, pady=10)

    def start_game(self, mode):
        grid_size = self.grid_size_var.get()
        diamond_count = self.diamond_var.get()
        self.start_callback(mode, grid_size, diamond_count)

# Pantalla de juego que utiliza los parámetros elegidos
class GameScreen(tk.Frame):
    def __init__(self, master, mode, grid_size, diamond_count):
        super().__init__(master)
        self.master = master
        self.mode = mode
        self.grid_size = grid_size
        self.diamond_count = diamond_count

        board = [[0] * grid_size for _ in range(grid_size)]
        diamonds = [[0] * grid_size for _ in range(grid_size)]
        diamond_positions = random.sample([(i, j) for i in range(grid_size) for j in range(grid_size)], k=diamond_count)
        for (i, j) in diamond_positions:
            diamonds[i][j] = 1

        game = WoodBlockAI(grid_size)
        game.set_board(board, diamonds)
        blocks = [
            [[1, 1, 1, 1]],      # Bloque horizontal
            [[1], [1], [1]],     # Bloque vertical
            [[1, 1], [1, 1]],    # Bloque cuadrado
        ]
        self.gui = WoodBlockGUI(self, game, blocks, mode=self.mode)
        self.gui.pack()

# Clase principal que maneja la navegación entre pantallas
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
        self.current_frame = StartScreen(self, self.start_game)
        self.current_frame.pack(expand=True, fill="both")

    def start_game(self, mode, grid_size, diamond_count):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = GameScreen(self, mode, grid_size, diamond_count)
        self.current_frame.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
