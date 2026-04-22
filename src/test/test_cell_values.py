"""
Test individual cell values using SLD resolution.
Queries: "Can cell (r, c) have value v?"
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.core.io_handler import read_input_file
from src.solver.Backward import query_cell

def main():
    print("=" * 70)
    print("  FUTOSHIKI — TEST INDIVIDUAL CELL VALUES (SLD Resolution)")
    print("=" * 70)

    # Load puzzle
    input_path = os.path.join(PROJECT_ROOT, "Inputs/inputs-03.txt")
    n, grid, horiz, vert = read_input_file(input_path)

    print(f"\nPuzzle loaded: {n}×{n} grid from {os.path.basename(input_path)}")
    print("\nInitial grid:")
    for row in grid:
        print(f"  {row}")

    print("\n" + "=" * 70)
    print("  TEST: Query individual cell values")
    print("=" * 70)

    
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 0:
                print(f"\nCell ({r}, {c}): Finding valid domain...")
                valid = query_cell(n, r, c, grid, horiz, vert)
                print(f"  Valid values: {valid if valid else 'NONE (contradiction)'}")
            else:
                print(f"\nCell ({r}, {c}): Already filled with {grid[r][c]}")


if __name__ == "__main__":
    main()
