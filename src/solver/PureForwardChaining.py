from collections import defaultdict, deque

from src.core.prop_kb_generator import FutoshikiKBGenerator


class PureForwardChainingSolver:
    """
    Pure Rule-based forward chaining for Futoshiki.
    This solver strictly uses pure Modus Ponens inference on Horn clauses.
    It does NOT use any CSP techniques like AC-3 constraint propagation or the State object.
    """

    def __init__(self, rules):
        self.rules = rules
        self.kb_generator = FutoshikiKBGenerator(self.rules.n)
        self.horn_rules = []
        self.rules_by_premise = {}
        self.stats = {"num_inferences": 0, "fc_iterations": 0}

    def solve(self, initial_state):
        # We accept initial_state to match the interface, but we ONLY use initial_state.grid
        self.stats = {"num_inferences": 0, "fc_iterations": 1}
        grid = initial_state.grid
        
        # Build Horn KB once per puzzle
        initial_facts, horn_rules = self.kb_generator.generate_horn_kb(
            grid,
            self.rules.horiz_const,
            self.rules.vert_const,
        )
        
        self.horn_rules = horn_rules
        self.rules_by_premise = self._index_rules_by_premise(self.horn_rules)

        # Run Modus Ponens closure exactly once until fixpoint
        inferred_facts, is_consistent = self._modus_ponens_closure(initial_facts)
        
        if not is_consistent:
            return None

        # Build the final grid from inferred positive facts
        final_grid = self._build_grid_from_facts(inferred_facts)
        
        if final_grid is None:
            return None # Conflict found during grid construction
            
        if not self.rules.is_solved(final_grid):
            return None
            
        return final_grid

    def _index_rules_by_premise(self, horn_rules):
        indexed = defaultdict(list)
        for idx, (body, _) in enumerate(horn_rules):
            for lit in body:
                indexed[lit].append(idx)
        return indexed

    def _modus_ponens_closure(self, initial_facts):
        """
        Pure Modus Ponens on Horn clauses.
        """
        inferred = set(initial_facts)

        # Check initial consistency
        for lit in list(inferred):
            if -lit in inferred:
                return inferred, False

        # remaining tracks how many unfulfilled premises are left for each rule
        remaining = [len(body) for body, _ in self.horn_rules]
        agenda = deque(inferred)

        while agenda:
            fact = agenda.popleft()
            
            # Find all rules where this fact is a premise
            for rule_idx in self.rules_by_premise.get(fact, []):
                remaining[rule_idx] -= 1
                
                # If all premises are fulfilled, the head can be inferred
                if remaining[rule_idx] == 0:
                    head = self.horn_rules[rule_idx][1]
                    
                    if -head in inferred:
                        # Contradiction found! (+X and -X are both inferred)
                        return inferred, False
                        
                    if head not in inferred:
                        inferred.add(head)
                        self.stats["num_inferences"] += 1
                        agenda.append(head)

        return inferred, True

    def _build_grid_from_facts(self, inferred_facts):
        n = self.rules.n
        final_grid = [[0 for _ in range(n)] for _ in range(n)]
        
        for lit in inferred_facts:
            if lit > 0: # Positive literal means Val(r, c, v) is true
                r, c, v = self.kb_generator.decode_var(lit)
                if final_grid[r][c] != 0 and final_grid[r][c] != v:
                    return None # Invalid/Contradiction
                final_grid[r][c] = v
                
        return final_grid
