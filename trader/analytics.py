from collections.abc import Callable
from math import erf, sqrt
import numpy as np
import pandas as pd


def _norm_cdf(x: np.ndarray) -> np.ndarray:
    return np.vectorize(lambda v: 0.5 * (1 + erf(v / sqrt(2))))(x).astype(float)


def _add_bs_columns(df: pd.DataFrame, S: float, r: float, q: float, option_type: str) -> pd.DataFrame:
    if "implied_vol" in df.columns and "T_years" in df.columns:
        sigma = df["implied_vol"].to_numpy(dtype=float)
        T = df["T_years"].to_numpy(dtype=float)
        K = df["strike"].to_numpy(dtype=float)
        valid = (sigma > 0) & (T > 0) & np.isfinite(sigma) & np.isfinite(T)
        with np.errstate(invalid="ignore", divide="ignore"):
            d1 = np.where(valid, (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T)), np.nan)
            d2 = np.where(valid, d1 - sigma * np.sqrt(T), np.nan)
        if option_type == "call":
            df["prob_win"] = np.where(valid, _norm_cdf(-d2), np.nan)
            df["delta"] = np.where(valid, np.exp(-q * T) * _norm_cdf(d1), np.nan)
        else:
            df["prob_win"] = np.where(valid, _norm_cdf(d2), np.nan)
            df["delta"] = np.where(valid, -np.exp(-q * T) * _norm_cdf(-d1), np.nan)
    else:
        df["prob_win"] = np.nan
        df["delta"] = np.nan
    df["bid_ask_spread"] = df["ask"] - df["bid"]
    return df


def _compute_option_metrics(
    df: pd.DataFrame, S: float, r: float, q: float, option_type: str
) -> pd.DataFrame:
    df = df[df["option_type"] == option_type].copy()
    df["premium"] = (df["bid"] + df["ask"]) / 2
    df = df[df["premium"] > 0]
    df["dte"] = (pd.to_datetime(df["expiration"]) - pd.Timestamp.today()).dt.days

    if option_type == "call":
        df["pct_otm"] = (df["strike"] - S) / S * 100
        df["breakeven"] = S - df["premium"]
        df["annualized_yield"] = (df["premium"] / S) * (365 / df["dte"])
        df = df[df["strike"] >= S]
    else:
        df["pct_otm"] = (S - df["strike"]) / S * 100
        df["breakeven"] = df["strike"] - df["premium"]
        df["annualized_yield"] = (df["premium"] / df["strike"]) * (365 / df["dte"])
        df = df[df["strike"] <= S]

    return _add_bs_columns(df, S, r, q, option_type)


def compute_cc_metrics(df: pd.DataFrame, S: float, r: float = 0.0, q: float = 0.0) -> pd.DataFrame:
    """Covered call: yield is premium / spot price, OTM calls only (strike >= S)."""
    return _compute_option_metrics(df, S, r, q, "call")


def compute_csp_metrics(df: pd.DataFrame, S: float, r: float = 0.0, q: float = 0.0) -> pd.DataFrame:
    """Cash-secured put: yield is premium / strike (cash at risk), OTM puts only (strike <= S)."""
    return _compute_option_metrics(df, S, r, q, "put")


_STRATEGIES: dict[str, tuple[str, Callable]] = {
    "cc":  ("COVERED CALL",    compute_cc_metrics),
    "csp": ("CASH SECURED PUT", compute_csp_metrics),
}
