"""
Core Hierarchical Reasoning Model (HRM) implementation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Tuple, Optional, Dict, Any, List
from dataclasses import dataclass

from .components import TransformerLayer, stablemax


@dataclass
class HRMConfig:
    """Configuration for the Hierarchical Reasoning Model"""
    # Model dimensions
    hidden_size: int = 512
    intermediate_size: int = 2048
    num_attention_heads: int = 8
    max_position_embeddings: int = 2048
    vocab_size: int = 32000
    
    # HRM specific parameters
    N: int = 2  # Number of high-level cycles
    T: int = 2  # Number of low-level timesteps per cycle
    
    # ACT parameters
    mmax: int = 8  # Maximum number of segments
    epsilon: float = 0.1  # Exploration probability for ACT
    
    # Training parameters
    dropout: float = 0.1
    layer_norm_eps: float = 1e-6
    use_cache: bool = False
    
    # Architecture details
    use_rotary_embedding: bool = True
    use_glu: bool = True
    use_rmsnorm: bool = True
    use_bias: bool = False
    use_stablemax: bool = False  # For small-sample experiments


class RecurrentModule(nn.Module):
    """Recurrent module using Transformer blocks"""
    def __init__(self, config: HRMConfig, num_layers: int = 1):
        super().__init__()
        self.config = config
        self.layers = nn.ModuleList([
            TransformerLayer(
                hidden_size=config.hidden_size,
                num_heads=config.num_attention_heads,
                intermediate_size=config.intermediate_size,
                use_glu=config.use_glu,
                use_rmsnorm=config.use_rmsnorm,
                use_bias=config.use_bias
            ) for _ in range(num_layers)
        ])
        
    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        for layer in self.layers:
            hidden_states = layer(hidden_states, attention_mask)
        return hidden_states


class HierarchicalReasoningModel(nn.Module):
    """
    Hierarchical Reasoning Model (HRM) implementation
    
    Features:
    - Two-level hierarchy with high-level (H) and low-level (L) modules
    - Hierarchical convergence mechanism
    - One-step gradient approximation
    - Deep supervision support
    - Adaptive Computation Time (ACT)
    """
    
    def __init__(self, config: HRMConfig):
        super().__init__()
        self.config = config
        
        # Input embedding layer
        self.input_embedding = nn.Embedding(config.vocab_size, config.hidden_size)
        
        # Low-level and high-level recurrent modules
        self.low_level_module = RecurrentModule(config)
        self.high_level_module = RecurrentModule(config)
        
        # Output head
        self.output_head = nn.Linear(config.hidden_size, config.vocab_size, bias=config.use_bias)
        
        # Q-head for ACT
        self.q_head = nn.Linear(config.hidden_size, 2, bias=config.use_bias)  # [halt, continue]
        
        # Initialize hidden states with truncated normal
        self.register_buffer("z_h_init", self._init_state(config.hidden_size))
        self.register_buffer("z_l_init", self._init_state(config.hidden_size))
        
        # Apply custom initialization
        self._init_weights()
    
    def _init_state(self, hidden_size: int) -> torch.Tensor:
        """Initialize state with truncated normal distribution (std=1, truncation=2)"""
        state = torch.randn(hidden_size)
        # Truncate to [-2, 2] range
        state = torch.clamp(state, min=-2.0, max=2.0)
        return state
    
    def _init_weights(self):
        """Initialize model weights using truncated LeCun Normal initialization"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                # Truncated LeCun Normal initialization
                std = math.sqrt(1.0 / module.in_features)
                nn.init.trunc_normal_(module.weight, mean=0.0, std=std, a=-2*std, b=2*std)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.trunc_normal_(module.weight, mean=0.0, std=0.02, a=-0.04, b=0.04)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        z_h: Optional[torch.Tensor] = None,
        z_l: Optional[torch.Tensor] = None,
        N: Optional[int] = None,
        T: Optional[int] = None,
        return_intermediate: bool = False,
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass of HRM with hierarchical convergence
        
        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            attention_mask: Attention mask [batch_size, seq_len]
            z_h: Initial high-level state [batch_size, seq_len, hidden_size]
            z_l: Initial low-level state [batch_size, seq_len, hidden_size]
            N: Number of high-level cycles (overrides config)
            T: Number of low-level timesteps per cycle (overrides config)
            return_intermediate: Whether to return intermediate states
        
        Returns:
            Dictionary containing:
            - logits: Output logits [batch_size, seq_len, vocab_size]
            - z_h: Final high-level state
            - z_l: Final low-level state
            - q_values: Q-values for ACT [batch_size, 2]
            - intermediate_states: List of intermediate states (if requested)
        """
        batch_size, seq_len = input_ids.shape
        N = N or self.config.N
        T = T or self.config.T
        
        # Input embedding
        x = self.input_embedding(input_ids)  # [batch_size, seq_len, hidden_size]
        
        # Initialize hidden states if not provided
        if z_h is None:
            z_h = self.z_h_init.unsqueeze(0).unsqueeze(0).expand(batch_size, seq_len, -1).clone()
        if z_l is None:
            z_l = self.z_l_init.unsqueeze(0).unsqueeze(0).expand(batch_size, seq_len, -1).clone()
        
        intermediate_states = [] if return_intermediate else None
        
        # HRM dynamics: N high-level cycles of T low-level timesteps each
        # This implements the hierarchical convergence mechanism
        for cycle in range(N):
            # Fix high-level state for this cycle (hierarchical convergence)
            z_h_cycle = z_h.clone()  # Fixed context for low-level updates
            
            # Low-level convergence phase
            for timestep in range(T):
                # Combine inputs for low-level module
                l_input = z_l + z_h_cycle + x  # Element-wise addition as per paper
                z_l = self.low_level_module(l_input, attention_mask)
                
                if return_intermediate:
                    intermediate_states.append({
                        'cycle': cycle,
                        'timestep': timestep,
                        'z_h': z_h.clone(),
                        'z_l': z_l.clone(),
                        'type': 'low_level'
                    })
            
            # High-level update at the end of the cycle
            h_input = z_h + z_l  # Element-wise addition
            z_h = self.high_level_module(h_input, attention_mask)
            
            if return_intermediate:
                intermediate_states.append({
                    'cycle': cycle,
                    'timestep': -1,  # Indicates high-level update
                    'z_h': z_h.clone(),
                    'z_l': z_l.clone(),
                    'type': 'high_level'
                })
        
        # Output prediction from high-level state
        if self.config.use_stablemax:
            logits = stablemax(self.output_head(z_h))
        else:
            logits = self.output_head(z_h)
        
        # Q-values for ACT (using mean pooling of high-level state)
        z_h_pooled = z_h.mean(dim=1)  # [batch_size, hidden_size]
        q_values = torch.sigmoid(self.q_head(z_h_pooled))  # [batch_size, 2]
        
        result = {
            "logits": logits,
            "z_h": z_h,
            "z_l": z_l,
            "q_values": q_values,
        }
        
        if return_intermediate:
            result["intermediate_states"] = intermediate_states
            
        return result
    
    def forward_with_gradient_approximation(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        z_h: Optional[torch.Tensor] = None,
        z_l: Optional[torch.Tensor] = None,
        N: Optional[int] = None,
        T: Optional[int] = None,
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass with one-step gradient approximation
        
        This method implements the gradient approximation described in the paper,
        where only the final states are included in the gradient computation.
        This provides O(1) memory complexity instead of O(T) for BPTT.
        
        The gradient path is: Output → final H-state → final L-state → input embedding
        """
        batch_size, seq_len = input_ids.shape
        N = N or self.config.N
        T = T or self.config.T
        
        # Input embedding
        x = self.input_embedding(input_ids)
        
        # Initialize hidden states
        if z_h is None:
            z_h = self.z_h_init.unsqueeze(0).unsqueeze(0).expand(batch_size, seq_len, -1).clone()
        if z_l is None:
            z_l = self.z_l_init.unsqueeze(0).unsqueeze(0).expand(batch_size, seq_len, -1).clone()
        
        # Run N*T - 1 steps without gradients (memory efficient)
        with torch.no_grad():
            for cycle in range(N):
                z_h_cycle = z_h
                
                for timestep in range(T):
                    # Skip the last low-level update to keep gradients
                    if cycle == N - 1 and timestep == T - 1:
                        break
                    
                    l_input = z_l + z_h_cycle + x
                    z_l = self.low_level_module(l_input, attention_mask)
                
                # Skip the last high-level update
                if cycle == N - 1:
                    break
                
                h_input = z_h + z_l
                z_h = self.high_level_module(h_input, attention_mask)
        
        # Final step with gradients (1-step approximation)
        # This is the only step that contributes to gradients
        l_input = z_l + z_h + x
        z_l = self.low_level_module(l_input, attention_mask)
        
        h_input = z_h + z_l
        z_h = self.high_level_module(h_input, attention_mask)
        
        # Output prediction
        if self.config.use_stablemax:
            logits = stablemax(self.output_head(z_h))
        else:
            logits = self.output_head(z_h)
            
        z_h_pooled = z_h.mean(dim=1)
        q_values = torch.sigmoid(self.q_head(z_h_pooled))
        
        return {
            "logits": logits,
            "z_h": z_h,
            "z_l": z_l,
            "q_values": q_values,
        }
    
    def compute_participation_ratio(self, hidden_states: torch.Tensor) -> float:
        """
        Compute participation ratio for brain correspondence analysis
        
        PR = (Σλᵢ)² / Σλᵢ²
        where λᵢ are eigenvalues of the covariance matrix
        """
        # Ensure we have enough samples and flatten if needed
        if hidden_states.dim() > 2:
            hidden_states = hidden_states.view(-1, hidden_states.size(-1))
        
        if hidden_states.size(0) < 2:
            return 0.0
        
        # Compute covariance matrix
        centered = hidden_states - hidden_states.mean(dim=0, keepdim=True)
        cov_matrix = torch.mm(centered.t(), centered) / (centered.size(0) - 1)
        
        # Compute eigenvalues
        try:
            eigenvalues = torch.linalg.eigvals(cov_matrix).real
            eigenvalues = eigenvalues[eigenvalues > 1e-10]  # Filter out near-zero eigenvalues
            
            if len(eigenvalues) == 0:
                return 0.0
            
            # Compute participation ratio
            sum_eig = eigenvalues.sum()
            sum_eig_sq = (eigenvalues ** 2).sum()
            
            if sum_eig_sq > 0:
                pr = (sum_eig ** 2) / sum_eig_sq
                return pr.item()
            else:
                return 0.0
        except:
            return 0.0
    
    def get_forward_residuals(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> List[float]:
        """
        Compute forward residuals to analyze convergence behavior
        Used for Figure 3 analysis in the paper
        """
        residuals = []
        batch_size, seq_len = input_ids.shape
        
        x = self.input_embedding(input_ids)
        z_h = self.z_h_init.unsqueeze(0).unsqueeze(0).expand(batch_size, seq_len, -1).clone()
        z_l = self.z_l_init.unsqueeze(0).unsqueeze(0).expand(batch_size, seq_len, -1).clone()
        
        prev_z_h = z_h.clone()
        prev_z_l = z_l.clone()
        
        for cycle in range(self.config.N):
            z_h_cycle = z_h.clone()
            
            for timestep in range(self.config.T):
                l_input = z_l + z_h_cycle + x
                z_l = self.low_level_module(l_input, attention_mask)
                
                # Compute residual for low-level module
                residual_l = torch.norm(z_l - prev_z_l).item()
                residuals.append(residual_l)
                prev_z_l = z_l.clone()
            
            h_input = z_h + z_l
            z_h = self.high_level_module(h_input, attention_mask)
            
            # Compute residual for high-level module
            residual_h = torch.norm(z_h - prev_z_h).item()
            residuals.append(residual_h)
            prev_z_h = z_h.clone()
        
        return residuals
    
    def generate_preliminary_output(self, input_ids: torch.Tensor, timestep: int, 
                                  z_h: torch.Tensor, z_l: torch.Tensor) -> torch.Tensor:
        """
        Generate preliminary output at any timestep for visualization
        Used for Figure 7 analysis showing intermediate reasoning steps
        """
        # Create a preliminary H-state update
        h_input = z_h + z_l
        z_h_prelim = self.high_level_module(h_input)
        
        # Generate output
        if self.config.use_stablemax:
            logits = stablemax(self.output_head(z_h_prelim))
        else:
            logits = self.output_head(z_h_prelim)
            
        return logits