from __future__ import annotations

from typing import Any, Callable, Dict

import pandas as pd

from .strategies.wheel import run_wheel


StrategyRunner = Callable[..., Dict[str, Any]]


_STRATEGIES: dict[str, StrategyRunner] = {
    "wheel": run_wheel,
}


def get_strategy_names() -> list[str]:
    return sorted(_STRATEGIES.keys())


def run_strategy(name: str, prices: pd.DataFrame, **kwargs: Any) -> Dict[str, Any]:
    try:
        runner = _STRATEGIES[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown strategy '{name}'. Available: {', '.join(get_strategy_names())}"
        ) from exc
    return runner(prices, **kwargs)
