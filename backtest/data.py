from __future__ import annotations

from typing import Optional

import pandas as pd


def try_load_prices_csv(path: str = "price.csv") -> Optional[pd.DataFrame]:
    """
    Load a simple price series CSV with columns ["date", "close"].
    Returns None if the file doesn't exist or doesn't match the expected schema.
    """
    try:
        df = pd.read_csv(path)
    except Exception:
        return None

    if df is None or df.empty:
        return None

    if not {"date", "close"}.issubset(set(df.columns)):
        return None

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.sort_values("date").dropna(subset=["date", "close"])
    if df.empty:
        return None

    return df[["date", "close"]].reset_index(drop=True)

