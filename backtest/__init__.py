"""
Backtesting utilities and strategy runners.

The intent is to keep backtests offline/reproducible:
- provide a price series (CSV or synthetic)
- choose a strategy runner (e.g., "wheel")
"""

from .registry import get_strategy_names, run_strategy

__all__ = ["get_strategy_names", "run_strategy"]

