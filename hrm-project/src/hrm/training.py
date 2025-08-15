"""
Training components for HRM including:
- Deep Supervision mechanism
- Adaptive Computation Time (ACT) with Q-learning
- HRM Trainer class
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Any
import random
import numpy as np
from dataclasses import dataclass

from .model import HierarchicalReasoningModel, HRMConfig


@dataclass
class TrainingConfig:
    """Configuration for HRM training"""
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    warmup_steps: int = 1000
    max_steps: int = 10000
    batch_size: int = 8
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    
    # Deep supervision settings
    max_segments: int = 8
    min_segments_prob: float = 0.1  # epsilon in paper
    
    # ACT settings
    q_learning_lr: float = 1e-3
    reward_correct: float = 1.0
    reward_continue: float = 0.0
    
    # Evaluation
    eval_steps: int = 500
    save_steps: int = 1000
    
    # Device and mixed precision
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    use_amp: bool = True


class DeepSupervision:
    """
    Deep Supervision mechanism as described in the paper
    
    Runs multiple forward passes (segments) with detached gradients between segments.
    Each segment provides supervision signal while maintaining 1-step gradient approximation.
    """
    
    def __init__(self, model: HierarchicalReasoningModel, config: TrainingConfig):
        self.model = model
        self.config = config
        
    def __call__(
        self,
        input_ids: torch.Tensor,
        labels: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        max_segments: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute deep supervision training
        
        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            labels: Target labels [batch_size, seq_len]
            attention_mask: Attention mask [batch_size, seq_len]
            max_segments: Maximum number of segments (overrides config)
            
        Returns:
            Dictionary containing:
            - total_loss: Combined loss from all segments
            - segment_losses: List of individual segment losses
            - segment_outputs: List of outputs from each segment
            - num_segments: Number of segments executed
        """
        max_segments = max_segments or self.config.max_segments
        
        # Determine minimum segments stochastically
        if random.random() < self.config.min_segments_prob:
            min_segments = random.randint(2, max_segments)
        else:
            min_segments = 1
            
        batch_size, seq_len = input_ids.shape
        device = input_ids.device
        
        # Initialize states
        z_h = None
        z_l = None
        
        segment_losses = []
        segment_outputs = []
        total_loss = 0.0
        
        for segment in range(max_segments):
            # Forward pass for this segment
            if segment == 0:
                # First segment - use initial states
                output = self.model.forward_with_gradient_approximation(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    z_h=z_h,
                    z_l=z_l
                )
            else:
                # Subsequent segments - use detached states from previous segment
                output = self.model.forward_with_gradient_approximation(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    z_h=z_h.detach() if z_h is not None else None,
                    z_l=z_l.detach() if z_l is not None else None
                )
            
            # Compute loss for this segment
            logits = output["logits"]
            segment_loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                labels.view(-1),
                ignore_index=-100
            )
            
            segment_losses.append(segment_loss)
            segment_outputs.append(output)
            total_loss += segment_loss
            
            # Update states for next segment (detached to prevent gradient flow)
            z_h = output["z_h"].detach()
            z_l = output["z_l"].detach()
            
            # Check if we should halt (minimum segments reached)
            if segment >= min_segments - 1:
                # Simple halting criterion - could be enhanced with ACT
                break
        
        return {
            "total_loss": total_loss / len(segment_losses),
            "segment_losses": segment_losses,
            "segment_outputs": segment_outputs,
            "num_segments": len(segment_losses),
        }


class AdaptiveComputationTime:
    """
    Adaptive Computation Time (ACT) with Q-learning
    
    Implements the "thinking, fast and slow" mechanism using Q-learning to
    determine optimal stopping time for each input.
    """
    
    def __init__(self, model: HierarchicalReasoningModel, config: TrainingConfig):
        self.model = model
        self.config = config
        
    def __call__(
        self,
        input_ids: torch.Tensor,
        labels: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Dict[str, Any]:
        """
        Execute ACT with Q-learning
        
        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            labels: Target labels [batch_size, seq_len]
            attention_mask: Attention mask [batch_size, seq_len]
            
        Returns:
            Dictionary containing:
            - total_loss: Combined sequence-to-sequence and Q-learning loss
            - seq2seq_loss: Sequence-to-sequence loss
            - q_loss: Q-learning loss
            - num_segments: Number of segments executed
            - halt_decisions: List of halt decisions for each segment
        """
        max_segments = self.config.max_segments
        batch_size, seq_len = input_ids.shape
        device = input_ids.device
        
        # Determine minimum segments stochastically (as in paper)
        if random.random() < self.config.min_segments_prob:
            min_segments = random.randint(2, max_segments)
        else:
            min_segments = 1
        
        # Initialize states and tracking
        z_h = None
        z_l = None
        segment_outputs = []
        q_targets = []
        halt_decisions = []
        
        for segment in range(max_segments):
            # Forward pass
            if segment == 0:
                output = self.model.forward_with_gradient_approximation(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    z_h=z_h,
                    z_l=z_l
                )
            else:
                output = self.model.forward_with_gradient_approximation(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    z_h=z_h.detach(),
                    z_l=z_l.detach()
                )
            
            segment_outputs.append(output)
            
            # Get Q-values for halt/continue decision
            q_values = output["q_values"]  # [batch_size, 2] - [halt, continue]
            q_halt, q_continue = q_values[:, 0], q_values[:, 1]
            
            # Determine halt decision
            should_halt = (segment >= min_segments - 1) and (q_halt > q_continue)
            halt_decisions.append(should_halt)
            
            # Update states
            z_h = output["z_h"]
            z_l = output["z_l"]
            
            # Break if halting or reached max segments
            if should_halt or segment >= max_segments - 1:
                break
        
        # Compute sequence-to-sequence loss (final segment)
        final_output = segment_outputs[-1]
        logits = final_output["logits"]
        seq2seq_loss = F.cross_entropy(
            logits.view(-1, logits.size(-1)),
            labels.view(-1),
            ignore_index=-100
        )
        
        # Compute Q-learning targets and loss
        q_loss = self._compute_q_loss(segment_outputs, labels, halt_decisions)
        
        # Combined loss
        total_loss = seq2seq_loss + q_loss
        
        return {
            "total_loss": total_loss,
            "seq2seq_loss": seq2seq_loss,
            "q_loss": q_loss,
            "num_segments": len(segment_outputs),
            "halt_decisions": halt_decisions,
        }
    
    def _compute_q_loss(
        self,
        segment_outputs: List[Dict[str, torch.Tensor]],
        labels: torch.Tensor,
        halt_decisions: List[bool],
    ) -> torch.Tensor:
        """Compute Q-learning loss based on segment outputs and decisions"""
        if len(segment_outputs) <= 1:
            return torch.tensor(0.0, device=labels.device)
        
        q_losses = []
        
        for i, output in enumerate(segment_outputs):
            q_values = output["q_values"]  # [batch_size, 2]
            logits = output["logits"]
            
            # Compute prediction correctness (simplified - token-level accuracy)
            predictions = torch.argmax(logits, dim=-1)
            correct = (predictions == labels).float().mean(dim=-1)  # [batch_size]
            
            # Compute Q-targets
            q_halt_target = correct * self.config.reward_correct
            
            if i < len(segment_outputs) - 1:
                # Not the final segment - can continue
                next_q_values = segment_outputs[i + 1]["q_values"]
                q_continue_target = torch.max(next_q_values, dim=-1)[0]
            else:
                # Final segment - cannot continue
                q_continue_target = torch.zeros_like(q_halt_target)
            
            # Q-learning loss (binary cross-entropy)
            q_targets = torch.stack([q_halt_target, q_continue_target], dim=-1)
            q_loss = F.binary_cross_entropy(q_values, q_targets)
            q_losses.append(q_loss)
        
        return torch.stack(q_losses).mean()


class HRMTrainer:
    """
    Main trainer class for HRM with deep supervision and ACT
    """
    
    def __init__(
        self,
        model: HierarchicalReasoningModel,
        config: TrainingConfig,
        use_act: bool = True,
    ):
        self.model = model
        self.config = config
        self.use_act = use_act
        
        # Initialize training components
        self.deep_supervision = DeepSupervision(model, config)
        self.act = AdaptiveComputationTime(model, config) if use_act else None
        
        # Initialize optimizer (Adam-atan2 as mentioned in paper)
        self.optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay,
            betas=(0.9, 0.999),
            eps=1e-8
        )
        
        # Learning rate scheduler with warmup
        self.scheduler = torch.optim.lr_scheduler.LambdaLR(
            self.optimizer,
            lr_lambda=self._get_lr_lambda
        )
        
        # Mixed precision scaler
        self.scaler = torch.cuda.amp.GradScaler() if config.use_amp else None
        
        # Training state
        self.step = 0
        self.epoch = 0
        
    def _get_lr_lambda(self, step: int) -> float:
        """Learning rate schedule with linear warmup"""
        if step < self.config.warmup_steps:
            return step / self.config.warmup_steps
        return 1.0
    
    def train_step(
        self,
        batch: Dict[str, torch.Tensor],
    ) -> Dict[str, float]:
        """
        Execute a single training step
        
        Args:
            batch: Dictionary containing 'input_ids', 'labels', and optionally 'attention_mask'
            
        Returns:
            Dictionary with loss components and metrics
        """
        self.model.train()
        
        input_ids = batch["input_ids"].to(self.config.device)
        labels = batch["labels"].to(self.config.device)
        attention_mask = batch.get("attention_mask", None)
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.config.device)
        
        # Forward pass with mixed precision
        with torch.cuda.amp.autocast(enabled=self.config.use_amp):
            if self.use_act and self.act is not None:
                # Use ACT for adaptive computation
                result = self.act(input_ids, labels, attention_mask)
                loss = result["total_loss"]
                metrics = {
                    "loss": loss.item(),
                    "seq2seq_loss": result["seq2seq_loss"].item(),
                    "q_loss": result["q_loss"].item(),
                    "num_segments": result["num_segments"],
                }
            else:
                # Use deep supervision without ACT
                result = self.deep_supervision(input_ids, labels, attention_mask)
                loss = result["total_loss"]
                metrics = {
                    "loss": loss.item(),
                    "num_segments": result["num_segments"],
                }
        
        # Backward pass
        if self.scaler is not None:
            self.scaler.scale(loss).backward()
            
            if (self.step + 1) % self.config.gradient_accumulation_steps == 0:
                # Gradient clipping
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.max_grad_norm
                )
                
                # Optimizer step
                self.scaler.step(self.optimizer)
                self.scaler.update()
                self.optimizer.zero_grad()
                self.scheduler.step()
        else:
            loss.backward()
            
            if (self.step + 1) % self.config.gradient_accumulation_steps == 0:
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.max_grad_norm
                )
                
                # Optimizer step
                self.optimizer.step()
                self.optimizer.zero_grad()
                self.scheduler.step()
        
        self.step += 1
        
        # Add learning rate to metrics
        metrics["lr"] = self.scheduler.get_last_lr()[0]
        
        return metrics
    
    def evaluate(
        self,
        eval_dataloader,
        max_eval_steps: Optional[int] = None,
    ) -> Dict[str, float]:
        """Evaluate the model on validation data"""
        self.model.eval()
        
        total_loss = 0.0
        total_steps = 0
        total_correct = 0
        total_tokens = 0
        
        with torch.no_grad():
            for step, batch in enumerate(eval_dataloader):
                if max_eval_steps and step >= max_eval_steps:
                    break
                
                input_ids = batch["input_ids"].to(self.config.device)
                labels = batch["labels"].to(self.config.device)
                attention_mask = batch.get("attention_mask", None)
                if attention_mask is not None:
                    attention_mask = attention_mask.to(self.config.device)
                
                # Forward pass
                with torch.cuda.amp.autocast(enabled=self.config.use_amp):
                    output = self.model(input_ids, attention_mask=attention_mask)
                    logits = output["logits"]
                    
                    # Compute loss
                    loss = F.cross_entropy(
                        logits.view(-1, logits.size(-1)),
                        labels.view(-1),
                        ignore_index=-100,
                        reduction='sum'
                    )
                    
                    # Compute accuracy
                    predictions = torch.argmax(logits, dim=-1)
                    mask = (labels != -100)
                    correct = ((predictions == labels) & mask).sum().item()
                    tokens = mask.sum().item()
                
                total_loss += loss.item()
                total_correct += correct
                total_tokens += tokens
                total_steps += 1
        
        avg_loss = total_loss / total_tokens if total_tokens > 0 else float('inf')
        accuracy = total_correct / total_tokens if total_tokens > 0 else 0.0
        perplexity = torch.exp(torch.tensor(avg_loss)).item()
        
        return {
            "eval_loss": avg_loss,
            "eval_accuracy": accuracy,
            "eval_perplexity": perplexity,
            "eval_steps": total_steps,
        }
    
    def save_checkpoint(self, save_path: str, epoch: int, best_metric: float = None):
        """Save model checkpoint"""
        checkpoint = {
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict(),
            "step": self.step,
            "epoch": epoch,
            "config": self.config,
            "model_config": self.model.config,
        }
        
        if best_metric is not None:
            checkpoint["best_metric"] = best_metric
            
        if self.scaler is not None:
            checkpoint["scaler_state_dict"] = self.scaler.state_dict()
        
        torch.save(checkpoint, save_path)
    
    def load_checkpoint(self, checkpoint_path: str):
        """Load model checkpoint"""
        checkpoint = torch.load(checkpoint_path, map_location=self.config.device)
        
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        
        self.step = checkpoint["step"]
        self.epoch = checkpoint["epoch"]
        
        if self.scaler is not None and "scaler_state_dict" in checkpoint:
            self.scaler.load_state_dict(checkpoint["scaler_state_dict"])