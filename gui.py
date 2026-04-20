import tkinter as tk
from tkinter import ttk, messagebox
import os
import time

from src.core.io_handler import read_input_file
from src.core.rules import FutoshikiRules
from src.core.state import State 
from src.solver.Astar import AstarSolver
from src.solver.Backtracking import BacktrackingSolver
from src.solver.Bruteforce import BruteForceSolver
from src.solver.ForwardChaining import ForwardChainingSolver

class FutoshikiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Futoshiki Puzzle Solver")
        self.root.geometry("900x650")
        self.root.configure(padx=20, pady=20)

        # Main Layout Frames
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(fill=tk.X, pady=(0, 20))

        self.display_frame = tk.Frame(root)
        self.display_frame.pack(fill=tk.BOTH, expand=True)

        self.setup_controls()
        self.setup_displays()

    def setup_controls(self):
        # 1. Test Case Selector
        tk.Label(self.control_frame, text="Select Test Case:", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.input_files = self.get_input_files()
        self.test_combo = ttk.Combobox(self.control_frame, values=self.input_files, state="readonly", width=25)
        if self.input_files:
            self.test_combo.current(0)
        self.test_combo.pack(side=tk.LEFT, padx=(0, 30))
        self.test_combo.bind("<<ComboboxSelected>>", self.preview_input)

        # 2. Algorithm Selector
        tk.Label(self.control_frame, text="Algorithm:", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.algorithms = ["A* Search", "Backtracking", "Brute-force", "Forward Chaining"]
        self.algo_combo = ttk.Combobox(self.control_frame, values=self.algorithms, state="readonly", width=20)
        self.algo_combo.current(0)
        self.algo_combo.pack(side=tk.LEFT, padx=(0, 30))

        # 3. Solve Button
        self.solve_btn = tk.Button(self.control_frame, text="Solve Puzzle", bg="#4CAF50", fg="white", 
                                   font=("Arial", 11, "bold"), command=self.run_solver)
        self.solve_btn.pack(side=tk.LEFT)

        # Status Label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        tk.Label(self.control_frame, textvariable=self.status_var, fg="blue").pack(side=tk.RIGHT)

    def setup_displays(self):
        # Left side: Input Grid
        input_frame = tk.Frame(self.display_frame)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        tk.Label(input_frame, text="Initial State", font=("Arial", 12, "bold")).pack()
        self.txt_input = tk.Text(input_frame, font=("Courier New", 14), state=tk.DISABLED, bg="#f4f4f4")
        self.txt_input.pack(fill=tk.BOTH, expand=True)

        # Right side: Solved Grid
        output_frame = tk.Frame(self.display_frame)
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        tk.Label(output_frame, text="Solved State", font=("Arial", 12, "bold")).pack()
        self.txt_output = tk.Text(output_frame, font=("Courier New", 14), state=tk.DISABLED, bg="#e8f5e9")
        self.txt_output.pack(fill=tk.BOTH, expand=True)

    def get_input_files(self):
        """Scans the 'Inputs' directory for text files."""
        input_dir = "Inputs"
        if not os.path.exists(input_dir):
            return []
        files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
        return sorted(files)

    def preview_input(self, event=None):
        """Loads and displays the selected input file."""
        filename = self.test_combo.get()
        if not filename: return
        
        filepath = os.path.join("Inputs", filename)
        try:
            n, grid, h_const, v_const = read_input_file(filepath)
            formatted_str = self.format_grid_to_string(n, grid, h_const, v_const)
            
            self.txt_input.config(state=tk.NORMAL)
            self.txt_input.delete(1.0, tk.END)
            self.txt_input.insert(tk.END, formatted_str)
            self.txt_input.config(state=tk.DISABLED)
            
            self.txt_output.config(state=tk.NORMAL)
            self.txt_output.delete(1.0, tk.END)
            self.txt_output.config(state=tk.DISABLED)
            self.status_var.set(f"Loaded: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{e}")

    def format_grid_to_string(self, n, grid, horiz_const, vert_const):
        """Adapts your write_output_file logic to output a string for the GUI."""
        lines = []
        for i in range(n):
            row_str = ""
            for j in range(n):
                val = str(grid[i][j]) if grid[i][j] != 0 else "."
                row_str += val
                if j < n - 1:
                    h_val = horiz_const[i][j]
                    if h_val == 1:
                        row_str += " < "
                    elif h_val == -1:
                        row_str += " > "
                    else:
                        row_str += "   "
            lines.append(row_str)
            
            if i < n - 1:
                vert_str = ""
                for j in range(n):
                    v_val = vert_const[i][j]
                    if v_val == 1:
                        vert_str += "^" 
                    elif v_val == -1:
                        vert_str += "v" 
                    else:
                        vert_str += " "
                    
                    if j < n - 1:
                        vert_str += "   "
                lines.append(vert_str)
        return "\n".join(lines)

    def run_solver(self):
        filename = self.test_combo.get()
        if not filename:
            messagebox.showwarning("Warning", "Please select an input file first.")
            return

        algo_choice = self.algo_combo.get()
        filepath = os.path.join("Inputs", filename)
        
        try:
            n, grid, h_const, v_const = read_input_file(filepath)
            rules = FutoshikiRules(n, h_const, v_const)

            initial_state = State(n, grid, rules)

            solver = None
            if algo_choice == "A* Search":
                solver = AstarSolver() 
            elif algo_choice == "Backtracking":
                 solver = BacktrackingSolver(rules)
            elif algo_choice == "Brute-force":
                solver = BruteForceSolver(rules)
            elif algo_choice == "Forward Chaining":
                solver = ForwardChainingSolver(rules)
            else:
                messagebox.showinfo("Info", f"{algo_choice} is not yet hooked up to the GUI.")
                return

            self.status_var.set("Solving...")
            self.root.update()

            start_time = time.time()
            
            final_grid = None
            
            if algo_choice == "A* Search":
                path = solver.solve(initial_state, rules)
                if path:
                    final_grid = path[-1] 
            elif algo_choice == "Brute-force":
                grid_copy = [row[:] for row in grid]
                final_grid = solver.solve(grid_copy)
            else:
                final_grid = solver.solve(initial_state)

            end_time = time.time()

            if final_grid:
                formatted_str = self.format_grid_to_string(n, final_grid, h_const, v_const)
                
                self.txt_output.config(state=tk.NORMAL)
                self.txt_output.delete(1.0, tk.END)
                self.txt_output.insert(tk.END, formatted_str)
                self.txt_output.config(state=tk.DISABLED)
                
                elapsed = round((end_time - start_time) * 1000, 2)
                self.status_var.set(f"Solved in {elapsed} ms")
            else:
                self.status_var.set("No solution found.")
                messagebox.showinfo("Result", "The puzzle could not be solved.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during solving:\n{e}")
if __name__ == "__main__":
    root = tk.Tk()
    app = FutoshikiGUI(root)
    if app.input_files:
        app.preview_input()
    root.mainloop()