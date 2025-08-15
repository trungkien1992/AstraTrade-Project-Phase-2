# Makefile for HRM project

.PHONY: help install test lint format clean train-sudoku train-maze train-arc evaluate demo reproduce

help:  ## Show this help message
	@echo "🧠 Hierarchical Reasoning Model (HRM) - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Installation complete!"

test:  ## Run test suite
	@echo "🧪 Running tests..."
	pytest tests/ -v
	@echo "✅ Tests complete!"

test-quick:  ## Run quick tests only
	@echo "⚡ Running quick tests..."
	pytest tests/ -v -m "not slow"

lint:  ## Run code linting
	@echo "🔍 Running linter..."
	flake8 src/ scripts/ examples/ --max-line-length=100 --ignore=E203,W503
	@echo "✅ Linting complete!"

format:  ## Format code with black
	@echo "🎨 Formatting code..."
	black src/ scripts/ examples/ tests/ --line-length=100
	@echo "✅ Formatting complete!"

clean:  ## Clean cache and temporary files
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf cache/
	@echo "✅ Cleanup complete!"

# Training commands
train-sudoku:  ## Train HRM on Sudoku-Extreme
	@echo "🎯 Training HRM on Sudoku-Extreme..."
	python scripts/train_sudoku.py \
		--hidden_size 512 \
		--N 2 --T 4 \
		--use_act \
		--max_steps 10000 \
		--output_dir ./outputs/sudoku \
		--use_wandb

train-maze:  ## Train HRM on Maze-Hard
	@echo "🗺️  Training HRM on Maze-Hard..."
	python scripts/train_maze.py \
		--hidden_size 512 \
		--N 2 --T 4 \
		--use_act \
		--max_steps 15000 \
		--output_dir ./outputs/maze \
		--use_wandb

train-arc:  ## Train HRM on ARC-AGI
	@echo "🧩 Training HRM on ARC-AGI..."
	python scripts/train_arc.py \
		--hidden_size 512 \
		--N 2 --T 4 \
		--use_act \
		--max_steps 20000 \
		--output_dir ./outputs/arc \
		--download_data \
		--use_wandb

# Quick training for testing
train-quick:  ## Quick training run for testing
	@echo "⚡ Quick training run..."
	python scripts/train_sudoku.py \
		--hidden_size 256 \
		--N 1 --T 2 \
		--max_steps 100 \
		--num_train_samples 50 \
		--output_dir ./outputs/quick_test

# Evaluation commands
evaluate:  ## Evaluate trained models on all benchmarks
	@echo "📊 Evaluating all models..."
	python scripts/evaluate_all.py \
		--sudoku_model ./outputs/sudoku/best_model.pt \
		--maze_model ./outputs/maze/best_model.pt \
		--arc_model ./outputs/arc/best_model.pt \
		--output_file ./evaluation_results.json

demo-sudoku:  ## Run interactive Sudoku demo
	@echo "🎮 Running Sudoku demo..."
	python scripts/demo.py \
		--task sudoku \
		--model_path ./outputs/sudoku/best_model.pt \
		--show_intermediate \
		--num_examples 3

demo-maze:  ## Run interactive Maze demo
	@echo "🎮 Running Maze demo..."
	python scripts/demo.py \
		--task maze \
		--model_path ./outputs/maze/best_model.pt \
		--show_intermediate \
		--num_examples 3

# Analysis and reproduction
reproduce:  ## Reproduce paper results
	@echo "📄 Reproducing paper results..."
	python examples/paper_reproduction.py

quick-start:  ## Run quick start example
	@echo "🚀 Running quick start..."
	python examples/quick_start.py

# Data preparation
prepare-data:  ## Download and prepare datasets
	@echo "📥 Preparing datasets..."
	mkdir -p data/arc
	python -c "from src.datasets.arc import download_arc_data; download_arc_data('data/arc')"
	@echo "✅ Data preparation complete!"

# Development commands
dev-setup:  ## Set up development environment
	@echo "🔧 Setting up development environment..."
	pip install -r requirements.txt
	pip install -e .
	pre-commit install
	@echo "✅ Development setup complete!"

# Docker commands
docker-build:  ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t hrm:latest .

docker-run:  ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker run --rm -it --gpus all -v $(PWD):/workspace hrm:latest

# Benchmarking
benchmark:  ## Run comprehensive benchmarks
	@echo "🏁 Running benchmarks..."
	@echo "This will train and evaluate models on all tasks..."
	make train-sudoku
	make train-maze
	make evaluate
	@echo "✅ Benchmarking complete!"

# Paper reproduction pipeline
paper-pipeline:  ## Full paper reproduction pipeline
	@echo "📄 Running full paper reproduction pipeline..."
	make install
	make prepare-data
	make train-sudoku
	make train-maze
	make evaluate
	make reproduce
	@echo "🎉 Paper reproduction pipeline complete!"

# Monitoring and analysis
monitor:  ## Monitor training with tensorboard
	@echo "📈 Starting tensorboard..."
	tensorboard --logdir=./outputs --port=6006

analysis:  ## Run model analysis
	@echo "🔬 Running model analysis..."
	python -c "
from examples.paper_reproduction import reproduce_figure_8_analysis, reproduce_figure_3_analysis;
reproduce_figure_8_analysis();
reproduce_figure_3_analysis()
"

# Performance testing
perf-test:  ## Run performance tests
	@echo "⚡ Running performance tests..."
	python -c "
import time
import torch
from src.hrm.model import HierarchicalReasoningModel, HRMConfig

config = HRMConfig(hidden_size=512, N=2, T=4)
model = HierarchicalReasoningModel(config)
input_ids = torch.randint(0, 100, (8, 50))

# Standard forward
start = time.time()
for _ in range(10):
    output = model(input_ids)
std_time = time.time() - start

# Gradient approximation
start = time.time()
for _ in range(10):
    output = model.forward_with_gradient_approximation(input_ids)
approx_time = time.time() - start

print(f'Standard forward: {std_time:.3f}s')
print(f'Gradient approx: {approx_time:.3f}s')
print(f'Speedup: {std_time/approx_time:.2f}x')
"

# Documentation
docs:  ## Generate documentation
	@echo "📚 Generating documentation..."
	@echo "Documentation available in README.md and examples/"

# All-in-one commands
setup-and-test:  ## Setup environment and run tests
	make install
	make test

full-demo:  ## Run complete demo pipeline
	make quick-start
	make reproduce

# Check system requirements
check-system:  ## Check system requirements
	@echo "🔍 Checking system requirements..."
	@python -c "
import torch
import sys
print(f'Python: {sys.version}')
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA device: {torch.cuda.get_device_name()}')
    print(f'CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
"

# Help for specific tasks
help-training:  ## Show training help
	@echo "🎯 Training Commands:"
	@echo "  make train-sudoku  - Train on Sudoku-Extreme (55% target accuracy)"
	@echo "  make train-maze    - Train on Maze-Hard (74.5% target accuracy)"
	@echo "  make train-arc     - Train on ARC-AGI (40.3% target accuracy)"
	@echo "  make train-quick   - Quick test training run"
	@echo ""
	@echo "🎛️  Training Options:"
	@echo "  Add --use_wandb for Weights & Biases logging"
	@echo "  Modify --hidden_size, --N, --T for different model sizes"
	@echo "  Use --use_act to enable Adaptive Computation Time"

help-evaluation:  ## Show evaluation help
	@echo "📊 Evaluation Commands:"
	@echo "  make evaluate     - Evaluate all trained models"
	@echo "  make demo-sudoku  - Interactive Sudoku demo"
	@echo "  make demo-maze    - Interactive Maze demo" 
	@echo "  make reproduce    - Reproduce paper figures"

# Version info
version:  ## Show version information
	@echo "🧠 Hierarchical Reasoning Model (HRM)"
	@echo "📄 Based on: Wang et al., 2025"
	@echo "🔗 Paper: arXiv:2506.21734v2"
	@echo "💻 Implementation: Complete standalone version"