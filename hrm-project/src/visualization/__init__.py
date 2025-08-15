"""
Visualization tools for HRM analysis
"""

from .analysis import (
    plot_forward_residuals,
    plot_convergence_comparison,
    visualize_intermediate_steps,
    plot_participation_ratio_analysis,
)

from .brain_analysis import (
    BrainCorrespondenceAnalyzer,
    plot_dimensionality_hierarchy,
    compare_with_mouse_cortex,
)

__all__ = [
    "plot_forward_residuals",
    "plot_convergence_comparison", 
    "visualize_intermediate_steps",
    "plot_participation_ratio_analysis",
    "BrainCorrespondenceAnalyzer",
    "plot_dimensionality_hierarchy",
    "compare_with_mouse_cortex",
]