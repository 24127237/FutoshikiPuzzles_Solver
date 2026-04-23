"""
Test file cho thuat toan Forward Chaining.
Chay tat ca 12 bo test input va ghi ket qua ra file output tuong ung.
"""
import sys
import os
import time

# Them duong dan goc cua project vao sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.core.io_handler import read_input_file, write_output_file
from src.core.rules import FutoshikiRules
from src.core.state import State
from src.solver.FCHybrid import FCHybridSolver


def run_test(test_id):
    """Chay thuat toan Forward Chaining cho mot bo test cu the."""
    input_path = os.path.join(PROJECT_ROOT, f"Inputs/inputs-{test_id:02d}.txt")
    output_path = os.path.join(PROJECT_ROOT, f"Outputs/outputs-{test_id:02d}.txt")

    print(f"\n{'='*60}")
    print(f"  Test {test_id:02d} - Thuat toan Forward Chaining")
    print(f"{'='*60}")
    print(f"  Input : {input_path}")
    print(f"  Output: {output_path}")

    # 1. Doc du lieu tu file input
    n, grid, horiz, vert = read_input_file(input_path)

    print(f"  Kich thuoc bang: {n}x{n}")
    print("  Bang ban dau:")
    for row in grid:
        print(f"    {row}")

    # 2. Khoi tao Rules va State
    rules = FutoshikiRules(n, horiz, vert)
    initial_state = State(n, grid, rules)

    # 3. Chay thuat toan Forward Chaining
    solver = FCHybridSolver(rules)
    print("\n  Dang giai bang Forward Chaining...")

    start_time = time.time()
    solution_grid = solver.solve(initial_state)
    elapsed = time.time() - start_time

    # 4. Xu ly ket qua
    if solution_grid:
        print(f"  [OK] Giai thanh cong! (Thoi gian: {elapsed:.4f}s)")
        print("  Bang ket qua:")
        for row in solution_grid:
            print(f"    {row}")

        # 5. Ghi ket qua ra file output
        write_output_file(output_path, solution_grid, horiz, vert)
        return True

    print(f"  [FAIL] Khong tim thay loi giai! (Thoi gian: {elapsed:.4f}s)")
    return False


def main():
    print("=" * 60)
    print("  FUTOSHIKI SOLVER - TEST FORWARD CHAINING ALGORITHM")
    print("=" * 60)

    total = 12
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
            print(f"  [ERROR] Loi khi chay test {i:02d}: {e}")
            results.append((i, False))
            failed += 1

    # Tong ket
    print(f"\n{'='*60}")
    print("  TONG KET - FORWARD CHAINING")
    print(f"{'='*60}")
    print(f"  Tong so test : {total}")
    print(f"  Thanh cong   : {passed}")
    print(f"  That bai     : {failed}")
    print(f"{'='*60}")

    for test_id, success in results:
        status = "[OK] PASSED" if success else "[FAIL] FAILED"
        print(f"  Test {test_id:02d}: {status}")

    print(f"{'='*60}")


if __name__ == "__main__":
    main()
