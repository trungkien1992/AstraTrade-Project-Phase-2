"""
Core components for the Hierarchical Reasoning Model
Includes RMSNorm, RotaryEmbedding, GLU, and MultiHeadAttention
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Tuple, Optional


class RMSNorm(nn.Module):
    """Root Mean Square Layer Normalization"""
    def __init__(self, hidden_size: int, eps: float = 1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(torch.float32)
        variance = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        return self.weight * hidden_states.to(input_dtype)


class RotaryEmbedding(nn.Module):
    """Rotary Position Embedding (RoPE)"""
    def __init__(self, dim: int, max_position_embeddings: int = 2048, base: float = 10000):
        super().__init__()
        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        self.base = base
        
        inv_freq = 1.0 / (self.base ** (torch.arange(0, self.dim, 2).float() / self.dim))
        self.register_buffer("inv_freq", inv_freq, persistent=False)

    def forward(self, x: torch.Tensor, seq_len: int = None) -> Tuple[torch.Tensor, torch.Tensor]:
        if seq_len is None:
            seq_len = x.shape[-2]
        
        t = torch.arange(seq_len, device=x.device, dtype=self.inv_freq.dtype)
        freqs = torch.outer(t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        
        cos = emb.cos()
        sin = emb.sin()
        return cos.to(dtype=x.dtype), sin.to(dtype=x.dtype)


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    """Rotate half the hidden dims of the input."""
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)


def apply_rotary_pos_emb(q: torch.Tensor, k: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Apply rotary position embedding to query and key tensors."""
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed


class GLU(nn.Module):
    """Gated Linear Unit"""
    def __init__(self, hidden_size: int, intermediate_size: int, use_bias: bool = False):
        super().__init__()
        self.gate_proj = nn.Linear(hidden_size, intermediate_size, bias=use_bias)
        self.up_proj = nn.Linear(hidden_size, intermediate_size, bias=use_bias)
        self.down_proj = nn.Linear(intermediate_size, hidden_size, bias=use_bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        gate = self.gate_proj(x)
        up = self.up_proj(x)
        return self.down_proj(F.silu(gate) * up)


class MultiHeadAttention(nn.Module):
    """Multi-Head Attention with RoPE support"""
    def __init__(self, hidden_size: int, num_heads: int, use_rotary: bool = True, use_bias: bool = False):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads
        self.use_rotary = use_rotary
        
        if hidden_size % num_heads != 0:
            raise ValueError(f"hidden_size ({hidden_size}) must be divisible by num_heads ({num_heads})")
        
        self.q_proj = nn.Linear(hidden_size, hidden_size, bias=use_bias)
        self.k_proj = nn.Linear(hidden_size, hidden_size, bias=use_bias)
        self.v_proj = nn.Linear(hidden_size, hidden_size, bias=use_bias)
        self.o_proj = nn.Linear(hidden_size, hidden_size, bias=use_bias)
        
        if use_rotary:
            self.rotary_emb = RotaryEmbedding(self.head_dim)

    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch_size, seq_len, _ = hidden_states.shape
        
        query_states = self.q_proj(hidden_states)
        key_states = self.k_proj(hidden_states)
        value_states = self.v_proj(hidden_states)
        
        # Reshape for multi-head attention
        query_states = query_states.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Apply rotary embeddings if enabled
        if self.use_rotary:
            cos, sin = self.rotary_emb(value_states, seq_len)
            query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        
        # Compute attention scores
        attn_weights = torch.matmul(query_states, key_states.transpose(2, 3)) / math.sqrt(self.head_dim)
        
        if attention_mask is not None:
            attn_weights = attn_weights + attention_mask
        
        attn_weights = F.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query_states.dtype)
        attn_output = torch.matmul(attn_weights, value_states)
        
        # Reshape and project
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.reshape(batch_size, seq_len, self.hidden_size)
        attn_output = self.o_proj(attn_output)
        
        return attn_output


class TransformerLayer(nn.Module):
    """Transformer layer with modern enhancements"""
    def __init__(self, hidden_size: int, num_heads: int, intermediate_size: int, 
                 use_glu: bool = True, use_rmsnorm: bool = True, use_bias: bool = False):
        super().__init__()
        self.hidden_size = hidden_size
        
        self.self_attn = MultiHeadAttention(hidden_size, num_heads, use_bias=use_bias)
        
        if use_glu:
            self.mlp = GLU(hidden_size, intermediate_size, use_bias)
        else:
            self.mlp = nn.Sequential(
                nn.Linear(hidden_size, intermediate_size, bias=use_bias),
                nn.SiLU(),
                nn.Linear(intermediate_size, hidden_size, bias=use_bias),
            )
        
        if use_rmsnorm:
            self.input_layernorm = RMSNorm(hidden_size)
            self.post_attention_layernorm = RMSNorm(hidden_size)
        else:
            self.input_layernorm = nn.LayerNorm(hidden_size)
            self.post_attention_layernorm = nn.LayerNorm(hidden_size)

    def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Self-attention with post-norm
        residual = hidden_states
        hidden_states = self.self_attn(hidden_states, attention_mask)
        hidden_states = self.input_layernorm(residual + hidden_states)
        
        # MLP with post-norm
        residual = hidden_states
        hidden_states = self.mlp(hidden_states)
        hidden_states = self.post_attention_layernorm(residual + hidden_states)
        
        return hidden_states


def stablemax(logits: torch.Tensor, dim: int = -1, temperature: float = 0.1) -> torch.Tensor:
    """
    Stable softmax implementation for improved generalization in small-sample settings
    """
    # Subtract max for numerical stability
    max_vals = torch.max(logits, dim=dim, keepdim=True)[0]
    logits_stable = logits - max_vals
    
    # Compute softmax with temperature scaling for stability
    exp_logits = torch.exp(logits_stable / temperature)
    sum_exp = torch.sum(exp_logits, dim=dim, keepdim=True)
    
    return exp_logits / sum_exp