from collections import defaultdict, deque

from src.core.kb_generator import FutoshikiKBGenerator


class ForwardChainingSolver:
    """
    Rule-based forward chaining for Futoshiki.
    The solver uses pure forward chaining (Modus Ponens + domain propagation)
    until reaching a fixpoint.
    """

    def __init__(self, rules):
        self.rules = rules
        self.kb_generator = FutoshikiKBGenerator(self.rules.n)
        self.horn_rules = []
        self.rules_by_premise = {}

    def solve(self, initial_state):
        state = initial_state.clone()

        # Build Horn KB once per puzzle. Inference will run as Modus Ponens over this KB.
        self.horn_rules = self.kb_generator.generate_horn_rules(
            self.rules.horiz_const,
            self.rules.vert_const,
        )
        self.rules_by_premise = self._index_rules_by_premise(self.horn_rules)

        if not self._forward_chain(state):
            return None

        if not self.rules.is_solved(state.grid):
            return None
        return state.grid

    def _forward_chain(self, state):
        """
        Forward chaining via Modus Ponens on Horn KB until fixpoint.
        """
        while True:
            if not self._check_non_empty_domains(state):
                return False

            seed_facts = self._extract_facts_from_state(state)
            inferred_facts, is_consistent = self._modus_ponens_closure(seed_facts)
            if not is_consistent:
                return False

            is_consistent, made_progress = self._apply_inferred_facts(state, inferred_facts)
            if not is_consistent:
                return False

            if not made_progress:
                break

        return self._check_non_empty_domains(state) and self.rules.is_valid(state.grid)

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
    def _check_non_empty_domains(state):
        for r in range(state.n):
            for c in range(state.n):
                if state.grid[r][c] == 0 and state.possible_values[r][c] == 0:
                    return False
        return True

    @staticmethod
    def _index_rules_by_premise(horn_rules):
        indexed = defaultdict(list)
        for idx, (body, _) in enumerate(horn_rules):
            for lit in body:
                indexed[lit].append(idx)
        return indexed

    def _extract_facts_from_state(self, state):
        """
        Encode current state to signed literals:
        +var: Val(r,c,v) is true
        -var: Val(r,c,v) is false
        """
        facts = set()

        for r in range(state.n):
            for c in range(state.n):
                assigned_val = state.grid[r][c]
                domain = state.possible_values[r][c]

                if assigned_val != 0:
                    facts.add(self.kb_generator.get_var(r, c, assigned_val))

                if assigned_val == 0 and domain.bit_count() == 1:
                    facts.add(self.kb_generator.get_var(r, c, self._single_value_from_mask(domain)))

                for v in range(1, state.n + 1):
                    bit = 1 << v
                    if (domain & bit) == 0:
                        facts.add(-self.kb_generator.get_var(r, c, v))

        return facts

    def _modus_ponens_closure(self, initial_facts):
        inferred = set(initial_facts)

        for lit in list(inferred):
            if -lit in inferred:
                return inferred, False

        remaining = [len(body) for body, _ in self.horn_rules]
        agenda = deque(inferred)

        while agenda:
            fact = agenda.popleft()
            for rule_idx in self.rules_by_premise.get(fact, []):
                remaining[rule_idx] -= 1
                if remaining[rule_idx] != 0:
                    continue

                head = self.horn_rules[rule_idx][1]
                if -head in inferred:
                    return inferred, False
                if head not in inferred:
                    inferred.add(head)
                    agenda.append(head)

        return inferred, True

    def _apply_inferred_facts(self, state, inferred_facts):
        made_progress = False

        # Apply positive facts first so assign() can run AC3 propagation early.
        positive_facts = [lit for lit in inferred_facts if lit > 0]
        negative_facts = [lit for lit in inferred_facts if lit < 0]

        for lit in positive_facts:
            r, c, v = self.kb_generator.decode_var(lit)
            current = state.grid[r][c]

            if current != 0 and current != v:
                return False, made_progress

            if current == 0:
                if (state.possible_values[r][c] & (1 << v)) == 0:
                    return False, made_progress
                if not state.assign(r, c, v, self.rules):
                    return False, made_progress
                made_progress = True

        for lit in negative_facts:
            var_id = -lit
            r, c, v = self.kb_generator.decode_var(var_id)

            if state.grid[r][c] == v:
                return False, made_progress

            if state.grid[r][c] != 0:
                continue

            old_domain = state.possible_values[r][c]
            new_domain = old_domain & ~(1 << v)

            if new_domain == 0:
                return False, made_progress

            if new_domain != old_domain:
                state.possible_values[r][c] = new_domain
                made_progress = True

                if new_domain.bit_count() == 1:
                    forced_value = self._single_value_from_mask(new_domain)
                    if not state.assign(r, c, forced_value, self.rules):
                        return False, made_progress
                    made_progress = True

        return True, made_progress
