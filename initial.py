import tkinter as tk
import numpy as np

# Lógica del juego: WoodBlockAI
class WoodBlockAI:
    def __init__(self, grid_size=10):
        self.grid_size = grid_size
        self.board = np.zeros((grid_size, grid_size), dtype=int)
        self.diamonds = np.zeros((grid_size, grid_size), dtype=int)

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
                    return False  # No se puede colocar sobre otro bloque
        return True

    def evaluate_move(self, block, x, y):
        """Evalúa qué tan buena es una jugada basada en los diamantes eliminados."""
        temp_board = self.board.copy()
        temp_diamonds = self.diamonds.copy()
        # Colocar el bloque temporalmente
        for i in range(len(block)):
            for j in range(len(block[0])):
                if block[i][j] == 1:
                    temp_board[x + i][y + j] = 1

        # Filas y columnas completas
        rows_to_clear = [i for i in range(self.grid_size) if all(temp_board[i])]
        cols_to_clear = [j for j in range(self.grid_size) if all(temp_board[:, j])]

        # Calcular g(n) = Diamantes eliminados
        diamonds_destroyed = sum(np.sum(temp_diamonds[row]) for row in rows_to_clear)
        diamonds_destroyed += sum(np.sum(temp_diamonds[:, col]) for col in cols_to_clear)

        # h(n) = Minimizar la cantidad de bloques sin eliminar
        empty_spaces = np.sum(temp_board == 0)

        return diamonds_destroyed - empty_spaces  # Se busca maximizar diamantes y reducir espacios vacíos

    def best_move(self, blocks):
        """Encuentra la mejor jugada basada en la cantidad de diamantes destruidos."""
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
        self.mode = mode  # "IA" o "Jugador"
        self.cell_size = cell_size
        self.grid_size = game.grid_size
        self.selected_block = None  # Para modo jugador

        # Canvas para dibujar el tablero
        self.canvas = tk.Canvas(self, width=self.grid_size * cell_size, 
                                       height=self.grid_size * cell_size, bg="lightblue")
        self.canvas.pack()

        # Frame para controles
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(pady=10)

        if self.mode == "IA":
            self.move_button = tk.Button(self.control_frame, text="Realizar Mejor Jugada", 
                                         command=self.make_best_move)
            self.move_button.pack(side="left", padx=5)
        else:
            # Para modo jugador, mostramos representaciones gráficas de cada bloque
            tk.Label(self.control_frame, text="Selecciona un bloque:").pack(side="left", padx=5)
            for idx, block in enumerate(self.blocks):
                preview = self.create_block_preview(block)
                # Envolvemos el canvas de previsualización en un frame para poder agregarle borde al seleccionarlo
                frame = tk.Frame(self.control_frame, bd=2, relief="raised")
                preview.pack(in_=frame)
                frame.pack(side="left", padx=3)
                # Asociamos el clic a la función que asigna el bloque seleccionado
                preview.bind("<Button-1>", lambda e, b=block: self.set_selected_block(b))
                # También hacemos que el frame capture el clic
                frame.bind("<Button-1>", lambda e, b=block: self.set_selected_block(b))
            # Enlazar click en el canvas para colocar el bloque seleccionado
            self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.reset_button = tk.Button(self.control_frame, text="Reiniciar Juego", command=self.reset_game)
        self.reset_button.pack(side="left", padx=5)

        self.draw_board()

    def create_block_preview(self, block):
        """Crea un canvas pequeño que representa gráficamente el bloque."""
        # Tamaño base para la previsualización
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
        # Calcular celda clickeada
        j = event.x // self.cell_size
        i = event.y // self.cell_size
        # Verificar si se puede colocar el bloque en (i, j)
        if self.game.can_place_block(self.selected_block, i, j):
            # Colocar bloque
            for di in range(len(self.selected_block)):
                for dj in range(len(self.selected_block[0])):
                    if self.selected_block[di][dj] == 1:
                        self.game.board[i + di][j + dj] = 1
            # Limpiar filas y columnas completas
            self.clear_complete_lines()
            self.draw_board()
            self.selected_block = None
        else:
            print("Movimiento inválido en la posición:", i, j)

    def clear_complete_lines(self):
        # Revisar filas y columnas completas y limpiarlas
        rows_to_clear = [i for i in range(self.grid_size) if all(self.game.board[i])]
        cols_to_clear = [j for j in range(self.grid_size) if all(self.game.board[:, j])]
        for row in rows_to_clear:
            self.game.board[row] = np.zeros(self.grid_size, dtype=int)
            self.game.diamonds[row] = np.zeros(self.grid_size, dtype=int)
        for col in cols_to_clear:
            self.game.board[:, col] = np.zeros(self.grid_size, dtype=int)
            self.game.diamonds[:, col] = np.zeros(self.grid_size, dtype=int)

    def draw_board(self):
        """Dibuja el tablero, los bloques y los diamantes."""
        self.canvas.delete("all")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                # Color de fondo de la celda según su estado
                fill_color = "grey" if self.game.board[i][j] == 1 else "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                # Dibujar diamante si existe (círculo azul)
                if self.game.diamonds[i][j] == 1:
                    self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill="blue", outline="blue")

    def make_best_move(self):
        """Realiza la mejor jugada con la IA, resaltando temporalmente los bloques elegidos."""
        move = self.game.best_move(self.blocks)
        if move is not None:
            block, x, y = move
            # Resaltar temporalmente las celdas donde se colocará el bloque (color naranja)
            for i in range(len(block)):
                for j in range(len(block[0])):
                    if block[i][j] == 1:
                        x1 = (y+j) * self.cell_size
                        y1 = (x+i) * self.cell_size
                        x2 = x1 + self.cell_size
                        y2 = y1 + self.cell_size
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill="orange", outline="black")
            # Después de 500 ms, aplicar la jugada
            self.after(500, lambda: self.commit_move(block, x, y))
        else:
            print("No hay movimientos posibles.")

    def commit_move(self, block, x, y):
        # Colocar el bloque en el tablero
        for i in range(len(block)):
            for j in range(len(block[0])):
                if block[i][j] == 1:
                    self.game.board[x + i][y + j] = 1
        # Limpiar filas y columnas completas
        self.clear_complete_lines()
        self.draw_board()

    def reset_game(self):
        """Reinicia el juego a su estado inicial."""
        board = [[0] * self.grid_size for _ in range(self.grid_size)]
        diamonds = [[0] * self.grid_size for _ in range(self.grid_size)]
        # Configuración inicial (ejemplo)
        board[1][2] = board[1][3] = board[1][4] = 1
        board[2][2] = board[2][3] = board[2][4] = 1
        board[3][2] = board[3][3] = board[3][4] = 1
        diamonds[1][3] = 1
        diamonds[2][2] = 1
        diamonds[3][3] = 1
        self.game.set_board(board, diamonds)
        self.draw_board()

# Pantalla inicial para elegir el modo
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

        # Si se pudo cargar, usarla como fondo
        if self.bg_image:
            bg_label = tk.Label(self, image=self.bg_image)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Se crea un frame transparente (o con color semitransparente) para los controles
        control_frame = tk.Frame(self, bg="lightblue")
        control_frame.pack(expand=True)
        
        tk.Label(control_frame, text="Wood Block Game", font=("Helvetica", 24), bg="lightblue").pack(pady=20)
        tk.Button(control_frame, text="Jugar contra IA", font=("Helvetica", 16), 
                  command=lambda: self.start_callback("IA"), width=20).pack(pady=10)
        tk.Button(control_frame, text="Jugar tú", font=("Helvetica", 16), 
                  command=lambda: self.start_callback("Jugador"), width=20).pack(pady=10)

# Pantalla de juego, que instancia la interfaz principal según el modo elegido
class GameScreen(tk.Frame):
    def __init__(self, master, mode):
        super().__init__(master)
        self.master = master
        self.mode = mode

        grid_size = 10
        # Estado inicial del tablero y diamantes
        board = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        diamonds = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        game = WoodBlockAI(grid_size)
        game.set_board(board, diamonds)
        # Bloques disponibles
        blocks = [
            [[1, 1, 1, 1],[1,0,0,0]],      # Bloque horizontal de 4
            [[1], [1], [1]],   # Bloque vertical de 3
            [[1, 1], [1, 1]],  # Bloque cuadrado de 2x2
        ]

        # Instanciar la interfaz principal según el modo
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

    def start_game(self, mode):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = GameScreen(self, mode)
        self.current_frame.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
