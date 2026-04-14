import sys
import os
import time

# Them duong dan goc cua project vao sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.core.io_handler import read_input_file, write_output_file

class BackwardDemo:
    def __init__(self, n, grid, horiz, vert):
        self.n = n
        self.grid = grid
        self.horiz = horiz
        self.vert = vert
        self.inference_count = 0

    def query_val(self, r, c, v):
        """
        The SLD Query: ?- Val(r, c, v).
        Checks if the value v can be unified with the current axioms.
        """
        self.inference_count += 1
        # print(f"  Querying: Val({r+1}, {c+1}, {v})?")

        # 1. Row Uniqueness Axiom [cite: 43, 83-85]
        if v in self.grid[r]:
            # print(f"    -> Refuted: Row {r+1} already contains {v}.")
            return False

        # 2. Column Uniqueness Axiom [cite: 44]
        if v in [self.grid[i][c] for i in range(self.n)]:
            # print(f"    -> Refuted: Column {c+1} already contains {v}.")
            return False

        # 3. Horizontal Inequality Axiom [cite: 45, 86-87]
        # Check left neighbor
        if c > 0 and self.horiz[r][c-1] != 0:
            left = self.grid[r][c-1]
            if left != 0:
                if self.horiz[r][c-1] == 1 and not (left < v):
                    # print(f"    -> Refuted: Constraint {left} < {v} failed.")
                    return False
                if self.horiz[r][c-1] == -1 and not (left > v):
                    # print(f"    -> Refuted: Constraint {left} > {v} failed.")
                    return False

        # 4. Vertical Inequality Axiom [cite: 45, 64-72]
        # Check top neighbor
        if r > 0 and self.vert[r-1][c] != 0:
            top = self.grid[r-1][c]
            if top != 0:
                if self.vert[r-1][c] == 1 and not (top < v):
                    # print(f"    -> Refuted: Vertical Constraint {top} < {v} failed.")
                    return False
                if self.vert[r-1][c] == -1 and not (top > v):
                    # print(f"    -> Refuted: Vertical Constraint {top} > {v} failed.")
                    return False

        # print(f"    -> Success: Val({r+1}, {c+1}, {v}) is a valid fact.")
        return True

    def solve(self, step=1):
        """
        The Backward Chaining Inference Engine.
        """
        for r in range(self.n):
            for c in range(self.n):
                if self.grid[r][c] == 0:
                    # print(f"\n[Step {step}] Target Goal: Resolve cell ({r+1}, {c+1})")
                    
                    # Search for a value v to satisfy the sub-goal
                    for v in range(1, self.n + 1):
                        if self.query_val(r, c, v):
                            # Temporarily add this fact to the KB
                            self.grid[r][c] = v
                            
                            # Recursively prove the remaining sub-goals
                            if self.solve(step + 1):
                                return True
                            
                            # Backtrack (Refutation): If future proof fails, retract fact
                            # print(f"\n[Backtrack] Retracting Val({r+1}, {c+1}, {v}). Trying next value...")
                            self.grid[r][c] = 0
                    
                    return False # No value v can satisfy this sub-goal
        return True

def main():
    # 4x4 Example similar to the PDF [cite: 29, 114-129]
    input_path = os.path.join(PROJECT_ROOT, f"Inputs/inputs-03.txt")
    n, grid, horiz, vert = read_input_file(input_path)
    solver = BackwardDemo(n, grid, horiz, vert)
    start_time = time.time()
    
    print("=== FUTOSHIKI BACKWARD CHAINING (SLD RESOLUTION) DEMO ===")
    if solver.solve():
        print("\n" + "="*40)
        print("GOAL PROVEN: SOLVED GRID")
        for row in solver.grid:
            print(row)
        print("="*40)
    else:
        print("\nGoal could not be proven.")

    print(f"\nTotal Inferences: {solver.inference_count}")
    print(f"Execution Time: {time.time() - start_time:.4f} seconds")

if __name__ == "__main__":
    main()