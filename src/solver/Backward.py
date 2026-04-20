from src.core.fol import FutoshikiKB
class BackwardSolver:
    def __init__(self, n, knowledge_base: FutoshikiKB):
        self.n = n
        self.kb = knowledge_base
        self.grid = None

    def sld_resolve(self, goals, substitution):
        """
        Depth-first SLD resolution (backward chaining).
        Base case  — empty goals ⟹ substitution is a solution.
        Inductive  — prove first goal, recurse on rest under new substitution.
        """
        if not goals:
            yield substitution
            return

        first_goal = goals[0]
        rest_goals = goals[1:]

        for new_sub in first_goal.evaluate(substitution):
            yield from self.sld_resolve(rest_goals, new_sub)

    def solve(self):
        """
        Run SLD resolution over kb.predicates and store the first solution
        in self.grid.

        Returns
        -------
        list[list[int]] | None
            The solved grid, or None if no solution exists.
        """
        solutions = self.sld_resolve(self.kb.predicates, {})

        try:
            final_sub = next(solutions)
            self.grid = [
                [final_sub[self.kb.variables[(r, c)].name]
                 for c in range(self.n)]
                for r in range(self.n)
            ]
            return self.grid
        except StopIteration:
            self.grid = None
            return None

    def query_cell(self, substitution, r, c):
        """
        Read the value assigned to cell (r,c) from a substitution dict.
        """
        var_name = self.kb.variables[(r, c)].name
        return substitution.get(var_name)