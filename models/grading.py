"""Grading service data models."""

from dataclasses import dataclass


@dataclass
class GradingTier:
    company: str = ""
    tier_name: str = ""
    cost_per_card: float = 0.0
    turnaround_days: int = 0
    max_declared_value: float = 0.0
