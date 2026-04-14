import sys
sys.stdout.reconfigure(encoding='utf-8')
from src.core.io_handler import read_input_file
from src.core.rules import FutoshikiRules
from src.core.state import State
from src.solver.Astar import AstarSolver

# 1. Đọc dữ liệu từ file
n, grid, horiz, vert = read_input_file("Inputs/inputs-06.txt")

# 2. Khởi tạo bộ Luật (Rules) và Trạng thái ban đầu (State)
rules = FutoshikiRules(n, horiz, vert)
initial_state = State(n, grid)

# 3. Chạy thuật toán A*
solver = AstarSolver()
path = solver.solve(initial_state, rules)

if path is not None:
    print("Solved! The final grid is:")
    for row in path[-1]: 
        print(row)
else:
    print("No solution found!")