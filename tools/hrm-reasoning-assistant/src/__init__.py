"""
HRM Reasoning Assistant for Claude Code Enhancement

This package provides hierarchical reasoning capabilities to enhance Claude Code's
problem-solving abilities for complex AstraTrade development tasks.
"""

__version__ = "1.0.0"
__author__ = "AstraTrade Development Team"

from .reasoning import CodeAnalyzer, ArchitectureAdvisor, DebugAssistant, PerformanceOptimizer
from .hrm import HierarchicalReasoningModel, HRMConfig

__all__ = [
    "CodeAnalyzer",
    "ArchitectureAdvisor", 
    "DebugAssistant",
    "PerformanceOptimizer",
    "HierarchicalReasoningModel",
    "HRMConfig"
]