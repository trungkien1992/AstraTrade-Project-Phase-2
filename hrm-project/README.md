# Hierarchical Reasoning Model (HRM)

Complete implementation of the Hierarchical Reasoning Model from the paper "Hierarchical Reasoning Model" by Wang et al., 2025.

## Features

- ✅ Complete HRM architecture with hierarchical convergence
- ✅ One-step gradient approximation for memory efficiency
- ✅ Deep supervision training mechanism
- ✅ Adaptive Computation Time (ACT) with Q-learning
- ✅ Sudoku-Extreme dataset and environment
- ✅ Maze-Hard navigation tasks
- ✅ ARC-AGI challenge support
- ✅ Brain correspondence analysis tools
- ✅ Comprehensive evaluation suite

## Installation

```bash
# Clone and setup
cd hrm-project
pip install -r requirements.txt
```

## Quick Start

```python
from src.hrm.model import HierarchicalReasoningModel, HRMConfig

# Create model
config = HRMConfig(hidden_size=512, N=2, T=4)
model = HierarchicalReasoningModel(config)

# Train on Sudoku-Extreme
python scripts/train_sudoku.py

# Evaluate on benchmarks
python scripts/evaluate_all.py
```

## Project Structure

```
hrm-project/
├── src/
│   ├── hrm/              # Core HRM implementation
│   ├── datasets/         # Dataset loaders and processors
│   ├── benchmarks/       # Benchmark tasks (Sudoku, Maze, ARC)
│   ├── training/         # Training loops and utilities
│   ├── evaluation/       # Evaluation metrics and tools
│   └── visualization/    # Visualization and analysis
├── configs/              # Configuration files
├── scripts/              # Training and evaluation scripts
├── tests/                # Unit tests
└── examples/             # Usage examples
```

## Benchmarks

### Sudoku-Extreme
- 1000 training examples
- Complex puzzles requiring backtracking
- 55% accuracy (vs 0% for CoT models)

### Maze-Hard (30x30)
- Optimal pathfinding in large mazes
- 74.5% accuracy (vs 0% for baselines)

### ARC-AGI Challenge
- 40.3% on ARC-AGI-1 (vs 34.5% o3-mini-high)
- 5.0% on ARC-AGI-2 (vs 3.0% for other models)

## Key Components

1. **Hierarchical Architecture**: Two-level recurrent modules operating at different timescales
2. **Hierarchical Convergence**: Prevents premature convergence through structured resets
3. **One-step Gradients**: Memory-efficient training without BPTT
4. **Deep Supervision**: Multiple forward passes with detached gradients
5. **Adaptive Computation**: Q-learning for dynamic thinking time

## Citation

```bibtex
@article{wang2025hierarchical,
  title={Hierarchical Reasoning Model},
  author={Wang, Guan and Li, Jin and Sun, Yuhao and others},
  journal={arXiv preprint arXiv:2506.21734v2},
  year={2025}
}
```