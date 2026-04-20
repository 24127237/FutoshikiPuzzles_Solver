import sys
import os
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.core.io_handler import read_input_file, write_output_file
from src.core.rules import FutoshikiRules
from src.solver.Backward import BackwardSolver

def run_test(test_id):
    input_path = os.path.join(PROJECT_ROOT, f"Inputs/inputs-{test_id:02d}.txt")
    output_path = os.path.join(PROJECT_ROOT, f"Outputs/outputs-{test_id:02d}.txt")

    # 1. Read data from input file
    n, grid, horiz, vert = read_input_file(input_path)

    # 2. Initialize Rules and the BackwardSolver
    rules = FutoshikiRules(n, horiz, vert)
    solver = BackwardSolver(n, rules)
# 3. Chạy thuật toán Backward Chaining
    print(f"\n  Đang giải bằng Backward Chaining...")
    
    start_time = time.time()
    solution_grid = solver.solve(grid)
    elapsed = time.time() - start_time

    # 4. Xử lý kết quả và in ra terminal
    if solution_grid is not None:
        print(f"  [OK] Giải thành công! (Thời gian: {elapsed:.4f}s)")
        print(f"  Bảng kết quả:")
        # In trực tiếp output ra terminal như bạn yêu cầu
        for row in solution_grid:
            print(f"    {row}")

        # 5. Ghi kết quả ra file output thông qua io_handler
        # Đảm bảo thư mục Outputs tồn tại
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        write_output_file(output_path, solution_grid, horiz, vert)
        return True
    else:
        print(f"  [FAIL] Không thể chứng minh mục tiêu (Không có lời giải)! (Thời gian: {elapsed:.4f}s)")
        return False
def run_query_demo(test_id=1):
    print("=" * 60)
    print("  PROLOG-STYLE SLD QUERY DEMONSTRATION")
    print("=" * 60)

    # 1. Load the board
    input_path = os.path.join(PROJECT_ROOT, f"Inputs/inputs-{test_id:02d}.txt")
    try:
        n, grid, horiz, vert = read_input_file(input_path)
    except FileNotFoundError:
        print("Input file not found!")
        return

    # 2. Initialize the engine
    rules = FutoshikiRules(n, horiz, vert)
    solver = BackwardSolver(n, rules)
    solver.grid = grid # Load the grid into the solver manually for querying

    print("Current Knowledge Base (Board State):")
    for row in grid:
        print(f"  {row}")
    print("-" * 60)

    # 3. Interactive Query Loop
    print("Enter a query to test if a value is logically valid for a cell.")
    print("Format: row col value (e.g., '0 1 3'). Type 'exit' to quit.")
    
    while True:
        user_input = input("\n?- query_cell: ")
        
        if user_input.lower() == 'exit':
            break
            
        try:
            r, c, v = map(int, user_input.split())
            
            # Boundary checks
            if not (0 <= r < n and 0 <= c < n and 1 <= v <= n):
                print(f"  [ERROR] Invalid input. r, c must be 0 to {n-1}. v must be 1 to {n}.")
                continue
                
            if grid[r][c] != 0:
                print(f"  [INFO] Cell ({r}, {c}) is already a known fact: {grid[r][c]}")
                continue

            # === THE ACTUAL SLD QUERY DEMONSTRATION ===
            print(f"  Evaluating Sub-goal: Can we prove Val({r}, {c}, {v})?")
            is_provable = solver.query_cell(r, c, v)
            
            if is_provable:
                print("  => YES (True). This fact unifies with current axioms without contradiction.")
            else:
                print("  => NO (False). Refutation! This fact violates the rules (Row/Col/Inequality).")
                
        except ValueError:
            print("  [ERROR] Please enter three numbers separated by spaces.")

def main():
    print("=" * 60)
    print("  FUTOSHIKI SOLVER - TEST BACKWARD CHAINING ALGORITHM")
    print("=" * 60)

    total = 1
    passed = 0
    failed = 0
    results = []

    for i in range(1, total + 1):
        try:
            success = run_test(i)
            results.append((i, success))
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  [ERROR] Lỗi khi chạy test {i:02d}: {e}")
            results.append((i, False))
            failed += 1

    # Tổng kết
    print(f"\n{'='*60}")
    print(f"  TỔNG KẾT - BACKWARD CHAINING")
    print(f"{'='*60}")
    print(f"  Tổng số test : {total}")
    print(f"  Thành công   : {passed}")
    print(f"  Thất bại     : {failed}")
    print(f"{'='*60}")
    for test_id, success in results:
        status = "[OK] PASSED" if success else "[FAIL] FAILED"
        print(f"  Test {test_id:02d}: {status}")
    print(f"{'='*60}")


if __name__ == "__main__":
    # main() chạy main để thực hiện solver
    # run_query_demo() để chạy demo query tương tác
    main()
    # run_query_demo(test_id=1)
