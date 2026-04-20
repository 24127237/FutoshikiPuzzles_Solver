# ==========================================
# 1. LOGIC ENGINE COMPONENTS (The SLD Base)
# ==========================================

class Variable:
    """Represents a logical variable in our knowledge base."""
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

class Predicate:
    """Base class for all Horn clauses/rules."""
    def evaluate(self, substitution):
        pass


# ==========================================
# 2. FOL AXIOMS AS PREDICATE CLASSES
# ==========================================

# ------------------------------------------
# AXIOM 1a — Given(i,j,v) => Val(i,j,v)
#
# Closed sentence:
#   ∀i,j,v: Given(i,j,v) => Val(i,j,v)
#
# If a cell is pre-filled, its domain is the singleton {v}.
# Unifies the variable at (i,j) with exactly one value v.
# ------------------------------------------
class GivenVal(Predicate):
    """
    Axiom 1a: Given(i,j,v) => Val(i,j,v)
    Pre-filled cell: binds variable to its unique clue value.
    """
    def __init__(self, var, given_value):
        self.var = var
        self.given_value = given_value  # The single clue value v

    def evaluate(self, sub):
        # Singleton domain — only one unification is possible
        new_sub = sub.copy()
        new_sub[self.var.name] = self.given_value
        yield new_sub


# ------------------------------------------
# AXIOM 1b — ¬Given(i,j,_) => Val(i,j,1) ∨ ... ∨ Val(i,j,N)
#
# Closed sentence:
#   ∀i,j: ¬Given(i,j,_) => (Val(i,j,1) ∨ Val(i,j,2) ∨ ... ∨ Val(i,j,N))
#
# Free cell: non-deterministically unifies the variable with
# each value in {1,...,N}, creating one branch per value.
# ------------------------------------------
class FreeVal(Predicate):
    """
    Axiom 1b: ¬Given(i,j,_) => Val(i,j,1) ∨ ... ∨ Val(i,j,N)
    Free cell: enumerates the full domain, one branch per value.
    """
    def __init__(self, var, n):
        self.var = var
        self.domain = list(range(1, n + 1))  # {1, ..., N}

    def evaluate(self, sub):
        # Each iteration is one disjunct: Val(i,j,k) for k in {1..N}
        for val in self.domain:
            new_sub = sub.copy()
            new_sub[self.var.name] = val
            yield new_sub


# ------------------------------------------
# AXIOM 2 — Row Uniqueness
#
# Closed sentence:
#   ∀i, j1, j2, v1, v2:
#     j1 < j2 ∧ Val(i,j1,v1) ∧ Val(i,j2,v2) => v1 ≠ v2
#
# For every pair of columns already assigned in the same row,
# the two bound values must differ.
# ------------------------------------------
class RowUnique(Predicate):
    """
    Axiom 2: j1 < j2 ∧ Val(i,j1,v1) ∧ Val(i,j2,v2) => v1 ≠ v2
    Enforces all-different across a row (left of current column).
    """
    def __init__(self, var_prev, var_curr):
        self.v_prev = var_prev  # Variable at (i, j1), j1 < j2
        self.v_curr = var_curr  # Variable at (i, j2)

    def evaluate(self, sub):
        val_prev = sub.get(self.v_prev.name)
        val_curr = sub.get(self.v_curr.name)
        # Guard: both must be bound before we can check
        if val_prev is not None and val_curr is not None:
            if val_prev != val_curr:          # v1 ≠ v2
                yield sub


# ------------------------------------------
# AXIOM 3 — Column Uniqueness
#
# Closed sentence:
#   ∀i1, i2, j, v1, v2:
#     i1 < i2 ∧ Val(i1,j,v1) ∧ Val(i2,j,v2) => v1 ≠ v2
#
# For every pair of rows already assigned in the same column,
# the two bound values must differ.
# ------------------------------------------
class ColUnique(Predicate):
    """
    Axiom 3: i1 < i2 ∧ Val(i1,j,v1) ∧ Val(i2,j,v2) => v1 ≠ v2
    Enforces all-different down a column (above current row).
    """
    def __init__(self, var_prev, var_curr):
        self.v_prev = var_prev  # Variable at (i1, j), i1 < i2
        self.v_curr = var_curr  # Variable at (i2, j)

    def evaluate(self, sub):
        val_prev = sub.get(self.v_prev.name)
        val_curr = sub.get(self.v_curr.name)
        if val_prev is not None and val_curr is not None:
            if val_prev != val_curr:          # v1 ≠ v2
                yield sub


# ------------------------------------------
# AXIOM 4 — Horizontal LessH Constraint
#
# Closed sentence:
#   ∀i, j, v1, v2:
#     LessH(i,j) ∧ Val(i,j,v1) ∧ Val(i,j+1,v2) => Less(v1,v2)
#
# horiz_const[i][j] == 1 means cell (i,j) < cell (i,j+1).
# After both cells are bound, verify v1 < v2.
# ------------------------------------------
class LessH(Predicate):
    """
    Axiom 4: LessH(i,j) ∧ Val(i,j,v1) ∧ Val(i,j+1,v2) => Less(v1,v2)
    Horizontal '<' constraint: left cell must be less than right cell.
    Corresponds to horiz_const[r][c-1] == 1 checked at column c.
    """
    def __init__(self, var_left, var_right):
        self.v_left  = var_left   # Variable at (i, j)
        self.v_right = var_right  # Variable at (i, j+1)

    def evaluate(self, sub):
        v1 = sub.get(self.v_left.name)
        v2 = sub.get(self.v_right.name)
        if v1 is not None and v2 is not None:
            if v1 < v2:                       # Less(v1, v2)
                yield sub


# ------------------------------------------
# AXIOM 5 — Horizontal GreaterH Constraint
#
# Closed sentence:
#   ∀i, j, v1, v2:
#     GreaterH(i,j) ∧ Val(i,j,v1) ∧ Val(i,j+1,v2) => Less(v2,v1)
#
# horiz_const[i][j] == -1 means cell (i,j) > cell (i,j+1).
# Rewritten as Less(v2, v1) to use the single background relation.
# ------------------------------------------
class GreaterH(Predicate):
    """
    Axiom 5: GreaterH(i,j) ∧ Val(i,j,v1) ∧ Val(i,j+1,v2) => Less(v2,v1)
    Horizontal '>' constraint: left cell must be greater than right cell.
    Corresponds to horiz_const[r][c-1] == -1 checked at column c.
    """
    def __init__(self, var_left, var_right):
        self.v_left  = var_left   # Variable at (i, j)
        self.v_right = var_right  # Variable at (i, j+1)

    def evaluate(self, sub):
        v1 = sub.get(self.v_left.name)
        v2 = sub.get(self.v_right.name)
        if v1 is not None and v2 is not None:
            if v2 < v1:                       # Less(v2, v1)
                yield sub


# ------------------------------------------
# AXIOM 6 — Vertical LessV Constraint
#
# Closed sentence:
#   ∀i, j, v1, v2:
#     LessV(i,j) ∧ Val(i,j,v1) ∧ Val(i+1,j,v2) => Less(v1,v2)
#
# vert_const[i][j] == 1 means cell (i,j) < cell (i+1,j).
# ------------------------------------------
class LessV(Predicate):
    """
    Axiom 6: LessV(i,j) ∧ Val(i,j,v1) ∧ Val(i+1,j,v2) => Less(v1,v2)
    Vertical '<' constraint: top cell must be less than bottom cell.
    Corresponds to vert_const[r-1][c] == 1 checked at row r.
    """
    def __init__(self, var_top, var_bot):
        self.v_top = var_top  # Variable at (i,   j)
        self.v_bot = var_bot  # Variable at (i+1, j)

    def evaluate(self, sub):
        v1 = sub.get(self.v_top.name)
        v2 = sub.get(self.v_bot.name)
        if v1 is not None and v2 is not None:
            if v1 < v2:                       # Less(v1, v2)
                yield sub


# ------------------------------------------
# AXIOM 7 — Vertical GreaterV Constraint
#
# Closed sentence:
#   ∀i, j, v1, v2:
#     GreaterV(i,j) ∧ Val(i,j,v1) ∧ Val(i+1,j,v2) => Less(v2,v1)
#
# vert_const[i][j] == -1 means cell (i,j) > cell (i+1,j).
# ------------------------------------------
class GreaterV(Predicate):
    """
    Axiom 7: GreaterV(i,j) ∧ Val(i,j,v1) ∧ Val(i+1,j,v2) => Less(v2,v1)
    Vertical '>' constraint: top cell must be greater than bottom cell.
    Corresponds to vert_const[r-1][c] == -1 checked at row r.
    """
    def __init__(self, var_top, var_bot):
        self.v_top = var_top  # Variable at (i,   j)
        self.v_bot = var_bot  # Variable at (i+1, j)

    def evaluate(self, sub):
        v1 = sub.get(self.v_top.name)
        v2 = sub.get(self.v_bot.name)
        if v1 is not None and v2 is not None:
            if v2 < v1:                       # Less(v2, v1)
                yield sub

class FutoshikiKB:
    """
    The Knowledge Base for Futoshiki: holds all axioms and facts.
    In a more complex system, this would manage the set of predicates
    and their interactions. For our purposes, it's a simple container.
    """
    def __init__(self, n, initial_grid, horiz_const, vert_const):
        self.n           = n
        self.initial_grid = initial_grid
        self.horiz_const  = horiz_const
        self.vert_const   = vert_const
        self.predicates   = []   # ordered goal list
        self.variables    = {}   # (r,c) → Variable

        # --- Assemble goal list from FOL axioms ---
    # Goals are interleaved so constraints prune the tree as early as possible.
    def build_kb(self):
        # Create one Variable per cell
        for r in range(self.n):
            for c in range(self.n):
                self.variables[(r, c)] = Variable(f"X{r}_{c}")

        # Assemble the goal list
        for r in range(self.n):
            for c in range(self.n):
                var = self.variables[(r, c)]

                # ── Axiom 1a / 1b : Val assignment ──────────────────────────
                if self.initial_grid[r][c] != 0:
                    # Given(r,c,v) => Val(r,c,v)
                    self.predicates.append(GivenVal(var, self.initial_grid[r][c]))
                else:
                    # ¬Given(r,c,_) => Val(r,c,1) ∨ ... ∨ Val(r,c,N)
                    self.predicates.append(FreeVal(var, self.n))   # FIX: self.n

                # ── Axiom 2 : Row uniqueness ─────────────────────────────────
                for prev_c in range(c):
                    self.predicates.append(
                        RowUnique(self.variables[(r, prev_c)], var))

                # ── Axiom 3 : Column uniqueness ──────────────────────────────
                for prev_r in range(r):
                    self.predicates.append(
                        ColUnique(self.variables[(prev_r, c)], var))

                # ── Axioms 4 & 5 : Horizontal inequality ─────────────────────
                if c > 0:
                    h = self.horiz_const[r][c - 1]
                    if h == 1:
                        self.predicates.append(
                            LessH(self.variables[(r, c - 1)], var))
                    elif h == -1:
                        self.predicates.append(
                            GreaterH(self.variables[(r, c - 1)], var))

                # ── Axioms 6 & 7 : Vertical inequality ───────────────────────
                if r > 0:
                    v = self.vert_const[r - 1][c]
                    if v == 1:
                        self.predicates.append(
                            LessV(self.variables[(r - 1, c)], var))
                    elif v == -1:
                        self.predicates.append(
                            GreaterV(self.variables[(r - 1, c)], var))

        return self.variables

