from src.core.io_handler import read_input_file
from src.core.rules import FutoshikiRules
from src.core.state import State
from src.solver.Astar import AstarSolver
import random

# 1. Đọc dữ liệu từ file
n, grid, horiz, vert = read_input_file(f"Inputs/inputs-{random.randint(1, 10):02d}.txt")

# 2. Khởi tạo bộ Luật (Rules) và Trạng thái ban đầu (State)
rules = FutoshikiRules(n, horiz, vert)
initial_state = State(n, grid)

# 3. Chạy thuật toán A*
solver = AstarSolver()
path = solver.solve(initial_state, rules)

if path:
    print("Giải thành công! Bàn cờ cuối cùng là:")
    for row in path[-1]: 
        print(row)
else:
    print("Không tìm thấy đường đi!")