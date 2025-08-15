"""
Test suite for HRM model components
"""

import torch
import pytest
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from hrm.model import HierarchicalReasoningModel, HRMConfig
from hrm.components import RMSNorm, RotaryEmbedding, GLU, MultiHeadAttention


class TestHRMComponents:
    """Test HRM component implementations"""
    
    def test_rmsnorm(self):
        """Test RMSNorm implementation"""
        batch_size, seq_len, hidden_size = 2, 10, 512
        norm = RMSNorm(hidden_size)
        
        x = torch.randn(batch_size, seq_len, hidden_size)
        output = norm(x)
        
        assert output.shape == x.shape
        
        # Check normalization properties
        output_flat = output.view(-1, hidden_size)
        variance = output_flat.pow(2).mean(-1)
        
        # Should be approximately 1 (within tolerance)
        assert torch.allclose(variance, torch.ones_like(variance), atol=1e-2)
    
    def test_rotary_embedding(self):
        """Test Rotary Position Embedding"""
        dim = 64
        seq_len = 20
        rope = RotaryEmbedding(dim)
        
        x = torch.randn(2, seq_len, dim)
        cos, sin = rope(x, seq_len)
        
        assert cos.shape == (seq_len, dim)
        assert sin.shape == (seq_len, dim)
        
        # Check that cos^2 + sin^2 = 1 for each position
        cos_sin_sum = cos.pow(2) + sin.pow(2)
        expected = torch.ones_like(cos_sin_sum)
        assert torch.allclose(cos_sin_sum, expected, atol=1e-6)
    
    def test_glu(self):
        """Test Gated Linear Unit"""
        hidden_size = 512
        intermediate_size = 2048
        glu = GLU(hidden_size, intermediate_size)
        
        batch_size, seq_len = 2, 10
        x = torch.randn(batch_size, seq_len, hidden_size)
        output = glu(x)
        
        assert output.shape == x.shape
    
    def test_multihead_attention(self):
        """Test Multi-Head Attention"""
        hidden_size = 512
        num_heads = 8
        attention = MultiHeadAttention(hidden_size, num_heads)
        
        batch_size, seq_len = 2, 10
        x = torch.randn(batch_size, seq_len, hidden_size)
        output = attention(x)
        
        assert output.shape == x.shape


class TestHRMModel:
    """Test HRM model functionality"""
    
    @pytest.fixture
    def model_config(self):
        """Create test model configuration"""
        return HRMConfig(
            hidden_size=256,
            intermediate_size=1024,
            num_attention_heads=4,
            vocab_size=1000,
            N=2,
            T=3,
            max_position_embeddings=100,
        )
    
    @pytest.fixture
    def model(self, model_config):
        """Create test model"""
        return HierarchicalReasoningModel(model_config)
    
    def test_model_initialization(self, model, model_config):
        """Test model initialization"""
        assert isinstance(model, HierarchicalReasoningModel)
        assert model.config == model_config
        
        # Check parameter count
        param_count = sum(p.numel() for p in model.parameters())
        assert param_count > 0
        
        # Check that initial states are initialized
        assert model.z_h_init.shape == (model_config.hidden_size,)
        assert model.z_l_init.shape == (model_config.hidden_size,)
    
    def test_forward_pass(self, model, model_config):
        """Test basic forward pass"""
        batch_size, seq_len = 2, 20
        input_ids = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        
        output = model(input_ids)
        
        # Check output shapes
        assert "logits" in output
        assert "z_h" in output
        assert "z_l" in output
        assert "q_values" in output
        
        assert output["logits"].shape == (batch_size, seq_len, model_config.vocab_size)
        assert output["z_h"].shape == (batch_size, seq_len, model_config.hidden_size)
        assert output["z_l"].shape == (batch_size, seq_len, model_config.hidden_size)
        assert output["q_values"].shape == (batch_size, 2)
    
    def test_forward_with_attention_mask(self, model, model_config):
        """Test forward pass with attention mask"""
        batch_size, seq_len = 2, 20
        input_ids = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        attention_mask = torch.ones(batch_size, seq_len)
        attention_mask[0, 10:] = 0  # Mask second half of first sequence
        
        output = model(input_ids, attention_mask=attention_mask)
        
        assert output["logits"].shape == (batch_size, seq_len, model_config.vocab_size)
    
    def test_hierarchical_convergence(self, model, model_config):
        """Test hierarchical convergence mechanism"""
        batch_size, seq_len = 1, 10
        input_ids = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        
        # Test with different N and T values
        output1 = model(input_ids, N=1, T=2)
        output2 = model(input_ids, N=2, T=2)
        output3 = model(input_ids, N=2, T=4)
        
        # Outputs should be different with different N and T
        assert not torch.allclose(output1["logits"], output2["logits"])
        assert not torch.allclose(output2["logits"], output3["logits"])
    
    def test_gradient_approximation(self, model, model_config):
        """Test one-step gradient approximation"""
        batch_size, seq_len = 2, 10
        input_ids = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        
        # Test gradient approximation method
        output = model.forward_with_gradient_approximation(input_ids)
        
        assert "logits" in output
        assert output["logits"].shape == (batch_size, seq_len, model_config.vocab_size)
        
        # Check that gradients can flow
        loss = output["logits"].sum()
        loss.backward()
        
        # Check that some parameters have gradients
        has_gradients = any(p.grad is not None and p.grad.abs().sum() > 0 
                           for p in model.parameters())
        assert has_gradients
    
    def test_intermediate_steps(self, model, model_config):
        """Test intermediate step visualization"""
        batch_size, seq_len = 1, 10
        input_ids = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        
        output = model(input_ids, return_intermediate=True)
        
        assert "intermediate_states" in output
        intermediate_states = output["intermediate_states"]
        
        # Should have N*T + N intermediate states (low-level + high-level updates)
        expected_states = model_config.N * model_config.T + model_config.N
        assert len(intermediate_states) == expected_states
        
        # Check state structure
        for state in intermediate_states:
            assert "cycle" in state
            assert "timestep" in state
            assert "z_h" in state
            assert "z_l" in state
            assert "type" in state
            assert state["type"] in ["low_level", "high_level"]
    
    def test_participation_ratio(self, model):
        """Test participation ratio computation"""
        # Test with random hidden states
        batch_size, seq_len, hidden_size = 10, 20, 256
        hidden_states = torch.randn(batch_size, seq_len, hidden_size)
        
        pr = model.compute_participation_ratio(hidden_states)
        
        assert isinstance(pr, float)
        assert pr >= 0
        assert pr <= hidden_size  # PR should be bounded by dimensionality
    
    def test_forward_residuals(self, model, model_config):
        """Test forward residual computation"""
        batch_size, seq_len = 1, 10
        input_ids = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        
        residuals = model.get_forward_residuals(input_ids)
        
        assert isinstance(residuals, list)
        assert len(residuals) > 0
        assert all(isinstance(r, float) for r in residuals)
        assert all(r >= 0 for r in residuals)  # Residuals should be non-negative
    
    def test_preliminary_output(self, model, model_config):
        """Test preliminary output generation"""
        batch_size, seq_len = 1, 10
        input_ids = torch.randint(0, model_config.vocab_size, (batch_size, seq_len))
        
        # Create dummy states
        z_h = torch.randn(batch_size, seq_len, model_config.hidden_size)
        z_l = torch.randn(batch_size, seq_len, model_config.hidden_size)
        
        prelim_output = model.generate_preliminary_output(input_ids, 0, z_h, z_l)
        
        assert prelim_output.shape == (batch_size, seq_len, model_config.vocab_size)


class TestHRMTraining:
    """Test HRM training components"""
    
    def test_model_gradient_flow(self):
        """Test that gradients flow properly through the model"""
        config = HRMConfig(
            hidden_size=128,
            intermediate_size=512,
            num_attention_heads=4,
            vocab_size=100,
            N=2,
            T=2,
        )
        model = HierarchicalReasoningModel(config)
        
        batch_size, seq_len = 2, 10
        input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len))
        labels = torch.randint(0, config.vocab_size, (batch_size, seq_len))
        
        # Forward pass
        output = model(input_ids)
        logits = output["logits"]
        
        # Compute loss
        loss = torch.nn.functional.cross_entropy(
            logits.view(-1, logits.size(-1)),
            labels.view(-1)
        )
        
        # Backward pass
        loss.backward()
        
        # Check that gradients exist
        for name, param in model.named_parameters():
            if param.requires_grad:
                assert param.grad is not None, f"No gradient for {name}"
                assert param.grad.abs().sum() > 0, f"Zero gradient for {name}"
    
    def test_memory_efficiency(self):
        """Test memory efficiency of gradient approximation"""
        config = HRMConfig(
            hidden_size=256,
            intermediate_size=1024,
            num_attention_heads=8,
            vocab_size=1000,
            N=4,  # Larger N to test memory
            T=8,  # Larger T to test memory
        )
        model = HierarchicalReasoningModel(config)
        
        batch_size, seq_len = 1, 50  # Longer sequence
        input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len))
        
        # Test that gradient approximation doesn't run out of memory
        try:
            output = model.forward_with_gradient_approximation(input_ids)
            loss = output["logits"].sum()
            loss.backward()
            success = True
        except RuntimeError as e:
            if "out of memory" in str(e):
                success = False
            else:
                raise e
        
        assert success, "Gradient approximation should be memory efficient"


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_input(self):
        """Test handling of empty input"""
        config = HRMConfig(
            hidden_size=128,
            vocab_size=100,
        )
        model = HierarchicalReasoningModel(config)
        
        # Test with minimal input
        input_ids = torch.randint(0, config.vocab_size, (1, 1))
        output = model(input_ids)
        
        assert output["logits"].shape == (1, 1, config.vocab_size)
    
    def test_different_batch_sizes(self):
        """Test with different batch sizes"""
        config = HRMConfig(
            hidden_size=128,
            vocab_size=100,
        )
        model = HierarchicalReasoningModel(config)
        
        seq_len = 10
        
        for batch_size in [1, 2, 4, 8]:
            input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len))
            output = model(input_ids)
            
            assert output["logits"].shape == (batch_size, seq_len, config.vocab_size)
            assert output["q_values"].shape == (batch_size, 2)
    
    def test_device_consistency(self):
        """Test device consistency"""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
        
        config = HRMConfig(
            hidden_size=128,
            vocab_size=100,
        )
        model = HierarchicalReasoningModel(config).cuda()
        
        batch_size, seq_len = 2, 10
        input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_len)).cuda()
        
        output = model(input_ids)
        
        # Check that all outputs are on CUDA
        assert output["logits"].is_cuda
        assert output["z_h"].is_cuda
        assert output["z_l"].is_cuda
        assert output["q_values"].is_cuda


if __name__ == "__main__":
    pytest.main([__file__])