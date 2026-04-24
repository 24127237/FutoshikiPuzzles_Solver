"""
LAYER 3 & 5 — SLD RESOLUTION ENGINE & SOLVER

Implements unification, SLD resolution (Prolog's execution model),
query generation, and solution extraction.
"""

from src.core.fol_types import Term, Atom, Number, Var, Compound
from src.core.fol_kb import KnowledgeBase, build_kb, cell, Fact, Rule


# =============================================================================
# UNIFICATION & VARIABLE RENAMING
# =============================================================================

_rename_counter = 0


def rename_clause(clause, tag: str):
    """
    Returns a structurally identical clause with all Vars renamed
    so that V → V_<tag>, preventing variable clashes across resolution steps.
    """
    def rename_term(t):
        if isinstance(t, Var):
            return Var(f"{t.name}_{tag}")
        if isinstance(t, Compound):
            return Compound(t.functor, [rename_term(a) for a in t.args])
        return t   # Atom / Number — ground, no renaming needed

    new_head = rename_term(clause.head)
    if isinstance(clause, Fact):
        return Fact(new_head)
    return Rule(new_head, [rename_term(b) for b in clause.body])


def unify(t1: Term, t2: Term, subst: dict):
    """
    Simple substitution unification (no occurs-check).
    Returns a new substitution dict (extending subst) or None if t1 and t2
    cannot be unified.

    Algorithm (Robinson, 1965):
      1. Walk both terms through current substitution.
      2. If both are identical ground terms → succeed (no new bindings).
      3. If either is an unbound Var        → bind it.
      4. If both are Compound with same f/n → unify args pairwise.
      5. Otherwise                          → fail (return None).
    """
    # Walk to get the dereferenced terms
    t1 = t1.walk(subst)
    t2 = t2.walk(subst)

    # Case 2: identical
    if t1 == t2:
        return subst

    # Case 3a: t1 is an unbound variable
    if isinstance(t1, Var):
        new_subst = dict(subst)
        new_subst[t1.name] = t2
        return new_subst

    # Case 3b: t2 is an unbound variable
    if isinstance(t2, Var):
        new_subst = dict(subst)
        new_subst[t2.name] = t1
        return new_subst

    # Case 4: both Compound — must have same functor and arity
    if (isinstance(t1, Compound) and isinstance(t2, Compound) and
            t1.functor == t2.functor and len(t1.args) == len(t2.args)):
        for a1, a2 in zip(t1.args, t2.args):
            subst = unify(a1, a2, subst)
            if subst is None:
                return None
        return subst

    # Case 5: fail
    return None


# =============================================================================
# SLD RESOLUTION ENGINE
# =============================================================================

def sld_resolve(goals: list, subst: dict, kb: KnowledgeBase, stats: dict = None, callback=None):
    """
    Depth-first SLD resolution engine — Prolog's execution model.
    """
    if not goals:
        if callback: callback("SUCCESS", "Found valid assignment", subst)
        yield subst          
        return

    global _rename_counter

    goal      = goals[0]
    rest      = goals[1:]

    if callback: callback("TRY_GOAL", f"Resolving: {goal}", subst)

    if stats is not None:
        stats["num_goal_expansions"] = stats.get("num_goal_expansions", 0) + 1

    # --- built-in arithmetic guards (not stored in KB) ---
    if isinstance(goal, Compound) and goal.functor in ["less_than", "greater_than", "neq"]:
        a = goal.args[0].walk(subst)
        b = goal.args[1].walk(subst)
        
        # Nếu đã biết giá trị cả 2, kiểm tra logic
        if isinstance(a, Number) and isinstance(b, Number):
            res = False
            if goal.functor == "less_than": res = a.value < b.value
            elif goal.functor == "greater_than": res = a.value > b.value
            elif goal.functor == "neq": res = a.value != b.value
            
            if not res:
                if callback: callback("CONFLICT", f"Constraint Violation: {a} {goal.functor} {b}", subst)
                return # Backtrack
        
        # Nếu thỏa mãn hoặc chưa đủ dữ kiện, đi tiếp
        yield from sld_resolve(rest, subst, kb, stats, callback)
        return

    # --- KB lookup: resolve goal against stored Horn clauses ---
    clauses = kb.get(goal.functor, len(goal.args))
    for clause in clauses:
        _rename_counter += 1
        fresh = rename_clause(clause, str(_rename_counter))
        new_sub = unify(goal, fresh.head, subst)
        
        if new_sub is None:
            continue
            
        yield from sld_resolve((fresh.body if isinstance(fresh, Rule) else []) + rest, 
                            new_sub, kb, stats, callback)


# =============================================================================
# QUERY BUILDER
# =============================================================================

def build_query(n, initial_grid, horiz_const, vert_const) -> tuple:
    """
    Construct the ordered goal list — the Prolog query.

    Goals are interleaved in row-major order so constraints fire as soon as
    both variables are bound — matching Prolog's left-to-right evaluation.
    
    Returns:
        (goals_list, query_vars_dict)
    """
    query_vars = {}    # (r,c) → Var("X_r_c")
    goals      = []

    for r in range(n):
        for c in range(n):
            qvar = Var(f"X_{r}_{c}")
            query_vars[(r, c)] = qvar

            # ── Goal 1: val(cell, Var)  [Axiom 1a / 1b] ─────────────────────
            goals.append(Compound("val", [cell(r, c), qvar]))

            # ── Goal 2: Axiom 2 — Row uniqueness ────────────────────────────
            for pc in range(c):
                goals.append(Compound("neq", [query_vars[(r, pc)], qvar]))

            # ── Goal 3: Axiom 3 — Column uniqueness ─────────────────────────
            for pr in range(r):
                goals.append(Compound("neq", [query_vars[(pr, c)], qvar]))

            # ── Goal 4/5: Axioms 4 & 5 — Horizontal inequality ──────────────
            if c > 0:
                h = horiz_const[r][c - 1]
                left_var = query_vars[(r, c - 1)]
                if h == 1:
                    goals.append(Compound("less_than", [left_var, qvar]))
                elif h == -1:
                    goals.append(Compound("greater_than", [left_var, qvar]))

            # ── Goal 6/7: Axioms 6 & 7 — Vertical inequality ────────────────
            if r > 0:
                v = vert_const[r - 1][c]
                top_var = query_vars[(r - 1, c)]
                if v == 1:
                    goals.append(Compound("less_than", [top_var, qvar]))
                elif v == -1:
                    goals.append(Compound("greater_than", [top_var, qvar]))

    return goals, query_vars

def query_cells(n, cells, grid, horiz_const, vert_const) -> list:
        """
        Demonstrates querying an individual cell: ?- val(v_r_c, X).
        Returns a list of all values that satisfy this single goal 
        based on the base facts in the KB.
        """
        # Rebuild KB to ensure fresh state
        kb = build_kb(n, grid, horiz_const, vert_const)
        
        # Create a single query variable and goal
        query_vars = {}
        goals = []
        
        for r, c in cells:
            qvar = Var(f"X_{r}_{c}")
            query_vars[(r, c)] = qvar
            goals.append(Compound("val", [cell(r, c), qvar]))

            for pc in range(c):
                goals.append(Compound("neq", [query_vars[(r, pc)], qvar]))

            for pr in range(r):
                goals.append(Compound("neq", [query_vars[(pr, c)], qvar]))

            if c > 0:
                h = horiz_const[r][c - 1]
                left_var = query_vars[(r, c - 1)]
                if h == 1:
                    goals.append(Compound("less_than", [left_var, qvar]))
                elif h == -1:
                    goals.append(Compound("greater_than", [left_var, qvar]))

            if r > 0:
                v = vert_const[r - 1][c]
                top_var = query_vars[(r - 1, c)]
                if v == 1:
                    goals.append(Compound("less_than", [top_var, qvar]))
                elif v == -1:
                    goals.append(Compound("greater_than", [top_var, qvar]))
 

        # Resolve the single goal
        solutions = sld_resolve(goals, {}, kb)
        
        possible_values = []
        for subst in solutions:
            bound_term = qvar.walk(subst)
            if isinstance(bound_term, Number) and bound_term.value not in possible_values:
                possible_values.append(bound_term.value)
            
        return possible_values
# =============================================================================
# SOLUTION EXTRACTION
# =============================================================================

def extract_solution(subst: dict, query_vars: dict, n: int) -> list:
    """
    Walk the final substitution to read off the grid values.
    Each query variable X_r_c is walked through the substitution chain
    until a Number is reached.
    """
    grid = []
    for r in range(n):
        row = []
        for c in range(n):
            term = query_vars[(r, c)].walk(subst)
            row.append(term.value if isinstance(term, Number) else "?")
        grid.append(row)
    return grid


# =============================================================================
# BACKWARD CHAINING SOLVER
# =============================================================================

class BackwardSolver:
    """
    Solver that uses SLD resolution to solve Futoshiki puzzles.
    """
    def __init__(self, n, horiz_const, vert_const):
        self.n = n
        self.horiz_const = horiz_const
        self.vert_const = vert_const
        self.stats = {"num_inferences": 0, "num_goal_expansions": 0}

    def solve(self, grid):
        """
        Solve the puzzle using SLD resolution.
        Returns the solution grid as a list of lists, or None if no solution.
        """
        self.stats = {"num_inferences": 0, "num_goal_expansions": 0}
        # Build KB and query
        kb = build_kb(self.n, grid, self.horiz_const, self.vert_const)
        goals, query_vars = build_query(self.n, grid, self.horiz_const, self.vert_const)

        # SLD resolution — take first solution
        solutions = sld_resolve(goals, {}, kb, self.stats)

        try:
            final_subst = next(solutions)
            return extract_solution(final_subst, query_vars, self.n)
        except StopIteration:
            return None