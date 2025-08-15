"""
Test suite for HRM training components
"""

import torch
import pytest
import numpy as np
import sys
import os
import tempfile

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from hrm.model import HierarchicalReasoningModel, HRMConfig
from hrm.training import HRMTrainer, TrainingConfig, DeepSupervision, AdaptiveComputationTime
from datasets.sudoku import create_sudoku_dataloader, SudokuConfig


class TestDeepSupervision:
    """Test Deep Supervision mechanism"""
    
    @pytest.fixture
    def model_and_config(self):
        """Create test model and training config"""
        model_config = HRMConfig(
            hidden_size=128,
            intermediate_size=512,
            num_attention_heads=4,
            vocab_size=100,
            N=2,
            T=2,
        )
        
        training_config = TrainingConfig(
            learning_rate=1e-4,
            batch_size=2,
            max_segments=4,
        )
        
        model = HierarchicalReasoningModel(model_config)
        return model, model_config, training_config
    
    def test_deep_supervision_init(self, model_and_config):
        """Test Deep Supervision initialization"""
        model, model_config, training_config = model_and_config
        
        deep_sup = DeepSupervision(model, training_config)
        
        assert deep_sup.model == model
        assert deep_sup.config == training_config
    
    def test_deep_supervision_forward(self, model_and_config):
        """Test Deep Supervision forward pass"""
        model, model_config, training_config = model_and_config
        
        deep_sup = DeepSupervision(model, training_config)
        
        # Create test data
        batch_size, seq_len = 2, 10
        input_ids = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        labels = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        
        # Test forward pass
        result = deep_sup(input_ids, labels)
        
        # Check output structure
        assert "total_loss" in result
        assert "segment_losses" in result
        assert "segment_outputs" in result
        assert "num_segments" in result
        
        # Check that loss is a tensor
        assert isinstance(result["total_loss"], torch.Tensor)
        assert result["total_loss"].requires_grad
        
        # Check segments
        assert isinstance(result["segment_losses"], list)
        assert len(result["segment_losses"]) == result["num_segments"]
        assert result["num_segments"] >= 1
        assert result["num_segments"] <= training_config.max_segments
    
    def test_deep_supervision_gradients(self, model_and_config):
        """Test that Deep Supervision produces gradients"""
        model, model_config, training_config = model_and_config
        
        deep_sup = DeepSupervision(model, training_config)
        
        # Clear gradients
        model.zero_grad()
        
        # Create test data
        batch_size, seq_len = 1, 5
        input_ids = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        labels = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        
        # Forward and backward
        result = deep_sup(input_ids, labels, max_segments=2)
        result["total_loss"].backward()
        
        # Check that some parameters have gradients
        has_gradients = any(p.grad is not None and p.grad.abs().sum() > 0 
                           for p in model.parameters() if p.requires_grad)
        assert has_gradients


class TestAdaptiveComputationTime:
    """Test Adaptive Computation Time mechanism"""
    
    @pytest.fixture
    def model_and_config(self):
        """Create test model and training config"""
        model_config = HRMConfig(
            hidden_size=128,
            intermediate_size=512,
            num_attention_heads=4,
            vocab_size=100,
            N=2,
            T=2,
        )
        
        training_config = TrainingConfig(
            learning_rate=1e-4,
            batch_size=2,
            max_segments=4,
            q_learning_lr=1e-3,
        )
        
        model = HierarchicalReasoningModel(model_config)
        return model, model_config, training_config
    
    def test_act_init(self, model_and_config):
        """Test ACT initialization"""
        model, model_config, training_config = model_and_config
        
        act = AdaptiveComputationTime(model, training_config)
        
        assert act.model == model
        assert act.config == training_config
    
    def test_act_forward(self, model_and_config):
        """Test ACT forward pass"""
        model, model_config, training_config = model_and_config
        
        act = AdaptiveComputationTime(model, training_config)
        
        # Create test data
        batch_size, seq_len = 2, 10
        input_ids = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        labels = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        
        # Test forward pass
        result = act(input_ids, labels)
        
        # Check output structure
        assert "total_loss" in result
        assert "seq2seq_loss" in result
        assert "q_loss" in result
        assert "num_segments" in result
        assert "halt_decisions" in result
        
        # Check losses
        assert isinstance(result["total_loss"], torch.Tensor)
        assert isinstance(result["seq2seq_loss"], torch.Tensor)
        assert isinstance(result["q_loss"], torch.Tensor)
        assert result["total_loss"].requires_grad
        
        # Check halt decisions
        assert isinstance(result["halt_decisions"], list)
        assert len(result["halt_decisions"]) == result["num_segments"]
    
    def test_act_q_learning(self, model_and_config):
        """Test Q-learning component of ACT"""
        model, model_config, training_config = model_and_config
        
        act = AdaptiveComputationTime(model, training_config)
        
        # Create test data
        batch_size, seq_len = 1, 5
        input_ids = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        labels = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        
        # Multiple forward passes to test Q-learning stability
        losses = []
        for _ in range(3):
            model.zero_grad()
            result = act(input_ids, labels)
            losses.append(result["q_loss"].item())
            result["total_loss"].backward()
        
        # Q-loss should be finite and reasonable
        assert all(np.isfinite(loss) for loss in losses)
        assert all(loss >= 0 for loss in losses)  # BCE loss should be non-negative


class TestHRMTrainer:
    """Test HRM Trainer class"""
    
    @pytest.fixture
    def trainer_setup(self):
        """Setup trainer for testing"""
        model_config = HRMConfig(
            hidden_size=128,
            intermediate_size=512,
            num_attention_heads=4,
            vocab_size=12,  # Sudoku vocab
            N=2,
            T=2,
        )
        
        training_config = TrainingConfig(
            learning_rate=1e-4,
            batch_size=2,
            max_segments=3,
            device="cpu",
            use_amp=False,  # Disable AMP for testing
        )
        
        model = HierarchicalReasoningModel(model_config)
        trainer = HRMTrainer(model, training_config, use_act=False)
        
        return trainer, model_config, training_config
    
    def test_trainer_init(self, trainer_setup):
        """Test trainer initialization"""
        trainer, model_config, training_config = trainer_setup
        
        assert isinstance(trainer, HRMTrainer)
        assert trainer.model is not None
        assert trainer.config == training_config
        assert trainer.optimizer is not None
        assert trainer.scheduler is not None
    
    def test_trainer_step(self, trainer_setup):
        """Test training step"""
        trainer, model_config, training_config = trainer_setup
        
        # Create test batch
        batch_size, seq_len = 2, 10
        batch = {
            "input_ids": torch.randint(0, model_config.vocab_size, (batch_size, seq_len)),
            "labels": torch.randint(0, model_config.vocab_size, (batch_size, seq_len)),
        }
        
        # Test training step
        metrics = trainer.train_step(batch)
        
        # Check metrics
        assert "loss" in metrics
        assert "lr" in metrics
        assert isinstance(metrics["loss"], float)
        assert isinstance(metrics["lr"], float)
        assert np.isfinite(metrics["loss"])
        assert metrics["lr"] > 0
    
    def test_trainer_evaluation(self, trainer_setup):
        """Test trainer evaluation"""
        trainer, model_config, training_config = trainer_setup
        
        # Create test dataloader
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_loader = create_sudoku_dataloader(
                num_samples=8,
                batch_size=2,
                config=SudokuConfig(),
                cache_dir=temp_dir,
                split="test"
            )
            
            # Test evaluation
            eval_metrics = trainer.evaluate(eval_loader, max_eval_steps=2)
            
            # Check evaluation metrics
            assert "eval_loss" in eval_metrics
            assert "eval_accuracy" in eval_metrics
            assert "eval_perplexity" in eval_metrics
            assert "eval_steps" in eval_metrics
            
            assert isinstance(eval_metrics["eval_loss"], float)
            assert isinstance(eval_metrics["eval_accuracy"], float)
            assert isinstance(eval_metrics["eval_perplexity"], float)
            assert eval_metrics["eval_steps"] > 0
    
    def test_trainer_checkpointing(self, trainer_setup):
        """Test model checkpointing"""
        trainer, model_config, training_config = trainer_setup
        
        with tempfile.TemporaryDirectory() as temp_dir:
            checkpoint_path = os.path.join(temp_dir, "test_checkpoint.pt")
            
            # Save checkpoint
            trainer.save_checkpoint(checkpoint_path, epoch=1, best_metric=0.5)
            
            assert os.path.exists(checkpoint_path)
            
            # Load checkpoint
            original_state = trainer.model.state_dict().copy()
            
            # Modify model slightly
            with torch.no_grad():
                for param in trainer.model.parameters():
                    param.add_(0.1)
            
            # Load checkpoint (should restore original state)
            trainer.load_checkpoint(checkpoint_path)
            
            # Check that state is restored
            loaded_state = trainer.model.state_dict()
            for key in original_state:
                assert torch.allclose(original_state[key], loaded_state[key])
    
    def test_trainer_with_act(self):
        """Test trainer with ACT enabled"""
        model_config = HRMConfig(
            hidden_size=128,
            num_attention_heads=4,
            vocab_size=12,
            N=2,
            T=2,
        )
        
        training_config = TrainingConfig(
            learning_rate=1e-4,
            batch_size=2,
            max_segments=3,
            device="cpu",
            use_amp=False,
        )
        
        model = HierarchicalReasoningModel(model_config)
        trainer = HRMTrainer(model, training_config, use_act=True)  # Enable ACT
        
        # Create test batch
        batch = {
            "input_ids": torch.randint(0, model_config.vocab_size, (2, 10)),
            "labels": torch.randint(0, model_config.vocab_size, (2, 10)),
        }
        
        # Test training step with ACT
        metrics = trainer.train_step(batch)
        
        # Should have additional ACT metrics
        assert "loss" in metrics
        assert "q_loss" in metrics
        assert "seq2seq_loss" in metrics
        assert "num_segments" in metrics


class TestTrainingIntegration:
    """Test integration of training components"""
    
    def test_end_to_end_training(self):
        """Test end-to-end training loop"""
        # Small model for fast testing
        model_config = HRMConfig(
            hidden_size=64,
            intermediate_size=256,
            num_attention_heads=2,
            vocab_size=12,
            N=1,
            T=2,
        )
        
        training_config = TrainingConfig(
            learning_rate=1e-3,
            batch_size=2,
            max_segments=2,
            device="cpu",
            use_amp=False,
        )
        
        model = HierarchicalReasoningModel(model_config)
        trainer = HRMTrainer(model, training_config, use_act=False)
        
        # Create small dataset
        with tempfile.TemporaryDirectory() as temp_dir:
            dataloader = create_sudoku_dataloader(
                num_samples=8,
                batch_size=2,
                config=SudokuConfig(),
                cache_dir=temp_dir,
                split="train"
            )
            
            # Run a few training steps
            initial_loss = None
            final_loss = None
            
            for step, batch in enumerate(dataloader):
                if step >= 3:  # Only run 3 steps
                    break
                
                metrics = trainer.train_step(batch)
                
                if initial_loss is None:
                    initial_loss = metrics["loss"]
                final_loss = metrics["loss"]
            
            # Training should produce finite losses
            assert np.isfinite(initial_loss)  
            assert np.isfinite(final_loss)
    
    def test_gradient_accumulation(self):
        """Test gradient accumulation"""
        model_config = HRMConfig(
            hidden_size=64,
            vocab_size=12,
            N=1,
            T=1,
        )
        
        training_config = TrainingConfig(
            learning_rate=1e-3,
            batch_size=2,
            gradient_accumulation_steps=2,  # Test accumulation
            device="cpu",
            use_amp=False,
        )
        
        model = HierarchicalReasoningModel(model_config)
        trainer = HRMTrainer(model, training_config, use_act=False)
        
        # Test that gradients accumulate properly
        batch = {
            "input_ids": torch.randint(0, model_config.vocab_size, (2, 5)),
            "labels": torch.randint(0, model_config.vocab_size, (2, 5)),
        }
        
        # First step should not update parameters
        initial_params = [p.clone() for p in model.parameters()]
        trainer.train_step(batch)
        
        # Parameters should be same (gradients accumulated, not applied)
        current_params = list(model.parameters())
        assert all(torch.equal(initial_params[i], current_params[i]) 
                  for i in range(len(initial_params)))
        
        # Second step should update parameters
        trainer.train_step(batch)
        
        # Now parameters should be different
        final_params = list(model.parameters())
        assert any(not torch.equal(initial_params[i], final_params[i]) 
                  for i in range(len(initial_params)))
    
    def test_memory_efficiency(self):
        """Test memory efficiency of training"""
        # Test with larger model to check memory usage
        model_config = HRMConfig(
            hidden_size=256,
            intermediate_size=1024,
            num_attention_heads=8,
            vocab_size=12,
            N=3,  # More cycles
            T=4,  # More timesteps
        )
        
        training_config = TrainingConfig(
            learning_rate=1e-4,
            batch_size=1,  # Small batch to fit in memory
            device="cpu",
            use_amp=False,
        )
        
        model = HierarchicalReasoningModel(model_config)
        trainer = HRMTrainer(model, training_config, use_act=False)
        
        # Test that training doesn't run out of memory
        batch = {
            "input_ids": torch.randint(0, model_config.vocab_size, (1, 50)),
            "labels": torch.randint(0, model_config.vocab_size, (1, 50)),
        }
        
        try:
            metrics = trainer.train_step(batch)
            success = True
        except RuntimeError as e:
            if "out of memory" in str(e):
                success = False
            else:
                raise e
        
        assert success, "Training should be memory efficient"


if __name__ == "__main__":
    pytest.main([__file__])