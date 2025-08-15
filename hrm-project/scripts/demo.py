"""
Interactive demo script for HRM
Shows the model solving problems step by step
"""

import os
import sys
import argparse
import torch
import numpy as np
from typing import Dict, List, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from hrm.model import HierarchicalReasoningModel, HRMConfig
from datasets.sudoku import SudokuGenerator, SudokuConfig
from datasets.maze import MazeGenerator, MazeConfig


def parse_args():
    parser = argparse.ArgumentParser(description="Interactive HRM Demo")
    
    parser.add_argument("--task", type=str, choices=["sudoku", "maze"], required=True, help="Task to demonstrate")
    parser.add_argument("--model_path", type=str, required=True, help="Path to trained model")
    parser.add_argument("--device", type=str, default="auto", help="Device (cuda/cpu/auto)")
    parser.add_argument("--show_intermediate", action="store_true", help="Show intermediate reasoning steps")
    parser.add_argument("--num_examples", type=int, default=3, help="Number of examples to show")
    
    return parser.parse_args()


def load_model(model_path: str, device: str):
    """Load trained model"""
    checkpoint = torch.load(model_path, map_location=device)
    model_config = HRMConfig(**checkpoint["model_config"])
    
    model = HierarchicalReasoningModel(model_config).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    return model, model_config


def visualize_sudoku(grid: np.ndarray, title: str = "Sudoku"):
    """Visualize Sudoku grid"""
    print(f"\n{title}:")
    print("┌" + "─" * 25 + "┐")
    
    for i, row in enumerate(grid):
        if i % 3 == 0 and i > 0:
            print("├" + "─" * 8 + "┼" + "─" * 8 + "┼" + "─" * 8 + "┤")
        
        row_str = "│"
        for j, cell in enumerate(row):
            if j % 3 == 0 and j > 0:
                row_str += "│"
            
            if cell == 0:
                row_str += " . "
            else:
                row_str += f" {cell} "
        row_str += "│"
        print(row_str)
    
    print("└" + "─" * 25 + "┘")


def visualize_maze(maze: np.ndarray, path: List[tuple] = None, title: str = "Maze"):
    """Visualize maze with optional path"""
    print(f"\n{title}:")
    
    # Create visual representation
    visual = maze.copy()
    
    if path:
        for x, y in path:
            if 0 <= x < maze.shape[1] and 0 <= y < maze.shape[0]:
                if visual[y, x] != 0:  # Don't overwrite walls
                    visual[y, x] = 4  # Path token
    
    # Print maze
    symbols = {0: "█", 1: " ", 2: "S", 3: "G", 4: "·", 5: " "}
    
    for row in visual:
        print("".join(symbols.get(cell, "?") for cell in row))


def demo_sudoku(model, model_config, device, show_intermediate, num_examples):
    """Demonstrate Sudoku solving"""
    print("=" * 50)
    print("SUDOKU-EXTREME DEMONSTRATION")
    print("=" * 50)
    
    sudoku_config = SudokuConfig()
    generator = SudokuGenerator(sudoku_config)
    
    for example_idx in range(num_examples):
        print(f"\n{'='*20} Example {example_idx + 1} {'='*20}")
        
        # Generate a puzzle
        puzzle, solution, difficulty = generator.generate_puzzle_pair(target_difficulty=20)
        
        print(f"Difficulty: {difficulty} backtracks required")
        
        # Visualize input
        visualize_sudoku(puzzle, "Input Puzzle")
        visualize_sudoku(solution, "True Solution")
        
        # Convert to sequence format
        input_seq, target_seq = generator.grid_to_sequence(puzzle, solution)
        
        # Pad and convert to tensors
        max_len = sudoku_config.max_sequence_length
        input_seq_padded = input_seq + [generator.PAD_TOKEN] * (max_len - len(input_seq))
        input_tensor = torch.tensor([input_seq_padded], dtype=torch.long).to(device)
        
        # Model prediction
        with torch.no_grad():
            if show_intermediate:
                # Show intermediate steps
                output = model(input_tensor, return_intermediate=True)
                
                print("\nIntermediate Reasoning Steps:")
                intermediate_states = output.get("intermediate_states", [])
                
                for i, state in enumerate(intermediate_states[:10]):  # Show first 10 steps
                    if state["type"] == "high_level":
                        print(f"Step {i}: High-level update (Cycle {state['cycle']})")
                    else:
                        print(f"Step {i}: Low-level update (Cycle {state['cycle']}, Timestep {state['timestep']})")
                
                if len(intermediate_states) > 10:
                    print(f"... and {len(intermediate_states) - 10} more steps")
                
            else:
                output = model(input_tensor)
            
            # Get predictions
            logits = output["logits"]
            predictions = torch.argmax(logits, dim=-1)
            
            # Convert back to grid
            pred_seq = predictions[0].cpu().numpy()
            pred_grid = pred_seq[:81].reshape(9, 9)  # First 81 tokens are the solution
            
            # Replace padding tokens with 0
            pred_grid = np.where(pred_grid == generator.PAD_TOKEN, 0, pred_grid)
        
        # Visualize prediction
        visualize_sudoku(pred_grid, "Model Prediction")
        
        # Check correctness
        correct = np.array_equal(pred_grid, solution)
        print(f"\nResult: {'✓ CORRECT' if correct else '✗ INCORRECT'}")
        
        if not correct:
            errors = np.sum(pred_grid != solution)
            print(f"Errors: {errors}/81 cells")
        
        # Show Q-values if available
        if "q_values" in output:
            q_values = output["q_values"][0].cpu().numpy()
            print(f"Q-values: halt={q_values[0]:.3f}, continue={q_values[1]:.3f}")
        
        print("\n" + "-" * 50)


def demo_maze(model, model_config, device, show_intermediate, num_examples):
    """Demonstrate maze solving"""
    print("=" * 50)
    print("MAZE-HARD DEMONSTRATION")
    print("=" * 50)
    
    maze_config = MazeConfig()
    generator = MazeGenerator(maze_config)
    
    for example_idx in range(num_examples):
        print(f"\n{'='*20} Example {example_idx + 1} {'='*20}")
        
        # Generate a maze
        maze, path, difficulty = generator.create_maze_with_path()
        
        print(f"Path length: {difficulty} (minimum required: {maze_config.min_difficulty})")
        
        # Visualize input
        visualize_maze(maze, title="Input Maze")
        visualize_maze(maze, path, "True Solution")
        
        # Convert to sequence format
        input_seq, target_seq = generator.maze_to_sequence(maze, path)
        
        # Pad and convert to tensors
        max_len = maze_config.max_sequence_length
        input_seq_padded = input_seq + [generator.PAD_TOKEN] * (max_len - len(input_seq))
        input_tensor = torch.tensor([input_seq_padded], dtype=torch.long).to(device)
        
        # Model prediction
        with torch.no_grad():
            if show_intermediate:
                output = model(input_tensor, return_intermediate=True)
                
                print("\nIntermediate Reasoning Steps:")
                intermediate_states = output.get("intermediate_states", [])
                
                for i, state in enumerate(intermediate_states[:8]):  # Show first 8 steps
                    if state["type"] == "high_level":
                        print(f"Step {i}: High-level planning (Cycle {state['cycle']})")
                    else:
                        print(f"Step {i}: Low-level search (Cycle {state['cycle']}, Timestep {state['timestep']})")
            else:
                output = model(input_tensor)
            
            # Get predictions
            logits = output["logits"]
            predictions = torch.argmax(logits, dim=-1)
            
            # Convert back to path (simplified)
            pred_seq = predictions[0].cpu().numpy()
            
            # Extract path coordinates (pairs of numbers)
            pred_path = []
            for i in range(0, len(target_seq), 2):
                if i + 1 < len(pred_seq):
                    x, y = pred_seq[i], pred_seq[i + 1]
                    if x < maze_config.maze_size and y < maze_config.maze_size:
                        pred_path.append((x, y))
            
            # Limit path length to reasonable size
            pred_path = pred_path[:len(path) * 2]  # At most 2x the true path length
        
        # Visualize prediction
        if pred_path:
            visualize_maze(maze, pred_path, "Model Prediction")
        else:
            print("\nModel Prediction: No valid path found")
        
        # Check correctness (simplified)
        if pred_path:
            correct_start = len(pred_path) > 0 and pred_path[0] == path[0]
            correct_goal = len(pred_path) > 0 and pred_path[-1] == path[-1]
            optimal_length = len(pred_path) == len(path)
            
            print(f"\nResult Analysis:")
            print(f"  Correct start: {'✓' if correct_start else '✗'}")
            print(f"  Correct goal: {'✓' if correct_goal else '✗'}")
            print(f"  Optimal length: {'✓' if optimal_length else '✗'} ({len(pred_path)} vs {len(path)})")
            
            if correct_start and correct_goal and optimal_length:
                print("Result: ✓ CORRECT")
            else:
                print("Result: ✗ INCORRECT")
        else:
            print("Result: ✗ NO PATH FOUND")
        
        # Show Q-values if available
        if "q_values" in output:
            q_values = output["q_values"][0].cpu().numpy()
            print(f"Q-values: halt={q_values[0]:.3f}, continue={q_values[1]:.3f}")
        
        print("\n" + "-" * 50)


def main():
    args = parse_args()
    
    # Device configuration
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device
    
    print(f"Using device: {device}")
    
    # Load model
    print(f"Loading model from: {args.model_path}")
    try:
        model, model_config = load_model(args.model_path, device)
        print(f"Model loaded successfully! Parameters: {sum(p.numel() for p in model.parameters()):,}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # Run demonstration
    if args.task == "sudoku":
        demo_sudoku(model, model_config, device, args.show_intermediate, args.num_examples)
    elif args.task == "maze":
        demo_maze(model, model_config, device, args.show_intermediate, args.num_examples)
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()