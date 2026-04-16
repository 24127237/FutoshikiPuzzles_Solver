"""
Test file cho module kb_generator.
Kiem tra cac menh de CNF duoc tao ra cho bien, bat dang thuc ngang/doc va full KB.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.core.kb_generator import FutoshikiKBGenerator


def test_get_var_mapping():
    gen = FutoshikiKBGenerator(4)
    assert gen.get_var(0, 0, 1) == 1
    assert gen.get_var(0, 0, 4) == 4
    assert gen.get_var(0, 1, 1) == 5
    assert gen.get_var(1, 0, 1) == 17
    assert gen.get_var(3, 3, 4) == 64


def test_vertical_inequalities_less_than():
    n = 4
    gen = FutoshikiKBGenerator(n)
    vert = [
        [1, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]

    clauses = gen.generate_vertical_inequalities(vert)

    expected_first = [
        -gen.get_var(0, 0, 1),
        gen.get_var(1, 0, 2),
        gen.get_var(1, 0, 3),
        gen.get_var(1, 0, 4),
    ]
    expected_last = [-gen.get_var(0, 0, 4)]

    assert len(clauses) == n
    assert expected_first in clauses
    assert expected_last in clauses


def test_vertical_inequalities_greater_than():
    n = 4
    gen = FutoshikiKBGenerator(n)
    vert = [
        [-1, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]

    clauses = gen.generate_vertical_inequalities(vert)

    expected_first = [-gen.get_var(0, 0, 1)]
    expected_last = [
        -gen.get_var(0, 0, 4),
        gen.get_var(1, 0, 1),
        gen.get_var(1, 0, 2),
        gen.get_var(1, 0, 3),
    ]

    assert len(clauses) == n
    assert expected_first in clauses
    assert expected_last in clauses


def test_full_kb_contains_given_and_inequalities():
    n = 3
    gen = FutoshikiKBGenerator(n)

    grid = [
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 2],
    ]
    horiz = [
        [1, 0],
        [0, 0],
        [0, 0],
    ]
    vert = [
        [0, 0, 0],
        [0, -1, 0],
    ]

    kb = gen.generate_full_kb(grid, horiz, vert)

    given_1 = [gen.get_var(0, 0, 1)]
    given_2 = [gen.get_var(2, 2, 2)]
    horiz_clause = [
        -gen.get_var(0, 0, 1),
        gen.get_var(0, 1, 2),
        gen.get_var(0, 1, 3),
    ]
    vert_clause = [
        -gen.get_var(1, 1, 3),
        gen.get_var(2, 1, 1),
        gen.get_var(2, 1, 2),
    ]

    assert given_1 in kb
    assert given_2 in kb
    assert horiz_clause in kb
    assert vert_clause in kb


def main():
    tests = [
        test_get_var_mapping,
        test_vertical_inequalities_less_than,
        test_vertical_inequalities_greater_than,
        test_full_kb_contains_given_and_inequalities,
    ]

    passed = 0
    for test_fn in tests:
        test_fn()
        passed += 1
        print(f"[OK] {test_fn.__name__}")

    print(f"\nPassed {passed}/{len(tests)} tests for kb_generator.")


if __name__ == "__main__":
    main()
