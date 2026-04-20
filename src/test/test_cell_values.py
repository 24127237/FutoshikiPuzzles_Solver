"""
Test individual cell values using SLD resolution.
Queries: "Can cell (r, c) have value v?"
"""

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.core.io_handler import read_input_file
from src.core.FOL import Number, Var, Compound
from src.core.kb_fol import build_kb, cell
from src.solver.Backward import sld_resolve, build_query, extract_solution


def test_cell_value(n, grid, horiz_const, vert_const, r, c, v):
    """
    Test if cell (r, c) can have value v using SLD resolution.
    Returns True if the value is consistent with all constraints.
    """
    kb = build_kb(n, grid, horiz_const, vert_const)
    
    # Create a goal: val(cell(r, c), v)
    goal = Compound("val", [cell(r, c), Number(v)])
    
    # Try to prove this goal
    solutions = sld_resolve([goal], {}, kb)
    
    try:
        next(solutions)
        return True  # Goal was provable
    except StopIteration:
        return False  # Goal failed


def test_cell_domain(n, grid, horiz_const, vert_const, r, c):
    """
    Test which values are valid for cell (r, c).
    Returns a list of valid values.
    """
    if grid[r][c] != 0:
        print(f"  Cell ({r}, {c}) is already filled with {grid[r][c]}")
        return [grid[r][c]]
    
    valid_values = []
    for v in range(1, n + 1):
        if test_cell_value(n, grid, horiz_const, vert_const, r, c, v):
            valid_values.append(v)
    
    return valid_values


def test_full_query(n, grid, horiz_const, vert_const, query_cells):
    """
    Test a full query with multiple cell constraints.
    query_cells: list of tuples [(r, c, v), ...]
    
    Returns the substitution if consistent, None otherwise.
    """
    kb = build_kb(n, grid, horiz_const, vert_const)
    
    # Build goals for each queried cell
    goals = []
    for r, c, v in query_cells:
        goals.append(Compound("val", [cell(r, c), Number(v)]))
    
    # Add row/col uniqueness constraints for queried cells
    for i, (r1, c1, v1) in enumerate(query_cells):
        for j, (r2, c2, v2) in enumerate(query_cells):
            if i < j:
                # If same row, values must differ
                if r1 == r2:
                    goals.append(Compound("neq", [Number(v1), Number(v2)]))
                # If same col, values must differ
                if c1 == c2:
                    goals.append(Compound("neq", [Number(v1), Number(v2)]))
    
    solutions = sld_resolve(goals, {}, kb)
    
    try:
        subst = next(solutions)
        return subst
    except StopIteration:
        return None


def main():
    print("=" * 70)
    print("  FUTOSHIKI — TEST INDIVIDUAL CELL VALUES (SLD Resolution)")
    print("=" * 70)

    # Load puzzle
    input_path = os.path.join(PROJECT_ROOT, "Inputs/inputs-01.txt")
    n, grid, horiz, vert = read_input_file(input_path)

    print(f"\nPuzzle loaded: {n}×{n} grid from {os.path.basename(input_path)}")
    print("\nInitial grid:")
    for row in grid:
        print(f"  {row}")

    print("\n" + "=" * 70)
    print("  TEST 1: Query individual cell values")
    print("=" * 70)

    # Test a few cells
    test_positions = [(0, 0), (0, 1), (1, 1), (2, 2)]
    
    for r, c in test_positions:
        if grid[r][c] == 0:
            print(f"\nCell ({r}, {c}): Finding valid domain...")
            valid = test_cell_domain(n, grid, horiz, vert, r, c)
            print(f"  Valid values: {valid if valid else 'NONE (contradiction)'}")
        else:
            print(f"\nCell ({r}, {c}): Already filled with {grid[r][c]}")

    print("\n" + "=" * 70)
    print("  TEST 2: Query multiple cells with constraints")
    print("=" * 70)

    # Test if we can place specific values
    test_queries = [
        [(0, 0, 1), (0, 1, 2)],   # Can (0,0)=1 and (0,1)=2?
        [(0, 0, 1), (0, 1, 1)],   # Can (0,0)=1 and (0,1)=1? (same row, should fail)
        [(0, 0, 1), (1, 0, 2)],   # Can (0,0)=1 and (1,0)=2? (different cols)
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        result = test_full_query(n, grid, horiz, vert, query)
        if result is not None:
            print(f"CONSISTENT")
        else:
            print(f"INCONSISTENT (violates constraints)")

if __name__ == "__main__":
    main()
