# Experiments Folder

This folder contains a reproducible benchmark script for:
- forward_chaining
- forward_chaining_fallback_astar
- forward_chaining_fallback_backtracking
- backward_chaining
- astar
- backtracking

## Output artifacts

Running the script generates:
- `experiments/results/detailed_results.csv`
- `experiments/results/summary_results.csv`
- `experiments/results/summary_report.md`
- `experiments/results/plots/*.png`

## Local run

From project root:

```powershell
uv run .\experiments\run_experiments.py --repeats 3 --timeout 60 --jobs -1
```

## Kaggle run

1. Upload project folder as Dataset/Input.
2. Set working directory to the project root in notebook or script.
3. Run:

```python
!python experiments/run_experiments.py --repeats 3 --timeout 60 --jobs -1
```

4. Collect files in `experiments/results` for submission/report.

## Notes

- `--timeout` is per algorithm per input per repeat.
- `--jobs` controls parallel workers for joblib (`-1` means all cores).
- If timeout happens, result is recorded with `status=timeout` and still included in summary.
- Memory is measured with `tracemalloc` peak memory in KB.
- For fallback modes, detailed CSV includes:
	- `fallback_used`
	- `fallback_algorithm`
	- `fallback_expansions`
	- `fc_inferences`
	- `fc_iterations`
