"""
Test file cho thuat toan Brute-force.
Chay tat ca 10 bo test input va ghi ket qua ra file output tuong ung.
"""
import sys
import os
import time
import copy

# Them duong dan goc cua project vao sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.core.io_handler import read_input_file, write_output_file
from src.core.rules import FutoshikiRules

# Module "Brute-force.py" co dau gach noi nen phai import bang importlib
import importlib
brute_force_module = importlib.import_module("src.solver.Brute-force")
BruteForceSolver = brute_force_module.BruteForceSolver


def run_test(test_id):
    """Chay thuat toan Brute-force cho mot bo test cu the."""
    input_path = os.path.join(PROJECT_ROOT, f"Inputs/inputs-{test_id:02d}.txt")
    output_path = os.path.join(PROJECT_ROOT, f"Outputs/outputs-{test_id:02d}.txt")

    print(f"\n{'='*60}")
    print(f"  Test {test_id:02d} - Thuat toan Brute-force")
    print(f"{'='*60}")
    print(f"  Input : {input_path}")
    print(f"  Output: {output_path}")

    # 1. Doc du lieu tu file input
    n, grid, horiz, vert = read_input_file(input_path)

    print(f"  Kich thuoc bang: {n}x{n}")
    print(f"  Bang ban dau:")
    for row in grid:
        print(f"    {row}")

    # 2. Khoi tao Rules
    rules = FutoshikiRules(n, horiz, vert)

    # 3. Chay thuat toan Brute-force
    # BruteForceSolver.solve() nhan grid truc tiep (khong dung State)
    # va modify grid in-place, nen can deepcopy de giu ban goc
    solver = BruteForceSolver(rules)
    grid_copy = copy.deepcopy(grid)

    print(f"\n  Dang giai bang Brute-force...")
    print(f"  [NOTE] Brute-force co the rat cham voi bang lon (>5x5)")

    start_time = time.time()
    solution_grid = solver.solve(grid_copy)
    elapsed = time.time() - start_time

    # 4. Xu ly ket qua
    if solution_grid:
        print(f"  [OK] Giai thanh cong! (Thoi gian: {elapsed:.4f}s)")
        print(f"  Bang ket qua:")
        for row in solution_grid:
            print(f"    {row}")

        # 5. Ghi ket qua ra file output
        write_output_file(output_path, solution_grid, horiz, vert)
        return True
    else:
        print(f"  [FAIL] Khong tim thay loi giai! (Thoi gian: {elapsed:.4f}s)")
        return False


def main():
    print("=" * 60)
    print("  FUTOSHIKI SOLVER - TEST BRUTE-FORCE ALGORITHM")
    print("=" * 60)

    total = 10
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
    print(f"  TONG KET - BRUTE-FORCE")
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
