import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import threading
import time
from src.core.io_handler import read_input_file
from src.core.rules import FutoshikiRules
from src.core.state import State 
from src.solver.Astar import AstarSolver
from src.solver.Backtracking import BacktrackingSolver
from src.solver.Bruteforce import BruteForceSolver
from src.solver.FCHybrid import FCHybridSolver

class FutoshikiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Futoshiki Puzzle Solver")

        self.solver_thread = None
        self.result = None

        self.selection_start = None
        self.selected_cells = []
        self.last_cell_size = None
        self.last_spacing = None
        self.last_start_x = None
        self.last_start_y = None
        
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
        self.display_frame.columnconfigure(2, weight=0)
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
        self.canvas_input.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(0, 0))
        self.canvas_input.bind("<Configure>", lambda e: self.redraw_input())
        self.canvas_input.bind("<Button-1>", self.canvas_click)
        self.canvas_input.bind("<B1-Motion>", self.canvas_drag)

        # Cột giữa: Solved State
        tk.Label(self.display_frame, text="Solved State", font=("Arial", 11, "bold")).grid(row=0, column=1, sticky="w")
        self.canvas_output = tk.Canvas(self.display_frame, bg="#e8f5e9", highlightthickness=1, highlightbackground="gray")
        self.canvas_output.grid(row=1, column=1, sticky="nsew", padx=(5, 5), pady=(0, 0))
        self.canvas_output.bind("<Configure>", lambda e: self.redraw_output())

        # Sidebar: Inference Tree và Log
        tk.Label(self.display_frame, text="Inference Trace", font=("Arial", 11, "bold")).grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.sidebar_frame = tk.Frame(self.display_frame, padx=10, pady=5)
        self.sidebar_frame.grid(row=1, column=2, sticky="nsew", padx=(10, 0))
        self.sidebar_frame.columnconfigure(0, weight=1)
        self.sidebar_frame.rowconfigure(3, weight=1)

        tk.Label(self.sidebar_frame, text="Inference Tree (Backward Chaining Trace):").grid(row=0, column=0, sticky="w")
        self.tree = ttk.Treeview(self.sidebar_frame, columns=("Status",), height=10)
        self.tree.heading("#0", text="Step / Hypothesis")
        self.tree.heading("Status", text="Result")
        self.tree.grid(row=1, column=0, sticky="nsew", pady=5)

        tk.Label(self.sidebar_frame, text="Detailed Log:").grid(row=2, column=0, sticky="w")
        self.log = scrolledtext.ScrolledText(self.sidebar_frame, height=8, state='disabled')
        self.log.grid(row=3, column=0, sticky="nsew", pady=5)

        self.btn_infer = tk.Button(self.sidebar_frame, text="Run Inference", 
                                   command=self.run_backward_chaining, bg="#4CAF50", fg="white")
        self.btn_clear = tk.Button(self.sidebar_frame, text="Clear Log", 
                                   command=self.clear_log, bg="#f44336", fg="white")

        self.btn_infer.grid(row=4, column=0, sticky="ew", pady=10)
        self.btn_clear.grid(row=5, column=0, sticky="ew", pady=5)

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
            self.selected_cells = []
            self.selection_start = None
            self.last_cell_size = None
            self.last_spacing = None
            self.last_start_x = None
            self.last_start_y = None
            
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
        canvas.delete("all")  # Xóa sạch để vẽ lại từ đầu (chỉ dùng khi load bài mới hoặc resize)
        if n == 0: return
        
        canvas.update_idletasks()
        c_width = canvas.winfo_width()
        c_height = canvas.winfo_height()
        if c_width < 10: c_width, c_height = 400, 400 # Mặc định nếu chưa render

        margin = 20
        cell_size = min((c_width - 2*margin) / (n + (n-1)*0.5), (c_height - 2*margin) / (n + (n-1)*0.5))
        spacing = cell_size * 0.5
        start_x = (c_width - (n * cell_size + (n-1) * spacing)) / 2
        start_y = (c_height - (n * cell_size + (n-1) * spacing)) / 2
        
        # Lưu lại thông số để dùng cho việc tính tọa độ chuột và vẽ overlay
        if canvas == self.canvas_input:
            self.last_cell_size, self.last_spacing = cell_size, spacing
            self.last_start_x, self.last_start_y = start_x, start_y

        for i in range(n):
            for j in range(n):
                x = start_x + j * (cell_size + spacing)
                y = start_y + i * (cell_size + spacing)
                
                # --- 1. Vẽ ô lưới (Rectangle) ---
                canvas.create_rectangle(x, y, x + cell_size, y + cell_size, 
                                        fill="white", outline="black", width=1)
                
                # --- 2. Vẽ con số (Nếu có) ---
                val = grid[i][j]
                if val != 0:
                    canvas.create_text(x + cell_size/2, y + cell_size/2, 
                                       text=str(val), font=("Arial", int(cell_size/2), "bold"))

                # --- 3. Vẽ dấu so sánh ngang (< >) ---
                if j < n - 1:
                    h_val = h_const[i][j]
                    if h_val != 0:
                        txt = "<" if h_val == 1 else ">"
                        canvas.create_text(x + cell_size + spacing/2, y + cell_size/2, 
                                           text=txt, font=("Arial", int(cell_size/3), "bold"), fill="red")
                        
                # --- 4. Vẽ dấu so sánh dọc (^ v) ---
                if i < n - 1:
                    v_val = v_const[i][j]
                    if v_val != 0:
                        txt = "^" if v_val == 1 else "v"
                        canvas.create_text(x + cell_size/2, y + cell_size + spacing/2, 
                                           text=txt, font=("Arial", int(cell_size/3), "bold"), fill="red")

        # Vẽ lại vùng chọn nếu có (dùng tag để sau này update ko bị lag)
        if canvas == self.canvas_input:
            self.update_selection_highlight()

    # --- Logic Chọn Range ---
    
    def get_cell_from_event(self, event):
        if not self.current_puzzle or self.last_cell_size is None:
            return None

        n, _, _, _ = self.current_puzzle
        x = event.x - self.last_start_x
        y = event.y - self.last_start_y
        if x < 0 or y < 0:
            return None

        step = self.last_cell_size + self.last_spacing
        col = int(x / step)
        row = int(y / step)
        if row < 0 or col < 0 or row >= n or col >= n:
            return None

        x_in = x - col * step
        y_in = y - row * step
        if x_in > self.last_cell_size or y_in > self.last_cell_size:
            return None

        return row, col

    def canvas_click(self, event):
        cell = self.get_cell_from_event(event)
        if not cell:
            return
        self.selection_start = cell
        self.selected_cells = [cell]
        self.redraw_input()

    def canvas_drag(self, event):
        if self.selection_start is None: return
        cell = self.get_cell_from_event(event)
        if not cell: return

        r_start, c_start = self.selection_start
        r_end, c_end = cell
        
        # Chỉ tính toán lại vùng chọn
        new_selection = [
            (r, c)
            for r in range(min(r_start, r_end), max(r_start, r_end) + 1)
            for c in range(min(c_start, c_end), max(c_start, c_end) + 1)
        ]
        
        if new_selection != self.selected_cells:
            self.selected_cells = new_selection
            self.update_selection_highlight() # Cập nhật lớp phủ, không vẽ lại cả bảng

    def update_selection_highlight(self):
        # Xóa duy nhất những đối tượng có tag "selection_overlay"
        self.canvas_input.delete("selection_overlay")
        
        for r, c in self.selected_cells:
            x = self.last_start_x + c * (self.last_cell_size + self.last_spacing)
            y = self.last_start_y + r * (self.last_cell_size + self.last_spacing)
            self.canvas_input.create_rectangle(
                x, y, x + self.last_cell_size, y + self.last_cell_size,
                fill="#ADD8E6", stipple="gray25", outline="#1976D2", width=2,
                tags="selection_overlay" # Đánh dấu để xóa chính xác lần sau
            )
    def clear_selection(self):
        self.selected_cells = []
        self.selection_start = None
        self.redraw_input()

    # --- Logic Inference & Trace ---
    def write_log(self, message):
        self.log.config(state='normal')
        self.log.insert(tk.END, f"> {message}\n")
        self.log.see(tk.END)
        self.log.config(state='disabled')

    def clear_log(self):
        self.log.config(state='normal')
        self.log.delete(1.0, tk.END)
        self.log.config(state='disabled')
    def run_backward_chaining(self):
        if not self.selected_cells:
            self.write_log("Cảnh báo: Hãy quét chọn một vùng ô trước!")
            return
        if not self.current_puzzle:
            self.write_log("Cảnh báo: Chưa có bài toán được tải.")
            return

        self.btn_infer.config(state=tk.DISABLED)
        # Remove demo inference and callback from sld_resolve
        self.status_var.set("Running inference...")
        threading.Thread(target=self.bc_inference, daemon=True).start()
    
    def bc_inference(self):
        n, grid, h_const, v_const = self.current_puzzle
        from src.core.fol_kb import build_kb
        from src.solver.PureBackwardChaining import sld_resolve, query_cells
        from src.core.fol_types import Number

        # 1. Lấy tọa độ ô đầu tiên trong vùng chọn
        r, c = self.selected_cells[0]
        new_r, new_c = r + 1, c + 1  # Chuyển sang 1-based index cho FOL
        
        # 2. Khởi tạo Knowledge Base và sử dụng query_cells để tạo goals cho 1 ô
        kb = build_kb(n, grid, h_const, v_const)
        goals, qvar = query_cells(n, r, c, grid, h_const, v_const)
        
        # Xóa Treeview cũ
        self.root.after(0, lambda: self.tree.delete(*self.tree.get_children()))
        self.root.after(0, lambda: self.write_log(f"--- Query Cell: ({new_r}, {new_c}) ---"))

        possible_values = set()

        def trace_callback(event_type, msg, subst=None):
            def _ui_update():
                if event_type == "CHECK_CELL":
                    # Log: Checking goal: ...
                    self.write_log(f"Checking goal: {msg}")
                elif event_type == "TRY_VALUE":
                    self.write_log(f"  Step: test value: {msg}")
                    self.tree.insert("", "end", text=f"Try: {msg}", values=("",))
                
                elif event_type == "CONFLICT":
                    # Log: Result: Conflict
                    self.write_log(f"  {msg}")
                    # Cập nhật trạng thái cho node cuối cùng trên cây
                    nodes = self.tree.get_children()
                    if nodes: self.tree.item(nodes[-1], values=("Conflict, backtracking",))
                
                elif event_type == "SUCCESS":
                    # Log: Result: Success
                    self.write_log(f"  Success: {msg}")
                    # Cập nhật trạng thái cho node cuối cùng trên cây
                    nodes = self.tree.get_children()
                    if nodes: self.tree.item(nodes[-1], values=("Success",))
                    if subst is not None:
                        bound_term = qvar.walk(subst)
                        if isinstance(bound_term, Number):
                            possible_values.add(bound_term.value)

            self.root.after(0, _ui_update)

        try:
            # Chạy SLD Resolution
            list(sld_resolve(goals, {}, kb, callback=trace_callback))
            
            # --- FINAL LOG ---
            v_range = sorted(list(possible_values))
            status = "Success" if v_range else "Conflict"
            
            # Định dạng: Test Val(r,c,v)? -> Success/Conflict
            final_msg = f"Conclusion: {status}: Test Val({new_r},{new_c},)? = {v_range}"
            self.root.after(0, lambda: self.write_log(final_msg))
                               
            self.root.after(0, lambda: self.status_var.set("Inference Complete"))
        except Exception as e:
            self.root.after(0, lambda: self.write_log(f"Lỗi: {e}"))
        finally:
            self.root.after(0, lambda: self.btn_infer.config(state=tk.NORMAL))
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
                solver = FCHybridSolver(rules)

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

