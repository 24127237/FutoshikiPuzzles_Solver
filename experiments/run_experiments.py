import argparse
import csv
import multiprocessing as mp
import os
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.io_handler import read_input_file
from src.core.rules import FutoshikiRules
from src.core.state import State
from src.solver.Astar import AstarSolver
from src.solver.Backtracking import BacktrackingSolver
from src.solver.Backward import BackwardSolver
from src.solver.ForwardChaining import ForwardChainingSolver

ALGORITHMS = [
    "forward_chaining",
    "forward_chaining_fallback_astar",
    "forward_chaining_fallback_backtracking",
    "backward_chaining",
    "astar",
    "backtracking",
]


def detect_difficulty(input_path: Path) -> str:
    with input_path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip().lower()
            if not line:
                continue
            if line.startswith("#"):
                if "easy" in line:
                    return "easy"
                if "extreme" in line:
                    return "extreme"
            else:
                break
    return "unknown"


def run_algorithm_once(algorithm: str, input_path: str) -> dict:
    n, grid, horiz, vert = read_input_file(input_path)
    rules = FutoshikiRules(n, horiz, vert)

    tracemalloc.start()
    t0 = time.perf_counter()

    solved = False
    result_grid = None
    stats = {}
    fallback_used = 0
    fallback_algorithm = ""
    fallback_expansions = None
    fc_inferences = None
    fc_iterations = None

    if algorithm == "forward_chaining":
        solver = ForwardChainingSolver(rules)
        result_grid = solver.solve(State(n, grid, rules))
        stats = dict(getattr(solver, "stats", {}))
        fc_inferences = stats.get("num_inferences")
        fc_iterations = stats.get("fc_iterations")
    elif algorithm == "forward_chaining_fallback_astar":
        fc_solver = ForwardChainingSolver(rules)
        initial_state = State(n, grid, rules)
        result_grid = fc_solver.solve(initial_state)
        fc_stats = dict(getattr(fc_solver, "stats", {}))
        fc_inferences = fc_stats.get("num_inferences")
        fc_iterations = fc_stats.get("fc_iterations")

        if result_grid is None:
            fallback_used = 1
            fallback_algorithm = "astar"
            astar_solver = AstarSolver()
            path = astar_solver.solve(State(n, grid, rules), rules)
            result_grid = path[-1] if path else None
            fallback_expansions = dict(getattr(astar_solver, "stats", {})).get("num_expansions")
            stats = {
                "num_inferences": fc_inferences,
                "fc_iterations": fc_iterations,
                "num_expansions": fallback_expansions,
            }
        else:
            stats = {
                "num_inferences": fc_inferences,
                "fc_iterations": fc_iterations,
            }
    elif algorithm == "forward_chaining_fallback_backtracking":
        fc_solver = ForwardChainingSolver(rules)
        initial_state = State(n, grid, rules)
        result_grid = fc_solver.solve(initial_state)
        fc_stats = dict(getattr(fc_solver, "stats", {}))
        fc_inferences = fc_stats.get("num_inferences")
        fc_iterations = fc_stats.get("fc_iterations")

        if result_grid is None:
            fallback_used = 1
            fallback_algorithm = "backtracking"
            bt_solver = BacktrackingSolver(rules)
            result_grid = bt_solver.solve(State(n, grid, rules))
            fallback_expansions = dict(getattr(bt_solver, "stats", {})).get("num_expansions")
            stats = {
                "num_inferences": fc_inferences,
                "fc_iterations": fc_iterations,
                "num_expansions": fallback_expansions,
            }
        else:
            stats = {
                "num_inferences": fc_inferences,
                "fc_iterations": fc_iterations,
            }
    elif algorithm == "backward_chaining":
        solver = BackwardSolver(n, horiz, vert)
        result_grid = solver.solve([row[:] for row in grid])
        stats = dict(getattr(solver, "stats", {}))
    elif algorithm == "astar":
        solver = AstarSolver()
        path = solver.solve(State(n, grid, rules), rules)
        result_grid = path[-1] if path else None
        stats = dict(getattr(solver, "stats", {}))
    elif algorithm == "backtracking":
        solver = BacktrackingSolver(rules)
        result_grid = solver.solve(State(n, grid, rules))
        stats = dict(getattr(solver, "stats", {}))
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    t1 = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if result_grid is not None:
        solved = rules.is_solved(result_grid)

    if algorithm == "forward_chaining_fallback_astar" or algorithm == "forward_chaining_fallback_backtracking":
        # For fallback modes, treat total effort as FC inference effort + fallback search effort.
        fc_part = fc_inferences if fc_inferences is not None else 0
        fb_part = fallback_expansions if fallback_expansions is not None else 0
        num_main = fc_part + fb_part
    elif algorithm in ("forward_chaining", "backward_chaining"):
        num_main = stats.get("num_inferences")
    else:
        num_main = stats.get("num_expansions")

    return {
        "algorithm": algorithm,
        "n": n,
        "solved": int(bool(solved)),
        "runtime_ms": (t1 - t0) * 1000,
        "memory_current_kb": current_mem / 1024,
        "memory_peak_kb": peak_mem / 1024,
        "num_inferences_or_expansions": num_main,
        "num_goal_expansions": stats.get("num_goal_expansions"),
        "fc_inferences": fc_inferences,
        "fc_iterations": fc_iterations,
        "fallback_used": fallback_used,
        "fallback_algorithm": fallback_algorithm,
        "fallback_expansions": fallback_expansions,
        "status": "ok",
        "error": "",
    }


def _worker(queue: mp.Queue, algorithm: str, input_path: str):
    try:
        queue.put(run_algorithm_once(algorithm, input_path))
    except Exception as exc:
        queue.put(
            {
                "algorithm": algorithm,
                "n": None,
                "solved": 0,
                "runtime_ms": None,
                "memory_current_kb": None,
                "memory_peak_kb": None,
                "num_inferences_or_expansions": None,
                "num_goal_expansions": None,
                "fc_inferences": None,
                "fc_iterations": None,
                "fallback_used": 0,
                "fallback_algorithm": "",
                "fallback_expansions": None,
                "status": "error",
                "error": str(exc),
            }
        )


def run_with_timeout(algorithm: str, input_path: Path, timeout_sec: int) -> dict:
    ctx = mp.get_context("spawn")
    queue = ctx.Queue()
    proc = ctx.Process(target=_worker, args=(queue, algorithm, str(input_path)))

    wall_t0 = time.perf_counter()
    proc.start()
    proc.join(timeout=timeout_sec)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        wall_t1 = time.perf_counter()
        return {
            "algorithm": algorithm,
            "n": None,
            "solved": 0,
            "runtime_ms": (wall_t1 - wall_t0) * 1000,
            "memory_current_kb": None,
            "memory_peak_kb": None,
            "num_inferences_or_expansions": None,
            "num_goal_expansions": None,
            "fc_inferences": None,
            "fc_iterations": None,
            "fallback_used": 0,
            "fallback_algorithm": "",
            "fallback_expansions": None,
            "status": "timeout",
            "error": f"timeout_{timeout_sec}s",
        }

    if queue.empty():
        wall_t1 = time.perf_counter()
        return {
            "algorithm": algorithm,
            "n": None,
            "solved": 0,
            "runtime_ms": (wall_t1 - wall_t0) * 1000,
            "memory_current_kb": None,
            "memory_peak_kb": None,
            "num_inferences_or_expansions": None,
            "num_goal_expansions": None,
            "fc_inferences": None,
            "fc_iterations": None,
            "fallback_used": 0,
            "fallback_algorithm": "",
            "fallback_expansions": None,
            "status": "error",
            "error": "worker_returned_no_data",
        }

    return queue.get()


def safe_mean(values):
    clean = [v for v in values if v is not None]
    if not clean:
        return None
    return statistics.mean(clean)


def safe_stdev(values):
    clean = [v for v in values if v is not None]
    if len(clean) < 2:
        return 0.0
    return statistics.pstdev(clean)


def write_csv(path: Path, rows: list, fieldnames: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def aggregate_results(rows: list) -> list:
    grouped = {}
    for row in rows:
        alg = row["algorithm"]
        grouped.setdefault(alg, []).append(row)

    summary_rows = []
    for alg, items in grouped.items():
        solve_rate = safe_mean([item["solved"] for item in items])
        runtimes = [item["runtime_ms"] for item in items if item["status"] == "ok"]
        memories = [item["memory_peak_kb"] for item in items if item["status"] == "ok"]
        inferences = [item["num_inferences_or_expansions"] for item in items if item["status"] == "ok"]
        fallback_usage = [item.get("fallback_used") for item in items if item["status"] == "ok"]

        summary_rows.append(
            {
                "algorithm": alg,
                "total_runs": len(items),
                "ok_runs": sum(1 for x in items if x["status"] == "ok"),
                "timeout_runs": sum(1 for x in items if x["status"] == "timeout"),
                "error_runs": sum(1 for x in items if x["status"] == "error"),
                "solve_rate": solve_rate if solve_rate is not None else 0.0,
                "avg_runtime_ms": safe_mean(runtimes),
                "std_runtime_ms": safe_stdev(runtimes),
                "avg_memory_peak_kb": safe_mean(memories),
                "avg_inferences_or_expansions": safe_mean(inferences),
                "fallback_usage_rate": safe_mean(fallback_usage),
            }
        )

    summary_rows.sort(key=lambda x: (-x["solve_rate"], x["avg_runtime_ms"] or float("inf")))
    return summary_rows


def format_value(value, digits=2):
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_summary_report(path: Path, summary_rows: list):
    lines = []
    lines.append("# Experiment Summary")
    lines.append("")
    if not summary_rows:
        lines.append("No results available.")
        path.write_text("\n".join(lines), encoding="utf-8")
        return

    best = summary_rows[0]
    lines.append(
        "Best overall by solve rate then runtime: "
        f"{best['algorithm']} (solve_rate={format_value(best['solve_rate'] * 100)}%, "
        f"avg_runtime_ms={format_value(best['avg_runtime_ms'])})."
    )
    lines.append("")
    lines.append("## Per-Algorithm")
    lines.append("")
    for row in summary_rows:
        lines.append(
            f"- {row['algorithm']}: solve_rate={format_value(row['solve_rate'] * 100)}%, "
            f"avg_runtime_ms={format_value(row['avg_runtime_ms'])}, "
            f"avg_memory_peak_kb={format_value(row['avg_memory_peak_kb'])}, "
            f"avg_inferences_or_expansions={format_value(row['avg_inferences_or_expansions'])}, "
            f"fallback_usage_rate={format_value((row.get('fallback_usage_rate') or 0) * 100)}%, "
            f"timeouts={row['timeout_runs']}, errors={row['error_runs']}"
        )

    lines.append("")
    lines.append("## Discussion Template (Use in Report)")
    lines.append("")
    lines.append("- Which performs best and why: prioritize solve rate first, then runtime and memory tradeoff.")
    lines.append("- Preferred conditions:")
    lines.append("  FC: strong local constraints, good for fast pruning/inference.")
    lines.append("  FC+fallback: practical mode when you want FC pruning benefits but still need full-solve robustness.")
    lines.append("  Backward Chaining: query-driven reasoning and proof traceability.")
    lines.append("  A*: robust full-solution search with guided expansion.")
    lines.append("  Backtracking: simple baseline, can be effective with MRV/forward-checking.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def generate_plots(rows: list, summary_rows: list, output_dir: Path):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("[WARN] matplotlib unavailable, skip plots.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    algs = [row["algorithm"] for row in summary_rows]
    solve_rates = [row["solve_rate"] * 100 for row in summary_rows]
    avg_runtime = [row["avg_runtime_ms"] or 0 for row in summary_rows]
    avg_memory = [row["avg_memory_peak_kb"] or 0 for row in summary_rows]

    plt.figure(figsize=(8, 4.5))
    plt.bar(algs, solve_rates)
    plt.ylabel("Solve Rate (%)")
    plt.title("Solve Rate by Algorithm")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(output_dir / "solve_rate_by_algorithm.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.bar(algs, avg_runtime)
    plt.ylabel("Avg Runtime (ms)")
    plt.title("Average Runtime by Algorithm")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(output_dir / "runtime_by_algorithm.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.bar(algs, avg_memory)
    plt.ylabel("Avg Peak Memory (KB)")
    plt.title("Average Peak Memory by Algorithm")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(output_dir / "memory_by_algorithm.png", dpi=150)
    plt.close()

    # Runtime by board size for successful runs
    ok_rows = [r for r in rows if r["status"] == "ok" and r["runtime_ms"] is not None and r["n"] is not None]
    if ok_rows:
        by_alg_n = {}
        for r in ok_rows:
            by_alg_n.setdefault((r["algorithm"], r["n"]), []).append(r["runtime_ms"])

        plt.figure(figsize=(8, 4.5))
        for alg in ALGORITHMS:
            points = sorted([(n, safe_mean(v)) for (a, n), v in by_alg_n.items() if a == alg], key=lambda x: x[0])
            if not points:
                continue
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            plt.plot(xs, ys, marker="o", label=alg)

        plt.xlabel("Board size n")
        plt.ylabel("Avg Runtime (ms)")
        plt.title("Runtime vs Board Size")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "runtime_vs_board_size.png", dpi=150)
        plt.close()


def list_input_files(inputs_dir: Path):
    return sorted(inputs_dir.glob("inputs-*.txt"))


def main():
    parser = argparse.ArgumentParser(description="Benchmark FC/BC/A*/Backtracking on Futoshiki inputs")
    parser.add_argument("--repeats", type=int, default=3, help="Runs per algorithm per input")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout seconds per single run")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(PROJECT_ROOT / "experiments" / "results"),
        help="Directory to save csv/plots/summary",
    )
    parser.add_argument(
        "--plot-only",
        action="store_true",
        help="Only regenerate plots from existing CSV files in output-dir",
    )
    args = parser.parse_args()

    inputs_dir = PROJECT_ROOT / "Inputs"
    output_dir = Path(args.output_dir)
    plot_dir = output_dir / "plots"

    if args.plot_only:
        detailed_path = output_dir / "detailed_results.csv"
        summary_path = output_dir / "summary_results.csv"
        if not detailed_path.exists() or not summary_path.exists():
            raise RuntimeError("Missing CSV files for plot-only mode. Run full benchmark first.")

        rows = read_csv(detailed_path)
        summary_rows = read_csv(summary_path)

        # Convert numeric fields loaded from CSV strings.
        for row in rows:
            row["n"] = int(row["n"]) if row.get("n") not in (None, "", "None") else None
            row["runtime_ms"] = float(row["runtime_ms"]) if row.get("runtime_ms") not in (None, "", "None") else None

        for row in summary_rows:
            row["solve_rate"] = float(row["solve_rate"]) if row.get("solve_rate") not in (None, "", "None") else 0.0
            row["avg_runtime_ms"] = float(row["avg_runtime_ms"]) if row.get("avg_runtime_ms") not in (None, "", "None") else None
            row["avg_memory_peak_kb"] = float(row["avg_memory_peak_kb"]) if row.get("avg_memory_peak_kb") not in (None, "", "None") else None

        generate_plots(rows, summary_rows, plot_dir)
        print(f"[DONE] Plots saved in {plot_dir}")
        return

    input_files = list_input_files(inputs_dir)
    if not input_files:
        raise RuntimeError(f"No inputs found in: {inputs_dir}")

    rows = []
    print(f"[INFO] Found {len(input_files)} input files")
    print(f"[INFO] Repeats={args.repeats}, timeout={args.timeout}s")

    for input_path in input_files:
        input_id = input_path.stem.split("-")[-1]
        difficulty = detect_difficulty(input_path)

        for algorithm in ALGORITHMS:
            for run_id in range(1, args.repeats + 1):
                print(f"[RUN] input={input_path.name}, algo={algorithm}, repeat={run_id}")
                row = run_with_timeout(algorithm, input_path, args.timeout)
                row["input_file"] = input_path.name
                row["input_id"] = input_id
                row["difficulty"] = difficulty
                row["repeat_id"] = run_id
                rows.append(row)

    detailed_fields = [
        "input_file",
        "input_id",
        "n",
        "difficulty",
        "algorithm",
        "repeat_id",
        "status",
        "error",
        "solved",
        "runtime_ms",
        "memory_current_kb",
        "memory_peak_kb",
        "num_inferences_or_expansions",
        "num_goal_expansions",
        "fc_inferences",
        "fc_iterations",
        "fallback_used",
        "fallback_algorithm",
        "fallback_expansions",
    ]
    write_csv(output_dir / "detailed_results.csv", rows, detailed_fields)

    summary_rows = aggregate_results(rows)
    summary_fields = [
        "algorithm",
        "total_runs",
        "ok_runs",
        "timeout_runs",
        "error_runs",
        "solve_rate",
        "avg_runtime_ms",
        "std_runtime_ms",
        "avg_memory_peak_kb",
        "avg_inferences_or_expansions",
        "fallback_usage_rate",
    ]
    write_csv(output_dir / "summary_results.csv", summary_rows, summary_fields)

    write_summary_report(output_dir / "summary_report.md", summary_rows)
    generate_plots(rows, summary_rows, plot_dir)

    print("[DONE] Saved:")
    print(f"  - {output_dir / 'detailed_results.csv'}")
    print(f"  - {output_dir / 'summary_results.csv'}")
    print(f"  - {output_dir / 'summary_report.md'}")
    print(f"  - {plot_dir}")


if __name__ == "__main__":
    main()
