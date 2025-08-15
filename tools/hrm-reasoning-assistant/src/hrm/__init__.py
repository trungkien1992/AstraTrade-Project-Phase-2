"""
Hierarchical Reasoning Model (HRM)
Complete implementation of the paper by Wang et al., 2025
"""

from .model import HierarchicalReasoningModel, HRMConfig
from .components import RMSNorm, RotaryEmbedding, GLU, MultiHeadAttention
from .training import HRMTrainer, DeepSupervision, AdaptiveComputationTime

__version__ = "1.0.0"
__all__ = [
    "HierarchicalReasoningModel",
    "HRMConfig", 
    "HRMTrainer",
    "DeepSupervision",
    "AdaptiveComputationTime",
    "RMSNorm",
    "RotaryEmbedding", 
    "GLU",
    "MultiHeadAttention",
]