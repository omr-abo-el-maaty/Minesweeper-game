import tkinter as tk
from collections import deque
import random

class Minesweeper:
    def __init__(self, master):
        self.master = master
        self.difficulty = None
        self.grid_size = None
        self.mines_count = None
        self.flags_count = 0  # Track number of placed flags
        self.show_difficulty_selection()

    def show_difficulty_selection(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        tk.Label(self.master, text="Select Difficulty", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.master, text="Easy (9x9, 10 Mines)", command=lambda: self.start_game(9, 10)).pack(pady=5)
        tk.Button(self.master, text="Medium (9x9, 20 Mines)", command=lambda: self.start_game(9, 20)).pack(pady=5)
        tk.Button(self.master, text="Hard (16x16, 40 Mines)", command=lambda: self.start_game(16, 40)).pack(pady=5)

    def start_game(self, grid_size, mines_count):
        self.grid_size = grid_size
        self.mines_count = mines_count
        self.flags_count = 0  # Reset flags on new game
        self.init_game()

    def init_game(self):
        self.board = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.buttons = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.revealed = [[False for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.flagged = [[False for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.move_history = []
        self.game_over = False
        self.auto_solve_steps = []

        for widget in self.master.winfo_children():
            widget.destroy()

        self.create_widgets()
        self.place_mines()
        self.calculate_numbers()

    def create_widgets(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                btn = tk.Button(self.master, text='', width=4, height=2,
                                command=lambda x=i, y=j: self.reveal(x, y))
                btn.grid(row=i, column=j)
                btn.bind("<Button-3>", lambda event, x=i, y=j: self.toggle_flag(event, x, y))  # Right-click event
                self.buttons[i][j] = btn

        control_frame = tk.Frame(self.master)
        control_frame.grid(row=self.grid_size, column=0, columnspan=self.grid_size)

        tk.Button(control_frame, text="Auto Solve", command=self.auto_solve).grid(row=0, column=0, padx=5)
        tk.Button(control_frame, text="Hint", command=self.give_hint).grid(row=0, column=1, padx=5)
        tk.Button(control_frame, text="Undo", command=self.undo_move).grid(row=0, column=2, padx=5)
        tk.Button(control_frame, text="Restart", command=self.restart_game).grid(row=0, column=3, padx=5)
        tk.Button(control_frame, text="Rules", command=self.show_rules).grid(row=0, column=4, padx=5)

    def place_mines(self):
        count = 0
        while count < self.mines_count:
            x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
            if self.board[x][y] != -1:
                self.board[x][y] = -1
                count += 1

    def calculate_numbers(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == -1:
                    continue
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < self.grid_size and 0 <= nj < self.grid_size and self.board[ni][nj] == -1:
                            count += 1
                self.board[i][j] = count

    def reveal(self, x, y):
        if self.game_over or self.revealed[x][y] or self.flagged[x][y]:
            return
        self.move_history.append((x, y, self.revealed[x][y]))  # Store previous state for undo
        self._reveal_cell_bfs(x, y)
        self.check_win()

    def _reveal_cell_bfs(self, x, y):
        queue = deque([(x, y)])

        while queue:
            cx, cy = queue.popleft()

            if self.revealed[cx][cy]:
                continue

            self.revealed[cx][cy] = True
            val = self.board[cx][cy]

            if val == -1:
                self.buttons[cx][cy].config(text='*', bg='red')
                self.game_over = True
                self.show_all_mines()
                return

            self.buttons[cx][cy].config(text=str(val) if val > 0 else '', bg='lightgrey')

            if val == 0:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and not self.revealed[nx][ny]:
                            queue.append((nx, ny))

    def show_all_mines(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == -1:
                    self.buttons[i][j].config(text='*', bg='red')

    def check_win(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] != -1 and not self.revealed[i][j]:
                    return
        self.show_win_window()

    def show_win_window(self):
        win_window = tk.Toplevel(self.master)
        win_window.title("You Win!")
        tk.Label(win_window, text="🎉 Congratulations!🎉 \n You won the game! ", padx=20, pady=20).pack()
        tk.Button(win_window, text="Close", command=win_window.destroy).pack(pady=10)

    def toggle_flag(self, event, x, y):
        if self.game_over or self.revealed[x][y]:
            return

        if self.flagged[x][y]:
            self.flagged[x][y] = False
            self.buttons[x][y].config(text='', bg='SystemButtonFace')
            self.flags_count -= 1
        else:
            if self.flags_count < self.mines_count:
                self.flagged[x][y] = True
                self.buttons[x][y].config(text='🚩', bg='lightyellow')
                self.flags_count += 1

    def give_hint(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if not self.revealed[i][j] and self.board[i][j] != -1:
                    self.reveal(i, j)
                    return

    def undo_move(self):
        if self.move_history:
            x, y, _ = self.move_history.pop()
            self.revealed[x][y] = False
            self.buttons[x][y].config(text='', bg='SystemButtonFace')

            if self.board[x][y] == -1 and self.game_over:
                self.game_over = False
                for i in range(self.grid_size):
                    for j in range(self.grid_size):
                        if self.board[i][j] == -1 and not self.revealed[i][j]:
                            self.buttons[i][j].config(text='', bg='SystemButtonFace')

    def auto_solve(self):
        """Starts the step-by-step auto-solve process."""
        # Initialize the queue for BFS
        self.auto_solve_queue = deque()

        # Add all unrevealed safe cells to the queue
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if not self.revealed[i][j] and not self.flagged[i][j] and self.board[i][j] != -1:
                    self.auto_solve_queue.append((i, j))

        # Start the step-by-step solving process
        self._auto_solve_step()

    def _auto_solve_step(self):
        """Processes one step in the BFS auto-solve."""
        if not self.auto_solve_queue:
            # No more steps, check for win
            self.check_win()
            return

        # Get the next cell to process
        x, y = self.auto_solve_queue.popleft()

        # Skip already revealed or flagged cells
        if self.revealed[x][y] or self.flagged[x][y]:
            self.master.after(100, self._auto_solve_step)  # Schedule the next step
            return

        # Reveal the current cell
        self._reveal_cell_bfs(x, y)

        # If the cell is a "clear zone" (0), add its neighbors to the queue
        if self.board[x][y] == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and not self.revealed[nx][ny]:
                        self.auto_solve_queue.append((nx, ny))

        # Schedule the next step with a delay
        self.master.after(100, self._auto_solve_step)

    def restart_game(self):
        self.init_game()

    def show_rules(self):
        top = tk.Toplevel(self.master)
        top.title("Rules")
        rules_text = (
            "🎮 Minesweeper Rules:\n\n"
            "1. Click to reveal a cell.\n"
            "2. Numbers = adjacent mines.\n"
            "3. 0 = clear zone, reveals nearby.\n"
            "4. Hitting a mine ends the game.\n"
            "5. Goal: reveal all safe cells.\n"
            "6. Right-click to flag a cell.\n"
            "7. Flag all mines to win."
        )
        tk.Label(top, text=rules_text, justify="left", padx=10, pady=10).pack()
        tk.Button(top, text="Close", command=top.destroy).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()
