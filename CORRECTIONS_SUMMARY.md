# Corrections Summary

## Scope

Only these two areas were corrected:
- KB generation
- Forward chaining

FOL/backward-chaining parts were intentionally left unchanged.

## What Was Corrected

### 1. Added Horn-KB support in KB module

File: [src/core/kb_generator.py](src/core/kb_generator.py)

Changes:
- Added variable decode helper:
  - `decode_var(var_id)`
- Added Horn KB fact generation from givens:
  - `generate_horn_facts_from_grid(grid)`
- Added Horn rule generation for forward inference:
  - `generate_horn_rules(horiz_const, vert_const)`
- Added combined Horn KB API:
  - `generate_horn_kb(grid, horiz_const, vert_const)`

Implemented Horn rule groups:
- Cell exclusivity implications
- Row/column uniqueness implications
- Horizontal/vertical inequality implications

### 2. Reworked forward chaining to use Modus Ponens over Horn KB

File: [src/solver/FCHybrid.py](src/solver/FCHybrid.py)

Changes:
- Replaced hardcoded rule-propagation flow with Horn-KB-based inference.
- Built Horn rules once per puzzle, then reused them.
- Added fact extraction from current domains/assignments:
  - `_extract_facts_from_state(state)`
- Added indexed Modus Ponens closure:
  - `_index_rules_by_premise(horn_rules)`
  - `_modus_ponens_closure(initial_facts)`
- Added application of inferred literals back to state:
  - `_apply_inferred_facts(state, inferred_facts)`
- Kept contradiction checks and domain consistency checks.

## Simplification Pass Applied

The code was simplified while preserving behavior:
- Removed non-essential Horn rule families to keep KB logic minimal.
- Kept a small rule-indexing helper because fully naive scanning made large tests much slower.
- Removed static-analysis warnings by initializing the KB generator in solver construction.

## Validation

- KB generator tests passed:
  - [src/test/test_kb_generator.py](src/test/test_kb_generator.py)
- Forward chaining tests were rerun and passed through large cases during validation runs:
  - [src/test/test_forward_chaining.py](src/test/test_forward_chaining.py)

## Files Modified

- [src/core/kb_generator.py](src/core/kb_generator.py)
- [src/solver/FCHybrid.py](src/solver/FCHybrid.py)
