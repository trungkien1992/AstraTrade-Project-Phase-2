"""
Training script for HRM on Maze-Hard benchmark
"""

import os
import sys
import argparse
import torch
import wandb
from tqdm import tqdm
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from hrm.model import HierarchicalReasoningModel, HRMConfig
from hrm.training import HRMTrainer, TrainingConfig
from datasets.maze import create_maze_benchmark


def parse_args():
    parser = argparse.ArgumentParser(description="Train HRM on Maze-Hard")
    
    # Model configuration
    parser.add_argument("--hidden_size", type=int, default=512, help="Hidden size")
    parser.add_argument("--num_heads", type=int, default=8, help="Number of attention heads")
    parser.add_argument("--N", type=int, default=2, help="Number of high-level cycles")
    parser.add_argument("--T", type=int, default=4, help="Number of low-level timesteps per cycle")
    
    # Training configuration
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    parser.add_argument("--learning_rate", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--max_steps", type=int, default=15000, help="Maximum training steps")
    parser.add_argument("--warmup_steps", type=int, default=1500, help="Warmup steps")
    parser.add_argument("--eval_steps", type=int, default=500, help="Evaluation frequency")
    parser.add_argument("--save_steps", type=int, default=1000, help="Save frequency")
    
    # ACT configuration
    parser.add_argument("--use_act", action="store_true", help="Use Adaptive Computation Time")
    parser.add_argument("--max_segments", type=int, default=8, help="Maximum ACT segments")
    
    # Dataset configuration
    parser.add_argument("--num_train_samples", type=int, default=1000, help="Number of training samples")
    
    # Output configuration
    parser.add_argument("--output_dir", type=str, default="./outputs/maze", help="Output directory")
    parser.add_argument("--cache_dir", type=str, default="./cache", help="Cache directory")
    parser.add_argument("--use_wandb", action="store_true", help="Use Weights & Biases logging")
    parser.add_argument("--project_name", type=str, default="hrm-maze", help="W&B project name")
    
    # Device configuration
    parser.add_argument("--device", type=str, default="auto", help="Device (cuda/cpu/auto)")
    parser.add_argument("--use_amp", action="store_true", help="Use automatic mixed precision")
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Device configuration
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device
    
    print(f"Using device: {device}")
    
    # Initialize wandb if requested
    if args.use_wandb:
        wandb.init(
            project=args.project_name,
            config=vars(args),
            name=f"hrm-maze-N{args.N}-T{args.T}-{'act' if args.use_act else 'ds'}"
        )
    
    # Model configuration
    model_config = HRMConfig(
        hidden_size=args.hidden_size,
        num_attention_heads=args.num_heads,
        intermediate_size=args.hidden_size * 4,
        vocab_size=6,  # Maze vocab size
        max_position_embeddings=1000,  # Larger for maze sequences
        N=args.N,
        T=args.T,
        mmax=args.max_segments,
        use_stablemax=True,
    )
    
    # Training configuration
    training_config = TrainingConfig(
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        max_steps=args.max_steps,
        warmup_steps=args.warmup_steps,
        eval_steps=args.eval_steps,
        save_steps=args.save_steps,
        max_segments=args.max_segments,
        device=device,
        use_amp=args.use_amp,
    )
    
    # Save configurations
    with open(os.path.join(args.output_dir, "model_config.json"), "w") as f:
        json.dump(model_config.__dict__, f, indent=2)
    
    with open(os.path.join(args.output_dir, "training_config.json"), "w") as f:
        config_dict = training_config.__dict__.copy()
        json.dump(config_dict, f, indent=2)
    
    # Create model
    print("Creating HRM model...")
    model = HierarchicalReasoningModel(model_config).to(device)
    
    print(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Create trainer
    trainer = HRMTrainer(
        model=model,
        config=training_config,
        use_act=args.use_act,
    )
    
    # Create datasets
    print("Creating Maze-Hard datasets...")
    from datasets.maze import create_maze_dataloader, MazeConfig
    
    maze_config = MazeConfig()
    
    train_loader = create_maze_dataloader(
        num_samples=args.num_train_samples,
        batch_size=args.batch_size,
        config=maze_config,
        cache_dir=args.cache_dir,
        split="train"
    )
    
    val_loader = create_maze_dataloader(
        num_samples=200,
        batch_size=args.batch_size,
        config=maze_config,
        cache_dir=args.cache_dir,
        split="val"
    )
    
    print(f"Training samples: {len(train_loader.dataset)}")
    print(f"Validation samples: {len(val_loader.dataset)}")
    
    # Training loop
    print("Starting training...")
    best_accuracy = 0.0
    step = 0
    
    model.train()
    
    while step < args.max_steps:
        epoch_losses = []
        
        for batch in tqdm(train_loader, desc=f"Step {step}"):
            if step >= args.max_steps:
                break
            
            # Training step
            metrics = trainer.train_step(batch)
            epoch_losses.append(metrics["loss"])
            
            # Logging
            if args.use_wandb:
                wandb.log(metrics, step=step)
            
            # Evaluation
            if (step + 1) % args.eval_steps == 0:
                print(f"\nEvaluating at step {step + 1}...")
                eval_metrics = trainer.evaluate(val_loader, max_eval_steps=50)
                
                print(f"Eval Loss: {eval_metrics['eval_loss']:.4f}")
                print(f"Eval Accuracy: {eval_metrics['eval_accuracy']:.4f}")
                print(f"Eval Perplexity: {eval_metrics['eval_perplexity']:.4f}")
                
                if args.use_wandb:
                    wandb.log(eval_metrics, step=step)
                
                # Save best model
                if eval_metrics['eval_accuracy'] > best_accuracy:
                    best_accuracy = eval_metrics['eval_accuracy']
                    best_path = os.path.join(args.output_dir, "best_model.pt")
                    trainer.save_checkpoint(best_path, step // len(train_loader), best_accuracy)
                    print(f"New best model saved with accuracy: {best_accuracy:.4f}")
                
                model.train()
            
            # Save checkpoint
            if (step + 1) % args.save_steps == 0:
                checkpoint_path = os.path.join(args.output_dir, f"checkpoint_step_{step + 1}.pt")
                trainer.save_checkpoint(checkpoint_path, step // len(train_loader))
                print(f"Checkpoint saved at step {step + 1}")
            
            step += 1
        
        # End of epoch logging
        avg_loss = sum(epoch_losses) / len(epoch_losses) if epoch_losses else 0.0
        print(f"Epoch average loss: {avg_loss:.4f}")
    
    # Final evaluation
    print("\nFinal evaluation...")
    
    # Load best model
    best_path = os.path.join(args.output_dir, "best_model.pt")
    if os.path.exists(best_path):
        trainer.load_checkpoint(best_path)
        print("Loaded best model for final evaluation")
    
    # Evaluate on test set
    test_loader = create_maze_dataloader(
        num_samples=200,
        batch_size=args.batch_size,
        config=maze_config,
        cache_dir=args.cache_dir,
        split="test"
    )
    
    final_eval_metrics = trainer.evaluate(test_loader)
    
    print(f"\nFinal Test Results:")
    print(f"Test Loss: {final_eval_metrics['eval_loss']:.4f}")
    print(f"Test Accuracy: {final_eval_metrics['eval_accuracy']:.4f}")
    print(f"Test Perplexity: {final_eval_metrics['eval_perplexity']:.4f}")
    
    if args.use_wandb:
        wandb.log({
            "final_test_loss": final_eval_metrics['eval_loss'],
            "final_test_accuracy": final_eval_metrics['eval_accuracy'],
            "final_test_perplexity": final_eval_metrics['eval_perplexity'],
        })
    
    # Save final model
    final_path = os.path.join(args.output_dir, "final_model.pt")
    trainer.save_checkpoint(final_path, step // len(train_loader), final_eval_metrics['eval_accuracy'])
    
    print(f"\nTraining completed! Best accuracy: {best_accuracy:.4f}")
    print(f"Models saved in: {args.output_dir}")
    
    if args.use_wandb:
        wandb.finish()


if __name__ == "__main__":
    main()