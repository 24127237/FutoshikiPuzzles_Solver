from src.core.rules import FutoshikiRules as rules_base
class BackwardSolver:
    def __init__(self, n, rules_base):
        self.n = n
        self.rules = rules_base
        self.grid = None
    def query_cell(self, r, c, val):
        """
        The 'Query' part: Can we prove Val(r, c, val)?
        This checks if the proposed 'fact' unifies with our Axioms.
        """
        # Step 1: Temporarily assert the fact into the knowledge base (the grid)
        self.grid[r][c] = val
        
        # Step 2: Ask the Oracle (rules.py) if this new universe is valid
        is_ok = self.rules.is_valid(self.grid)
        
        # Step 3: Retract the temporary fact so we don't mess up the board state
        self.grid[r][c] = 0

        return is_ok

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
                        
                        if self.n <= 5:
                            print(f"  ?- Query: Can we prove Val({r}, {c}, {v})?")
                            
                        # Attempt to prove Val(r, c, v)
                        if self.query_cell(r, c, v):
                            self.grid[r][c] = v # Unify 
                            
                            if self.n <= 5:
                                print(f"  -> YES: Val({r}, {c}, {v}) is locally valid.")
                            
                            # Recursively prove the next sub-goal
                            if self.solve(self.grid):
                                if self.n <= 5:
                                    print(f"  => PROVEN: Val({r}, {c}, {v}) is part of the final solution!")
                                return self.grid
                            
                            # Refutation: This choice leads to False, backtrack
                            self.grid[r][c] = 0
                            if self.n <= 5:
                                print(f"  <- BACKTRACK: Val({r}, {c}, {v}) led to a dead end.")
                                
                    return None # Trigger backtrack to previous cell
        return self.grid