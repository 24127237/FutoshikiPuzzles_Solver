"""
LAYER 1 — FIRST-ORDER LOGIC TERMS (Herbrand Universe)

Implements the Herbrand universe for Futoshiki:
  • Atom     — ground constant (cell names, predicates)
  • Number   — integer constant (cell values 1..N)
  • Var      — logical variable (unified via substitution)
  • Compound — structured term (predicate application)
"""


class Term:
    """Abstract base for all Herbrand-universe objects."""
    def walk(self, subst):
        """Chase variable bindings until we hit a non-Var or unbound Var."""
        return self


class Atom(Term):
    """
    Ground constant — e.g. Atom("v_0_0"), Atom("less"), Atom("neq")
    FOL: 0-ary function symbol.
    """
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Atom) and self.name == other.name

    def __hash__(self):
        return hash(("Atom", self.name))


class Number(Term):
    """
    Integer constant — e.g. Number(3)
    FOL: element of the index sort {1, …, N}.
    """
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        return isinstance(other, Number) and self.value == other.value

    def __hash__(self):
        return hash(("Number", self.value))


class Var(Term):
    """
    Logical variable — e.g. Var("X"), Var("V_0_0")
    FOL: universally-quantified variable; unified by substitution.
    """
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name

    def __hash__(self):
        return hash(("Var", self.name))

    def walk(self, subst: dict):
        """
        Variable dereferencing (simple substitution, no occurs-check).
        Follows the binding chain: X→Y→3  becomes  Number(3).
        """
        t = self
        while isinstance(t, Var) and t.name in subst:
            t = subst[t.name]
        return t


class Compound(Term):
    """
    Structured term — Compound(functor, [arg1, …, argN])
    FOL: n-ary function / predicate symbol applied to terms.

    Examples:
      val(v_0_0, 3)    → Compound("val",     [Atom("v_0_0"), Number(3)])
      less(X, Y)       → Compound("less",    [Var("X"), Var("Y")])
      neq(X, Y)        → Compound("neq",     [Var("X"), Var("Y")])
      lh(v_0_2, v_0_3) → Compound("lh",     [Atom("v_0_2"), Atom("v_0_3")])
    """
    def __init__(self, functor: str, args: list):
        self.functor = functor
        self.args    = args          # list[Term]

    def __repr__(self):
        return f"{self.functor}({', '.join(map(repr, self.args))})"

    def __eq__(self, other):
        return (isinstance(other, Compound) and
                self.functor == other.functor and
                self.args == other.args)

    def __hash__(self):
        return hash(("Compound", self.functor, tuple(self.args)))
