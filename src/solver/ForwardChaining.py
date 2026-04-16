class ForwardChainingSolver:
    """
    Rule-based forward chaining for Futoshiki.
    The solver repeatedly infers forced values, then falls back to DFS when needed.
    """

    def __init__(self, rules):
        self.rules = rules

    def solve(self, initial_state):
        state = initial_state.clone()

        if not self._forward_chain(state):
            return None

        if self.rules.is_solved(state.grid):
            return state.grid

        result = self._search(state)
        if result is None:
            return None
        return result.grid

    def _search(self, state):
        if self.rules.is_solved(state.grid):
            return state

        cell = state.get_mrv_cell()
        if cell is None:
            return state if self.rules.is_solved(state.grid) else None

        row, col = cell
        domain = state.possible_values[row][col]

        for value in self._iter_domain_values(domain, state.n):
            next_state = state.clone()
            if not next_state.assign(row, col, value, self.rules):
                continue

            if not self._forward_chain(next_state):
                continue

            result = self._search(next_state)
            if result is not None:
                return result

        return None

    def _forward_chain(self, state):
        """
        Keep applying deterministic inference rules until no new facts can be derived.
        """
        while True:
            made_progress = False

            # Contradiction check: empty cell with empty domain.
            for r in range(state.n):
                for c in range(state.n):
                    if state.grid[r][c] == 0 and state.possible_values[r][c] == 0:
                        return False

            # Rule 1: Single-domain cell must be assigned.
            for r in range(state.n):
                for c in range(state.n):
                    if state.grid[r][c] != 0:
                        continue

                    domain = state.possible_values[r][c]
                    if domain.bit_count() == 1:
                        value = self._single_value_from_mask(domain)
                        if not state.assign(r, c, value, self.rules):
                            return False
                        made_progress = True

            if made_progress:
                continue

            # Rule 2: Hidden single in each row.
            for r in range(state.n):
                for value in range(1, state.n + 1):
                    placed_col = self._find_value_in_row(state, r, value)
                    if placed_col is not None:
                        continue

                    candidates = []
                    bit = 1 << value
                    for c in range(state.n):
                        if state.grid[r][c] == 0 and (state.possible_values[r][c] & bit):
                            candidates.append(c)

                    if len(candidates) == 0:
                        return False

                    if len(candidates) == 1:
                        if not state.assign(r, candidates[0], value, self.rules):
                            return False
                        made_progress = True

            if made_progress:
                continue

            # Rule 3: Hidden single in each column.
            for c in range(state.n):
                for value in range(1, state.n + 1):
                    placed_row = self._find_value_in_col(state, c, value)
                    if placed_row is not None:
                        continue

                    candidates = []
                    bit = 1 << value
                    for r in range(state.n):
                        if state.grid[r][c] == 0 and (state.possible_values[r][c] & bit):
                            candidates.append(r)

                    if len(candidates) == 0:
                        return False

                    if len(candidates) == 1:
                        if not state.assign(candidates[0], c, value, self.rules):
                            return False
                        made_progress = True

            if not made_progress:
                break

        return self.rules.is_valid(state.grid)

    @staticmethod
    def _iter_domain_values(mask, n):
        for value in range(1, n + 1):
            if mask & (1 << value):
                yield value

    @staticmethod
    def _single_value_from_mask(mask):
        # mask is guaranteed to have exactly one set bit > 0.
        return mask.bit_length() - 1

    @staticmethod
    def _find_value_in_row(state, row, value):
        for c in range(state.n):
            if state.grid[row][c] == value:
                return c
        return None

    @staticmethod
    def _find_value_in_col(state, col, value):
        for r in range(state.n):
            if state.grid[r][col] == value:
                return r
        return None
