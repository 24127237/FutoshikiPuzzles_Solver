import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
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

        self.solver_thread = None  
        self.result = None
        
        # Thiết lập kích thước tối thiểu và cho phép co giãn
        self.root.minsize(800, 600)
        self.root.geometry("900x650")
        
        # Cấu hình grid cho root để các frame bên trong có thể scale
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # 1. Control Frame (Phía trên)
        self.control_frame = tk.Frame(self.root, pady=10)
        self.control_frame.grid(row=0, column=0, sticky="ew", padx=20)

        # 2. Display Frame (Phía dưới - Chiếm toàn bộ diện tích còn lại)
        self.display_frame = tk.Frame(self.root)
        self.display_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Cấu hình tỉ lệ 1:1 cho 2 cột Input và Output
        self.display_frame.columnconfigure(0, weight=1)
        self.display_frame.columnconfigure(1, weight=1)
        self.display_frame.rowconfigure(1, weight=1)

        self.setup_controls()
        self.setup_displays()

    def setup_controls(self):
        # Frame phụ bên trong để chứa các widget theo hàng ngang
        inner_ctrl = tk.Frame(self.control_frame)
        inner_ctrl.pack(fill=tk.X)

        tk.Label(inner_ctrl, text="Test Case:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.input_files = self.get_input_files()
        self.test_combo = ttk.Combobox(inner_ctrl, values=self.input_files, state="readonly", width=20)
        if self.input_files: self.test_combo.current(0)
        self.test_combo.pack(side=tk.LEFT, padx=5)
        self.test_combo.bind("<<ComboboxSelected>>", self.preview_input)

        tk.Label(inner_ctrl, text="Algo:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.algorithms = ["A* Search", "Backtracking", "Brute-force", "Forward Chaining"]
        self.algo_combo = ttk.Combobox(inner_ctrl, values=self.algorithms, state="readonly", width=15)
        self.algo_combo.current(0)
        self.algo_combo.pack(side=tk.LEFT, padx=5)

        self.solve_btn = tk.Button(inner_ctrl, text="SOLVE", bg="#4CAF50", fg="white", 
                                   font=("Arial", 10, "bold"), command=self.run_solver, padx=10)
        self.solve_btn.pack(side=tk.LEFT, padx=10)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(inner_ctrl, textvariable=self.status_var, fg="blue", font=("Arial", 10, "italic")).pack(side=tk.RIGHT)

    def setup_displays(self):
        # Cột trái: Initial State
        tk.Label(self.display_frame, text="Initial State", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w")
        self.txt_input = tk.Text(self.display_frame, font=("Courier New", 12), bg="#f8f9fa", height=10)
        self.txt_input.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        # Cột phải: Solved State
        tk.Label(self.display_frame, text="Solved State", font=("Arial", 11, "bold")).grid(row=0, column=1, sticky="w")
        self.txt_output = tk.Text(self.display_frame, font=("Courier New", 12), bg="#e8f5e9", height=10)
        self.txt_output.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

    def get_input_files(self):
        input_dir = "Inputs"
        if not os.path.exists(input_dir): return []
        return sorted([f for f in os.listdir(input_dir) if f.endswith('.txt')])

    def preview_input(self, event=None):
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
            messagebox.showerror("Error", f"Could not read file: {e}")

    def format_grid_to_string(self, n, grid, horiz_const, vert_const):
        lines = []
        for i in range(n):
            row_str = ""
            for j in range(n):
                val = str(grid[i][j]) if grid[i][j] != 0 else "."
                row_str += val
                if j < n - 1:
                    h_val = horiz_const[i][j]
                    row_str += " < " if h_val == 1 else " > " if h_val == -1 else "   "
            lines.append(row_str)
            if i < n - 1:
                vert_str = ""
                for j in range(n):
                    v_val = vert_const[i][j]
                    vert_str += "^" if v_val == 1 else "v" if v_val == -1 else " "
                    if j < n - 1: vert_str += "   "
                lines.append(vert_str)
        return "\n".join(lines)

    def run_solver(self):
        filename = self.test_combo.get()
        if not filename: return

        algo_choice = self.algo_combo.get()
        filepath = os.path.join("Inputs", filename)
        
        try:
            n, grid, h_const, v_const = read_input_file(filepath)
            rules = FutoshikiRules(n, h_const, v_const)
            
            # Khởi tạo solver dựa trên lựa chọn
            if algo_choice == "Brute-force":
                solver = BruteForceSolver(rules, limit=1000000) # Giới hạn 1 triệu nodes
            elif algo_choice == "Backtracking":
                solver = BacktrackingSolver(rules)
            elif algo_choice == "A* Search":
                solver = AstarSolver()
            else:
                solver = ForwardChainingSolver(rules)

            # 1. Chuẩn bị giao diện trước khi chạy
            self.solve_btn.config(state=tk.DISABLED) # Khóa nút Solve
            self.status_var.set("Solving (Background)...")
            self.txt_output.config(state=tk.NORMAL)
            self.txt_output.delete(1.0, tk.END)
            self.txt_output.config(state=tk.DISABLED)
            
            self.result = None
            start_time = time.time()

            # 2. Hàm bao để chạy trong Thread
            def worker():
                try:
                    if algo_choice == "A* Search":
                        path = solver.solve(State(n, grid, rules), rules)
                        self.result = path[-1] if path else None
                    elif algo_choice == "Brute-force":
                        self.result = solver.solve([row[:] for row in grid])
                    else:
                        self.result = solver.solve(State(n, grid, rules))
                except Exception as e:
                    self.result = e # Lưu lỗi nếu có

            # 3. Kích hoạt Thread
            self.solver_thread = threading.Thread(target=worker)
            self.solver_thread.daemon = True # Thread sẽ tự đóng nếu tắt App
            self.solver_thread.start()

            # 4. Bắt đầu vòng lặp kiểm tra trạng thái (Polling)
            self.monitor_thread(start_time, n, h_const, v_const)

        except Exception as e:
            messagebox.showerror("Error", f"Lỗi khởi tạo: {e}")

    def monitor_thread(self, start_time, n, h_const, v_const):
        """Hàm này chạy trên Main Thread để kiểm tra khi nào Worker Thread xong."""
        if self.solver_thread.is_alive():
            # Nếu vẫn đang chạy, hẹn 100ms sau quay lại kiểm tra tiếp
            self.root.after(100, lambda: self.monitor_thread(start_time, n, h_const, v_const))
        else:
            # Thread đã chạy xong!
            self.solve_btn.config(state=tk.NORMAL) # Mở khóa nút Solve
            end_time = time.time()
            elapsed = round((end_time - start_time) * 1000, 2)

            if isinstance(self.result, Exception):
                messagebox.showerror("Error", f"Lỗi trong lúc giải: {self.result}")
            elif self.result == "LIMIT_EXCEEDED":
                self.status_var.set("Limit Exceeded!")
                messagebox.showwarning("Unsolvable", "Brute-force quá tải. Hãy thử các thuật toán khác!")
            elif self.result:
                formatted_str = self.format_grid_to_string(n, self.result, h_const, v_const)
                self.txt_output.config(state=tk.NORMAL)
                self.txt_output.insert(tk.END, formatted_str)
                self.txt_output.config(state=tk.DISABLED)
                self.status_var.set(f"Solved in {elapsed} ms")
            else:
                self.status_var.set("No solution.")
                messagebox.showinfo("Result", "Không tìm thấy lời giải.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FutoshikiGUI(root)
    if app.input_files: app.preview_input()
    root.mainloop()