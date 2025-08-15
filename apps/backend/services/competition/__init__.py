"""
Competition Service Package

Manages daily trading tournaments with real-time scoring, leaderboards,
AI ghost traders, and WebSocket infrastructure for live updates.
"""

from .competition_service import CompetitionService

__all__ = ['CompetitionService']