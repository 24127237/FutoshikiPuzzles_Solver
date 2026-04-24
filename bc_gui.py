import tkinter as tk
from tkinter import ttk, scrolledtext
from src.solver.PureBackwardChaining import query_cell
from gui import FutoshikiGUI
class FutoshikiInferenceDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Futoshiki Inference Solver - GUI & Trace")
        self.size = 4  # Grid 4x4
        
        # Biến trạng thái
        self.cells = {} # Lưu trữ các widget Entry
        self.selection_start = None
        self.selected_cells = []
        
        self.setup_ui()

    def setup_ui(self):
        # --- Frame bên trái: Grid Futoshiki ---
        self.grid_frame = tk.Frame(self.root, padx=20, pady=20)
        self.grid_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        for r in range(self.size):
            for c in range(self.size):
                # Tạo một ô nhập liệu
                cell = tk.Entry(self.grid_frame, width=3, font=('Arial', 18, 'bold'), 
                                justify='center', bd=2, relief="groove")
                cell.grid(row=r*2, column=c*2, padx=5, pady=5)
                
                # Bind sự kiện chuột
                cell.bind("<Button-1>", lambda e, r=r, c=c: self.start_selection(r, c))
                cell.bind("<B1-Motion>", lambda e: self.update_selection(e))
                
                self.cells[(r, c)] = cell

                # Thêm ký hiệu Futoshiki giả định (Ví dụ dấu > giữa cột 0 và 1)
                if c < self.size - 1 and r == 0:
                    tk.Label(self.grid_frame, text=">").grid(row=r*2, column=c*2+1)

        # --- Frame bên phải: Log và Cây suy luận ---
        self.side_frame = tk.Frame(self.root, padx=10, pady=10)
        self.side_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Cây suy luận (Treeview)
        tk.Label(self.side_frame, text="Inference Tree (Backward Chaining Trace):").pack(anchor="w")
        self.tree = ttk.Treeview(self.side_frame, columns=("Status"), height=10)
        self.tree.heading("#0", text="Step / Hypothesis")
        self.tree.heading("Status", text="Result")
        self.tree.pack(fill=tk.X, pady=5)

        # Log chi tiết
        tk.Label(self.side_frame, text="Detailed Log:").pack(anchor="w")
        self.log = scrolledtext.ScrolledText(self.side_frame, height=8, state='disabled')
        self.log.pack(fill=tk.BOTH, expand=True)

        # Nút điều khiển
        self.btn_solve = tk.Button(self.side_frame, text="Run Inference Step", 
                                   command=self.demo_inference, bg="#4CAF50", fg="white")
        self.btn_solve.pack(fill=tk.X, pady=10)

    # --- Logic Chọn Range ---
    def start_selection(self, r, c):
        self.clear_selection()
        self.selection_start = (r, c)
        self.add_to_selection(r, c)

    def update_selection(self, event):
        # Tìm widget dưới con trỏ chuột
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        for coords, cell in self.cells.items():
            if cell == widget:
                r_start, c_start = self.selection_start
                r_end, c_end = coords
                self.clear_selection()
                # Vẽ vùng chọn hình chữ nhật
                for r in range(min(r_start, r_end), max(r_start, r_end) + 1):
                    for c in range(min(c_start, c_end), max(c_start, c_end) + 1):
                        self.add_to_selection(r, c)

    def add_to_selection(self, r, c):
        self.cells[(r, c)].config(bg="#ADD8E6") # Light blue
        if (r, c) not in self.selected_cells:
            self.selected_cells.append((r, c))

    def clear_selection(self):
        for cell in self.cells.values():
            cell.config(bg="white")
        self.selected_cells = []

    # --- Logic Inference & Trace ---
    def write_log(self, message):
        self.log.config(state='normal')
        self.log.insert(tk.END, f"> {message}\n")
        self.log.see(tk.END)
        self.log.config(state='disabled')

    def demo_inference(self):
        """Mô phỏng Backward Chaining trên vùng được chọn"""
        if not self.selected_cells:
            self.write_log("Cảnh báo: Hãy quét chọn một vùng ô trước!")
            return

        self.tree.delete(*self.tree.get_children())
        self.write_log(f"Bắt đầu suy luận ngược cho {len(self.selected_cells)} ô...")

        # Giả lập các bước suy luận ngược
        root_node = self.tree.insert("", "end", text="Main Goal: Fill Range", open=True)
        
        for i, (r, c) in enumerate(self.selected_cells):
            node = self.tree.insert(root_node, "end", text=f"Checking Cell ({r},{c})", open=True)
            
            # Giả lập thử giá trị (Backward Chaining Hypothesis)
            for val in range(1, 3):
                status = "OK" if val == 1 else "Conflict (Row)"
                sub_node = self.tree.insert(node, "end", text=f"Try value: {val}", values=(status,))
                
                if status != "OK":
                    self.tree.item(sub_node, tags=('fail',))
                    self.write_log(f"Ô ({r},{c}) thử giá trị {val} -> Thất bại, quay lui!")
                else:
                    self.write_log(f"Ô ({r},{c}) thử giá trị {val} -> Khả thi.")

        self.tree.tag_configure('fail', foreground='red')

if __name__ == "__main__":
    root = tk.Tk()
    app = FutoshikiInferenceDemo(root)
    root.mainloop()