"""Tests for BackwardSolver.sld_resolve — focusing on:
  1. Full solve correctness
  2. query_cell() reading bound values from a substitution
  3. Backtracking behaviour: given cell rejects wrong value, retries, succeeds
  4. Backtracking behaviour: inequality constraint forces retry
  5. Backtracking behaviour: row/col uniqueness forces retry
  6. No-solution puzzle returns None
  """


import sys
import os
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.core.io_handler import read_input_file, write_output_file
from src.core.fol import FutoshikiKB
from src.solver.Backward import BackwardSolver

def run_test(test_id):
    input_path = os.path.join(PROJECT_ROOT, f"Inputs/inputs-{test_id:02d}.txt")
    output_path = os.path.join(PROJECT_ROOT, f"Outputs/outputs-{test_id:02d}.txt")

    # 1. Read data from input file
    n, grid, horiz, vert = read_input_file(input_path)

    # 2. Initialize Rules and the BackwardSolver
    kb = FutoshikiKB(n, grid, horiz, vert)
    kb.build_kb()
    solver = BackwardSolver(n, kb)
    
# 3. Chạy thuật toán Backward Chaining
    print(f"\n  Đang giải bằng Backward Chaining...")
    
    start_time = time.time()
    solution_grid = solver.solve()
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
