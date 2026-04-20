"""
LAYER 2 & 4 — KNOWLEDGE BASE & FOL AXIOMS

Implements Horn clauses (Fact, Rule) and the KnowledgeBase storage.
Builds Futoshiki axioms as Facts and Rules encoded in the KB.

Predicate vocabulary (from the assignment):
  val(Cell, V)          — Cell is assigned value V              [Val(i,j,v)]
  given(Cell, V)        — Cell has pre-filled clue value V      [Given(i,j,v)]
  domain(Cell, V)       — V is in the domain of Cell            [free cell]
  neq(V1, V2)           — V1 ≠ V2                               [background]
  less_than(V1,V2)      — V1 < V2                               [Less(v1,v2)]
  greater_than(V1,V2)   — V1 > V2                               [background]
  row_uniq(C1,C2)       — different-valued cells in same row    [Axiom 2]
  col_uniq(C1,C2)       — different-valued cells in same col    [Axiom 3]
  lh(C1,C2)             — LessH: val(C1)<val(C2) horizontal     [Axiom 4]
  gh(C1,C2)             — GreaterH: val(C1)>val(C2) horizontal  [Axiom 5]
  lv(C1,C2)             — LessV: val(C1)<val(C2) vertical       [Axiom 6]
  gv(C1,C2)             — GreaterV: val(C1)>val(C2) vertical    [Axiom 7]
"""

from src.core.FOL import Atom, Number, Var, Compound


class Fact:
    """
    head.
    FOL: ground atom (or atom with free vars treated as universally quantified).
    e.g.  val(v_0_5, 5).
          given(v_3_0, 2).
    """
    def __init__(self, head: Compound):
        self.head = head

    def __repr__(self):
        return f"{self.head}."


class Rule:
    """
    head :- body[0], body[1], …, body[N-1].
    FOL: ∀X̄: body[0](X̄) ∧ … ∧ body[N-1](X̄)  ⟹  head(X̄)

    Used for derived predicates:
      neq, less_than, greater_than,
      row_unique, col_unique,
      horiz_less, horiz_greater,
      vert_less,  vert_greater.
    """
    def __init__(self, head: Compound, body: list):
        self.head = head
        self.body = body          # list[Term]  (goals in the body)

    def __repr__(self):
        body_str = ", ".join(map(repr, self.body))
        return f"{self.head} :- {body_str}."


class KnowledgeBase:
    """
    The KB is the finite set of all Horn clauses.
    Indexed by (functor, arity) for O(1) lookup during resolution.

    Usage:
        kb = KnowledgeBase()
        kb.add(Fact(...))
        kb.add(Rule(...))
        clauses = kb.get("val", 2)   # → list of Fact/Rule with head val/2
    """
    def __init__(self):
        self._db: dict = {}          # (functor, arity) → list[Fact | Rule]

    def add(self, clause):
        key = (clause.head.functor, len(clause.head.args))
        self._db.setdefault(key, []).append(clause)

    def get(self, functor: str, arity: int) -> list:
        return self._db.get((functor, arity), [])

    def __repr__(self):
        lines = []
        for clauses in self._db.values():
            for c in clauses:
                lines.append(repr(c))
        return "\n".join(lines)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def cell(r, c) -> Atom:
    """Canonical cell name atom: cell(0,2) → Atom("v_0_2")"""
    return Atom(f"v_{r}_{c}")


# =============================================================================
# AXIOM 1a — Given(i,j,v)  ⟹  Val(i,j,v)
# =============================================================================

def add_given_implies_val(kb: KnowledgeBase):
    """
    val(Cell, V) :- given(Cell, V).
    """
    C = Var("Cell_G")
    V = Var("V_G")
    kb.add(Rule(
        Compound("val",   [C, V]),
        [Compound("given", [C, V])]
    ))


# =============================================================================
# AXIOM 1b — ¬Given(i,j,_)  ⟹  Val(i,j,1) ∨ … ∨ Val(i,j,N)
# =============================================================================

def add_free_domain(kb: KnowledgeBase, r: int, c: int, n: int):
    """
    For each v in {1,…,N}: val(v_r_c, v).
    Creates N disjunctive branches for the free cell at (r,c).
    """
    for v in range(1, n + 1):
        kb.add(Fact(Compound("val", [cell(r, c), Number(v)])))


# =============================================================================
# AXIOM 2 — Row Uniqueness
# =============================================================================

def add_row_unique(kb: KnowledgeBase):
    """
    row_uniq(C1, C2) :-
        val(C1, V1), val(C2, V2), neq(V1, V2).
    """
    C1 = Var("C1_RU"); C2 = Var("C2_RU")
    V1 = Var("V1_RU"); V2 = Var("V2_RU")
    kb.add(Rule(
        Compound("row_uniq", [C1, C2]),
        [
            Compound("val", [C1, V1]),
            Compound("val", [C2, V2]),
            Compound("neq", [V1, V2]),
        ]
    ))


# =============================================================================
# AXIOM 3 — Column Uniqueness
# =============================================================================

def add_col_unique(kb: KnowledgeBase):
    """
    col_uniq(C1, C2) :-
        val(C1, V1), val(C2, V2), neq(V1, V2).
    """
    C1 = Var("C1_CU"); C2 = Var("C2_CU")
    V1 = Var("V1_CU"); V2 = Var("V2_CU")
    kb.add(Rule(
        Compound("col_uniq", [C1, C2]),
        [
            Compound("val", [C1, V1]),
            Compound("val", [C2, V2]),
            Compound("neq", [V1, V2]),
        ]
    ))


# =============================================================================
# AXIOM 4 — Horizontal LessH
# =============================================================================

def add_horiz_less(kb: KnowledgeBase):
    """
    lh(C1, C2) :- val(C1, V1), val(C2, V2), less_than(V1, V2).
    """
    C1 = Var("C1_LH"); C2 = Var("C2_LH")
    V1 = Var("V1_LH"); V2 = Var("V2_LH")
    kb.add(Rule(
        Compound("lh", [C1, C2]),
        [
            Compound("val",       [C1, V1]),
            Compound("val",       [C2, V2]),
            Compound("less_than", [V1, V2]),
        ]
    ))


# =============================================================================
# AXIOM 5 — Horizontal GreaterH
# =============================================================================

def add_horiz_greater(kb: KnowledgeBase):
    """
    gh(C1, C2) :- val(C1, V1), val(C2, V2), greater_than(V1, V2).
    """
    C1 = Var("C1_GH"); C2 = Var("C2_GH")
    V1 = Var("V1_GH"); V2 = Var("V2_GH")
    kb.add(Rule(
        Compound("gh", [C1, C2]),
        [
            Compound("val",          [C1, V1]),
            Compound("val",          [C2, V2]),
            Compound("greater_than", [V1, V2]),
        ]
    ))


# =============================================================================
# AXIOM 6 — Vertical LessV
# =============================================================================

def add_vert_less(kb: KnowledgeBase):
    """
    lv(C1, C2) :- val(C1, V1), val(C2, V2), less_than(V1, V2).
    """
    C1 = Var("C1_LV"); C2 = Var("C2_LV")
    V1 = Var("V1_LV"); V2 = Var("V2_LV")
    kb.add(Rule(
        Compound("lv", [C1, C2]),
        [
            Compound("val",       [C1, V1]),
            Compound("val",       [C2, V2]),
            Compound("less_than", [V1, V2]),
        ]
    ))


# =============================================================================
# AXIOM 7 — Vertical GreaterV
# =============================================================================

def add_vert_greater(kb: KnowledgeBase):
    """
    gv(C1, C2) :- val(C1, V1), val(C2, V2), greater_than(V1, V2).
    """
    C1 = Var("C1_GV"); C2 = Var("C2_GV")
    V1 = Var("V1_GV"); V2 = Var("V2_GV")
    kb.add(Rule(
        Compound("gv", [C1, C2]),
        [
            Compound("val",          [C1, V1]),
            Compound("val",          [C2, V2]),
            Compound("greater_than", [V1, V2]),
        ]
    ))


# =============================================================================
# KB BUILDER
# =============================================================================

def build_kb(n, initial_grid, horiz_const, vert_const) -> KnowledgeBase:
    """
    Populate the KnowledgeBase with:
      • Structural axiom rules  (Axioms 1a, 2–7)
      • Ground facts for given cells  (Axiom 1a: given/2 facts)
      • Domain facts for free cells   (Axiom 1b: val/2 facts)
      • Constraint facts: lh/gh/lv/gv — ground atoms encoding puzzle layout
    """
    kb = KnowledgeBase()

    # ── Structural rules (one per axiom) ──────────────────────────────────────
    add_given_implies_val(kb)
    add_row_unique(kb)
    add_col_unique(kb)
    add_horiz_less(kb)
    add_horiz_greater(kb)
    add_vert_less(kb)
    add_vert_greater(kb)

    # ── Ground facts from puzzle data ─────────────────────────────────────────
    for r in range(n):
        for c in range(n):
            v = initial_grid[r][c]
            if v != 0:
                # Axiom 1a: given(v_r_c, v).
                kb.add(Fact(Compound("given", [cell(r, c), Number(v)])))
            else:
                # Axiom 1b: val(v_r_c, 1). … val(v_r_c, N).
                add_free_domain(kb, r, c, n)

    # ── Horizontal inequality facts ───────────────────────────────────────────
    for r in range(n):
        for c in range(n - 1):
            h = horiz_const[r][c]
            if h == 1:
                # LessH(r,c): lh(v_r_c, v_r_{c+1}).
                kb.add(Fact(Compound("lh", [cell(r, c), cell(r, c + 1)])))
            elif h == -1:
                # GreaterH(r,c): gh(v_r_c, v_r_{c+1}).
                kb.add(Fact(Compound("gh", [cell(r, c), cell(r, c + 1)])))

    # ── Vertical inequality facts ─────────────────────────────────────────────
    for r in range(n - 1):
        for c in range(n):
            v = vert_const[r][c]
            if v == 1:
                # LessV(r,c): lv(v_r_c, v_{r+1}_c).
                kb.add(Fact(Compound("lv", [cell(r, c), cell(r + 1, c)])))
            elif v == -1:
                # GreaterV(r,c): gv(v_r_c, v_{r+1}_c).
                kb.add(Fact(Compound("gv", [cell(r, c), cell(r + 1, c)])))

    return kb

