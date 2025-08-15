"""
Comprehensive evaluation script for HRM on all benchmarks
Reproduces the results from Figure 1 of the paper
"""

import os
import sys
import argparse
import torch
import json
import numpy as np
from typing import Dict, List, Any
from tqdm import tqdm

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from hrm.model import HierarchicalReasoningModel, HRMConfig
from hrm.training import HRMTrainer, TrainingConfig
from datasets.sudoku import create_sudoku_benchmark, SudokuGenerator
from datasets.maze import create_maze_benchmark, evaluate_path_correctness
from datasets.arc import create_arc_benchmark, evaluate_arc_prediction


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate HRM on all benchmarks")
    
    # Model paths
    parser.add_argument("--sudoku_model", type=str, help="Path to trained Sudoku model")
    parser.add_argument("--maze_model", type=str, help="Path to trained Maze model")
    parser.add_argument("--arc_model", type=str, help="Path to trained ARC model")
    
    # Data paths
    parser.add_argument("--arc_data_dir", type=str, default="./data/arc", help="ARC data directory")
    parser.add_argument("--cache_dir", type=str, default="./cache", help="Cache directory")
    
    # Evaluation settings
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size for evaluation")
    parser.add_argument("--max_eval_samples", type=int, default=200, help="Maximum samples to evaluate")
    parser.add_argument("--device", type=str, default="auto", help="Device (cuda/cpu/auto)")
    
    # Output
    parser.add_argument("--output_file", type=str, default="./evaluation_results.json", help="Output results file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    return parser.parse_args()


def load_model_and_config(model_path: str, device: str) -> tuple:
    """Load model and configuration from checkpoint"""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    checkpoint = torch.load(model_path, map_location=device)
    model_config = HRMConfig(**checkpoint["model_config"])
    
    model = HierarchicalReasoningModel(model_config).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    return model, model_config


def evaluate_sudoku(model_path: str, device: str, cache_dir: str, max_samples: int, verbose: bool) -> Dict[str, Any]:
    """Evaluate on Sudoku-Extreme benchmark"""
    print("Evaluating Sudoku-Extreme...")
    
    if not model_path or not os.path.exists(model_path):
        print(f"Sudoku model not found: {model_path}")
        return {"error": "Model not found"}
    
    # Load model
    model, config = load_model_and_config(model_path, device)
    
    # Create test dataset
    from datasets.sudoku import create_sudoku_dataloader, SudokuConfig
    
    sudoku_config = SudokuConfig()
    test_loader = create_sudoku_dataloader(
        num_samples=min(max_samples, 200),
        batch_size=8,
        config=sudoku_config,
        difficulty_range=(20, 50),  # Higher difficulty for test
        augment=False,
        cache_dir=cache_dir,
        split="test"
    )
    
    # Evaluation
    correct_predictions = 0
    total_predictions = 0
    losses = []
    
    with torch.no_grad():
        for batch in tqdm(test_loader, desc="Sudoku evaluation"):
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            attention_mask = batch.get("attention_mask", None)
            if attention_mask is not None:
                attention_mask = attention_mask.to(device)
            
            # Forward pass
            output = model(input_ids, attention_mask=attention_mask)
            logits = output["logits"]
            
            # Compute loss
            loss = torch.nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)),
                labels.view(-1),
                ignore_index=-100
            )
            losses.append(loss.item())
            
            # Compute accuracy (exact sequence match)
            predictions = torch.argmax(logits, dim=-1)
            
            # Check exact match for each sequence
            for i in range(predictions.size(0)):
                pred_seq = predictions[i]
                label_seq = labels[i]
                
                # Mask out padding tokens
                valid_mask = label_seq != -100
                if valid_mask.sum() > 0:
                    pred_valid = pred_seq[valid_mask]
                    label_valid = label_seq[valid_mask]
                    
                    if torch.equal(pred_valid, label_valid):
                        correct_predictions += 1
                    total_predictions += 1
    
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
    avg_loss = np.mean(losses) if losses else float('inf')
    
    results = {
        "accuracy": accuracy * 100,  # Convert to percentage
        "loss": avg_loss,
        "correct": correct_predictions,
        "total": total_predictions,
        "model_params": sum(p.numel() for p in model.parameters()),
    }
    
    if verbose:
        print(f"Sudoku Results:")
        print(f"  Accuracy: {results['accuracy']:.1f}%")
        print(f"  Loss: {results['loss']:.4f}")
        print(f"  Correct: {results['correct']}/{results['total']}")
    
    return results


def evaluate_maze(model_path: str, device: str, cache_dir: str, max_samples: int, verbose: bool) -> Dict[str, Any]:
    """Evaluate on Maze-Hard benchmark"""
    print("Evaluating Maze-Hard...")
    
    if not model_path or not os.path.exists(model_path):
        print(f"Maze model not found: {model_path}")
        return {"error": "Model not found"}
    
    # Load model
    model, config = load_model_and_config(model_path, device)
    
    # Create test dataset
    from datasets.maze import create_maze_dataloader, MazeConfig
    
    maze_config = MazeConfig()
    test_loader = create_maze_dataloader(
        num_samples=min(max_samples, 200),
        batch_size=8,
        config=maze_config,
        cache_dir=cache_dir,
        split="test"
    )
    
    # Evaluation
    correct_predictions = 0
    total_predictions = 0
    valid_paths = 0
    optimal_paths = 0
    losses = []
    
    with torch.no_grad():
        for batch in tqdm(test_loader, desc="Maze evaluation"):
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            attention_mask = batch.get("attention_mask", None)
            if attention_mask is not None:
                attention_mask = attention_mask.to(device)
            
            # Forward pass
            output = model(input_ids, attention_mask=attention_mask)
            logits = output["logits"]
            
            # Compute loss
            loss = torch.nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)),
                labels.view(-1),
                ignore_index=-100
            )
            losses.append(loss.item())
            
            # For maze evaluation, we need to decode paths and check validity
            predictions = torch.argmax(logits, dim=-1)
            
            # Simple accuracy based on token-level matching
            for i in range(predictions.size(0)):
                pred_seq = predictions[i]
                label_seq = labels[i]
                
                valid_mask = label_seq != -100
                if valid_mask.sum() > 0:
                    pred_valid = pred_seq[valid_mask]
                    label_valid = label_seq[valid_mask]
                    
                    # Exact sequence match
                    if torch.equal(pred_valid, label_valid):
                        correct_predictions += 1
                        optimal_paths += 1
                        valid_paths += 1
                    
                    total_predictions += 1
    
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
    avg_loss = np.mean(losses) if losses else float('inf')
    
    results = {
        "accuracy": accuracy * 100,  # Convert to percentage
        "loss": avg_loss,
        "correct": correct_predictions,
        "total": total_predictions,
        "valid_paths": valid_paths,
        "optimal_paths": optimal_paths,
        "model_params": sum(p.numel() for p in model.parameters()),
    }
    
    if verbose:
        print(f"Maze Results:")
        print(f"  Accuracy: {results['accuracy']:.1f}%")
        print(f"  Loss: {results['loss']:.4f}")
        print(f"  Correct: {results['correct']}/{results['total']}")
        print(f"  Valid paths: {results['valid_paths']}")
        print(f"  Optimal paths: {results['optimal_paths']}")
    
    return results


def evaluate_arc(model_path: str, device: str, arc_data_dir: str, max_samples: int, verbose: bool) -> Dict[str, Any]:
    """Evaluate on ARC-AGI benchmark"""
    print("Evaluating ARC-AGI...")
    
    if not model_path or not os.path.exists(model_path):
        print(f"ARC model not found: {model_path}")
        return {"error": "Model not found"}
    
    # Load model
    model, config = load_model_and_config(model_path, device)
    
    # Create test datasets
    try:
        dataloaders = create_arc_benchmark(arc_data_dir)
    except FileNotFoundError:
        print("ARC data not found")
        return {"error": "ARC data not found"}
    
    results = {}
    
    # Evaluate on both ARC-AGI-1 (eval) and ARC-AGI-2 (test) if available
    for split_name, test_loader in dataloaders.items():
        if split_name == "train":
            continue
        
        print(f"Evaluating ARC {split_name}...")
        
        correct_predictions = 0
        total_predictions = 0
        exact_matches = 0
        pixel_accuracies = []
        losses = []
        
        with torch.no_grad():
            eval_count = 0
            for batch in tqdm(test_loader, desc=f"ARC {split_name}"):
                if eval_count >= max_samples:
                    break
                
                input_ids = batch["input_ids"].to(device)
                labels = batch["labels"].to(device)
                attention_mask = batch.get("attention_mask", None)
                if attention_mask is not None:
                    attention_mask = attention_mask.to(device)
                
                # Forward pass
                output = model(input_ids, attention_mask=attention_mask)
                logits = output["logits"]
                
                # Compute loss
                loss = torch.nn.functional.cross_entropy(
                    logits.view(-1, logits.size(-1)),
                    labels.view(-1),
                    ignore_index=-100
                )
                losses.append(loss.item())
                
                # Compute accuracy
                predictions = torch.argmax(logits, dim=-1)
                
                for i in range(predictions.size(0)):
                    pred_seq = predictions[i]
                    label_seq = labels[i]
                    
                    valid_mask = label_seq != -100
                    if valid_mask.sum() > 0:
                        pred_valid = pred_seq[valid_mask]
                        label_valid = label_seq[valid_mask]
                        
                        # Exact sequence match
                        if torch.equal(pred_valid, label_valid):
                            correct_predictions += 1
                            exact_matches += 1
                        
                        # Pixel-level accuracy
                        pixel_acc = (pred_valid == label_valid).float().mean().item()
                        pixel_accuracies.append(pixel_acc)
                        
                        total_predictions += 1
                        eval_count += 1
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        avg_loss = np.mean(losses) if losses else float('inf')
        avg_pixel_acc = np.mean(pixel_accuracies) if pixel_accuracies else 0.0
        
        results[split_name] = {
            "accuracy": accuracy * 100,
            "pixel_accuracy": avg_pixel_acc * 100,
            "loss": avg_loss,
            "exact_matches": exact_matches,
            "total": total_predictions,
            "model_params": sum(p.numel() for p in model.parameters()),
        }
        
        if verbose:
            print(f"ARC {split_name} Results:")
            print(f"  Accuracy: {results[split_name]['accuracy']:.1f}%")
            print(f"  Pixel Accuracy: {results[split_name]['pixel_accuracy']:.1f}%")
            print(f"  Loss: {results[split_name]['loss']:.4f}")
            print(f"  Exact matches: {results[split_name]['exact_matches']}/{results[split_name]['total']}")
    
    return results


def main():
    args = parse_args()
    
    # Device configuration
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device
    
    print(f"Using device: {device}")
    
    # Evaluation results
    results = {
        "device": device,
        "evaluation_settings": {
            "max_eval_samples": args.max_eval_samples,
            "batch_size": args.batch_size,
        }
    }
    
    # Evaluate Sudoku
    if args.sudoku_model:
        try:
            results["sudoku"] = evaluate_sudoku(
                args.sudoku_model, device, args.cache_dir, 
                args.max_eval_samples, args.verbose
            )
        except Exception as e:
            print(f"Error evaluating Sudoku: {e}")
            results["sudoku"] = {"error": str(e)}
    
    # Evaluate Maze
    if args.maze_model:
        try:
            results["maze"] = evaluate_maze(
                args.maze_model, device, args.cache_dir,
                args.max_eval_samples, args.verbose
            )
        except Exception as e:
            print(f"Error evaluating Maze: {e}")
            results["maze"] = {"error": str(e)}
    
    # Evaluate ARC
    if args.arc_model:
        try:
            results["arc"] = evaluate_arc(
                args.arc_model, device, args.arc_data_dir,
                args.max_eval_samples, args.verbose
            )
        except Exception as e:
            print(f"Error evaluating ARC: {e}")
            results["arc"] = {"error": str(e)}
    
    # Summary
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print("="*50)
    
    if "sudoku" in results and "error" not in results["sudoku"]:
        print(f"Sudoku-Extreme: {results['sudoku']['accuracy']:.1f}% accuracy")
    
    if "maze" in results and "error" not in results["maze"]:
        print(f"Maze-Hard: {results['maze']['accuracy']:.1f}% accuracy")
    
    if "arc" in results and "error" not in results["arc"]:
        for split, res in results["arc"].items():
            if isinstance(res, dict) and "accuracy" in res:
                print(f"ARC-AGI {split}: {res['accuracy']:.1f}% accuracy")
    
    # Save results
    with open(args.output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {args.output_file}")


if __name__ == "__main__":
    main()