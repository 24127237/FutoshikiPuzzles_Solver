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
        self.canvas_input = tk.Canvas(self.display_frame, bg="#f8f9fa", highlightthickness=1, highlightbackground="gray")
        self.canvas_input.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        # Ràng buộc sự kiện Configure để vẽ lại khi thay đổi kích thước
        self.canvas_input.bind("<Configure>", lambda e: self.redraw_input())

        # Cột phải: Solved State
        tk.Label(self.display_frame, text="Solved State", font=("Arial", 11, "bold")).grid(row=0, column=1, sticky="w")
        self.canvas_output = tk.Canvas(self.display_frame, bg="#e8f5e9", highlightthickness=1, highlightbackground="gray")
        self.canvas_output.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        self.canvas_output.bind("<Configure>", lambda e: self.redraw_output())
        
        self.current_puzzle = None
        self.current_result = None

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
            self.current_puzzle = (n, grid, h_const, v_const)
            self.current_result = None
            
            self.redraw_input()
            self.canvas_output.delete("all")
            
            self.status_var.set(f"Loaded: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")

    def redraw_input(self):
        if hasattr(self, 'current_puzzle') and self.current_puzzle:
            self.draw_grid_on_canvas(self.canvas_input, *self.current_puzzle, is_result=False)
            
    def redraw_output(self):
        if hasattr(self, 'current_result') and self.current_result and hasattr(self, 'current_puzzle'):
            n, _, h_const, v_const = self.current_puzzle
            self.draw_grid_on_canvas(self.canvas_output, n, self.current_result, h_const, v_const, is_result=True)

    def draw_grid_on_canvas(self, canvas, n, grid, h_const, v_const, is_result=False):
        canvas.delete("all")
        if n == 0: return
        
        canvas.update_idletasks()
        c_width = canvas.winfo_width()
        c_height = canvas.winfo_height()
        
        if c_width < 10 or c_height < 10:
            c_width, c_height = 400, 400

        margin = 20
        cell_size = min((c_width - 2*margin) / (n + (n-1)*0.5), (c_height - 2*margin) / (n + (n-1)*0.5))
        if cell_size <= 0: cell_size = 30
        
        spacing = cell_size * 0.5
        
        start_x = (c_width - (n * cell_size + (n-1) * spacing)) / 2
        start_y = (c_height - (n * cell_size + (n-1) * spacing)) / 2
        
        for i in range(n):
            for j in range(n):
                x = start_x + j * (cell_size + spacing)
                y = start_y + i * (cell_size + spacing)
                
                val = grid[i][j]
                bg_color = "white" if val == 0 else ("#c8e6c9" if is_result else "#bbdefb")
                canvas.create_rectangle(x, y, x + cell_size, y + cell_size, fill=bg_color, outline="black", width=2)
                
                if val != 0:
                    canvas.create_text(x + cell_size/2, y + cell_size/2, text=str(val), font=("Arial", int(cell_size/2.5), "bold"))
                    
                if j < n - 1:
                    h_val = h_const[i][j]
                    if h_val != 0:
                        text = "<" if h_val == 1 else ">"
                        canvas.create_text(x + cell_size + spacing/2, y + cell_size/2, text=text, font=("Arial", int(cell_size/2.5), "bold"), fill="red")
                        
                if i < n - 1:
                    v_val = v_const[i][j]
                    if v_val != 0:
                        text = "^" if v_val == 1 else "v"
                        canvas.create_text(x + cell_size/2, y + cell_size + spacing/2, text=text, font=("Arial", int(cell_size/2.5), "bold"), fill="red")

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
            self.canvas_output.delete("all")
            self.current_result = None
            
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
                self.current_result = self.result
                self.redraw_output()
                self.status_var.set(f"Solved in {elapsed} ms")
            else:
                self.status_var.set("No solution.")
                messagebox.showinfo("Result", "Không tìm thấy lời giải.")
