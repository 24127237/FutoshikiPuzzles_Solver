# Futoshiki Puzzles Solver

## Overview

A constraint satisfaction problem (CSP) solver for Futoshiki puzzles implemented in Python. Futoshiki (Japanese for "inequality") is a logic puzzle similar to Sudoku. The solver provides multiple solving algorithms including Backtracking, Forward Chaining, A* search, and hybrid approaches.

## Features

- **Multiple Solving Algorithms**: Brute Force, Backtracking, Forward Chaining, Pure Backward Chaining, A* Search, and Hybrid approaches
- **GUI and CLI Interfaces**: User-friendly graphical interface and command-line options
- **Experiment Framework**: Built-in support for running experiments and analyzing solver performance
- **Flexible Input/Output**: Support for reading puzzles from files and outputting solutions

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Navigate to the project directory:
```bash
cd /path/to/FutoshikiPuzzles_Solver
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Running the Solver
Solve puzzles from the command line:
```bash
python main.py
```

## Directory Structure

- `src/` - Core solver implementation
  - `core/` - Core classes and utilities (KB, state, rules)
  - `solver/` - Different solving algorithms
  - `test/` - Unit tests
- `Inputs/` - Sample puzzle input files
- `Outputs/` - Solver output files
- `experiments/` - Experiment framework for benchmarking


## Running Experiments

To run performance experiments and generate reports:
```bash
cd experiments
python run_experiments.py
```

Results will be saved to `experiments/results/`
