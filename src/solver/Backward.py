
class BackwardSolver:
    def __init__(self, n, horizontal_constraints, vertical_constraints):
        self.n = n
        self.horiz = horizontal_constraints
        self.vert = vertical_constraints
        self.grid = None
    def query_cell(self, r, c, val):
        """
        The 'Query' part: Can we prove Val(r, c, val)?
        This checks if the proposed 'fact' unifies with our Axioms.
        """
        # Axiom 3: Row Uniqueness
        if val in self.grid[r]:
            return False

        # Column Uniqueness Axiom
        if val in [self.grid[i][c] for i in range(self.n)]:
            return False

        # Axiom 4: Horizontal Inequality Constraints [cite: 86-87]
        if not self._check_horizontal(r, c, val):
            return False

        # Vertical Inequality Constraints [cite: 90]
        if not self._check_vertical(r, c, val):
            return False

        return True

    def _check_horizontal(self, r, c, v):
        # Check left constraint (cell c-1 and c)
        if c > 0 and self.horiz[r][c-1] != 0:
            left_val = self.grid[r][c-1]
            if left_val != 0:
                if self.horiz[r][c-1] == 1 and not (left_val < v): return False
                if self.horiz[r][c-1] == -1 and not (left_val > v): return False
        
        # Check right constraint (cell c and c+1)
        if c < self.n - 1 and self.horiz[r][c] != 0:
            right_val = self.grid[r][c+1]
            if right_val != 0:
                if self.horiz[r][c] == 1 and not (v < right_val): return False
                if self.horiz[r][c] == -1 and not (v > right_val): return False
        return True

    def _check_vertical(self, r, c, v):
        # Top-bottom relations [cite: 64-72]
        if r > 0 and self.vert[r-1][c] != 0:
            top_val = self.grid[r-1][c]
            if top_val != 0:
                if self.vert[r-1][c] == 1 and not (top_val < v): return False
                if self.vert[r-1][c] == -1 and not (top_val > v): return False
        
        if r < self.n - 1 and self.vert[r][c] != 0:
            bot_val = self.grid[r+1][c]
            if bot_val != 0:
                if self.vert[r][c] == 1 and not (v < bot_val): return False
                if self.vert[r][c] == -1 and not (v > bot_val): return False
        return True

    def solve(self, grid):
        """
        The SLD Resolution engine: 
        Proving the goal by resolving sub-goals (empty cells) one by one.
        """
        self.grid = grid
        for r in range(self.n):
            for c in range(self.n):
                if self.grid[r][c] == 0: # Found a sub-goal
                    for v in range(1, self.n + 1):
                        # Attempt to prove Val(r, c, v)
                        if self.query_cell(r, c, v):
                            self.grid[r][c] = v # Unify value
                            
                            # Recursively prove the next sub-goal
                            if self.solve(self.grid):
                                return self.grid
                            
                            # Refutation: This choice leads to False, backtrack
                            self.grid[r][c] = 0
                    return None
        return self.grid