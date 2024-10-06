import numpy as np
import customtkinter as ctk


class GameOfLife:
    def __init__(self, grid_size=(50, 100)):
        self.grid_size = grid_size
        self.grid = np.zeros(self.grid_size, dtype=int)
        self.initial_grid = np.zeros(self.grid_size, dtype=int)
        self.history = []
        self.redo_stack = []

    def update(self):
        new_grid = np.copy(self.grid)
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                total = int(np.sum(self.grid[i-1:i+2, j-1:j+2]) - self.grid[i, j])
                if self.grid[i, j] == 1 and (total < 2 or total > 3):
                    new_grid[i, j] = 0
                elif self.grid[i, j] == 0 and total == 3:
                    new_grid[i, j] = 1
        self.grid = new_grid

    def place_cell(self, row, col):
        self.save_state()
        self.grid[row, col] = 1

    def clear_grid(self):
        self.grid = np.zeros(self.grid_size, dtype=int)  # Reset grid to all zeros
        self.save_state()  # Save this state for undo functionality

    def save_initial_state(self):
        self.initial_grid = np.copy(self.grid)

    def restore_initial_state(self):
        self.grid = np.copy(self.initial_grid)

    def save_state(self):
        self.history.append(np.copy(self.grid))
        self.redo_stack.clear()

    def undo(self):
        if self.history:
            self.redo_stack.append(np.copy(self.grid))
            self.grid = self.history.pop()

    def redo(self):
        if self.redo_stack:
            self.history.append(np.copy(self.grid))
            self.grid = self.redo_stack.pop()


class GameOfLifeGUI(ctk.CTk):
    def __init__(self, game):
        super().__init__()
        self.title("Conway's Game of Life")
        self.game = game
        self.cell_size = 10
        self.simulating = False
        self.bg_color = '#ffffff'
        self.cell_color = '#007BFF'
        self.dragging = False
        self.simulation_speed = 20  # Initialize simulation speed here
        self.configure_grid()

    def configure_grid(self):
        self.canvas = ctk.CTkCanvas(self, width=self.game.grid_size[1] * self.cell_size,
                                     height=self.game.grid_size[0] * self.cell_size, bg=self.bg_color)
        self.canvas.pack(padx=20, pady=20)

        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10)

        self.create_buttons()
        self.create_speed_slider()

        self.update_canvas()

    def create_buttons(self):
        buttons = [("Start Simulation", self.start_simulation),
                   ("Stop Simulation", self.stop_simulation),
                   ("Reset to Initial State", self.reset_to_initial_state),
                   ("Clear", self.clear_grid),  # Add Clear button
                   ("Undo", self.undo),
                   ("Redo", self.redo)]
        
        for i, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(self.button_frame, text=text, command=command, width=120)
            btn.grid(row=0, column=i, padx=10, pady=5)

    def create_speed_slider(self):
        self.speed_slider = ctk.CTkSlider(self.button_frame, from_=1, to=100, command=self.update_speed)
        self.speed_slider.set(50)  # Set the initial value of the slider
        self.speed_slider.grid(row=1, column=0, columnspan=5, padx=10, pady=10)
        self.speed_label = ctk.CTkLabel(self.button_frame, text="Speed")
        self.speed_label.grid(row=2, column=0, columnspan=5)

    def update_speed(self, value):
        self.simulation_speed = 1000 / float(value)  # Speed control based on slider

    def start_drag(self, event):
        self.dragging = True
        self.place_cell(event)

    def drag(self, event):
        if self.dragging:
            self.place_cell(event)

    def stop_drag(self, event):
        self.dragging = False

    def place_cell(self, event):
        row = event.y // self.cell_size
        col = event.x // self.cell_size
        if 0 <= row < self.game.grid_size[0] and 0 <= col < self.game.grid_size[1]:
            self.game.place_cell(row, col)
            self.update_canvas()

    def update_canvas(self):
        self.canvas.delete("all")
        for i in range(self.game.grid_size[0]):
            for j in range(self.game.grid_size[1]):
                if self.game.grid[i, j] == 1:
                    x1 = j * self.cell_size
                    y1 = i * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.cell_color, outline='')

    def start_simulation(self):
        self.game.save_initial_state()
        if not self.simulating:
            self.simulating = True
            self.animate()

    def stop_simulation(self):
        self.simulating = False

    def reset_to_initial_state(self):
        self.game.restore_initial_state()
        self.update_canvas()

    def clear_grid(self):
        self.game.clear_grid()  # Clear the grid
        self.update_canvas()

    def undo(self):
        self.game.undo()
        self.update_canvas()

    def redo(self):
        self.game.redo()
        self.update_canvas()

    def animate(self):
        if self.simulating:
            self.game.update()
            self.update_canvas()
            self.after(int(self.simulation_speed), self.animate)

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    gol = GameOfLife(grid_size=(50, 100))
    gui = GameOfLifeGUI(gol)
    gui.mainloop()
