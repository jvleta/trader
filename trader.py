from datetime import date, timedelta
from math import erf, sqrt
import numpy as np
import pandas as pd
from openbb import obb

_COLUMN_LABELS = {
    "expiration": "Expiration",
    "strike": "Strike",
    "premium": "Premium",
    "dte": "DTE",
    "pct_otm": "% OTM",
    "breakeven": "Breakeven",
    "annualized_yield": "Ann. Yield",
    "prob_win": "P(Win)",
    "delta": "Delta",
    "bid_ask_spread": "Spread",
}

_FORMATTERS = {
    "Strike":     lambda v: f"${v:,.2f}",
    "Premium":    lambda v: f"${v:,.2f}",
    "DTE":        lambda v: f"{int(v)}",
    "% OTM":      lambda v: f"{v:.2f}%",
    "Breakeven":  lambda v: f"${v:,.2f}",
    "Ann. Yield": lambda v: f"{v * 100:.2f}%",
    "P(Win)":     lambda v: f"{v * 100:.1f}%" if pd.notna(v) else "N/A",
    "Delta":      lambda v: f"{v:.3f}" if pd.notna(v) else "N/A",
    "Spread":     lambda v: f"${v:,.2f}",
}


def parse_dividend_amounts(dividends) -> list[float]:
    if dividends is None:
        return []

    if isinstance(dividends, dict):
        if "data" in dividends:
            dividends = dividends["data"]
        elif "results" in dividends:
            dividends = dividends["results"]

    if hasattr(dividends, "to_dict"):
        try:
            dividends = dividends.to_dict(orient="records")
        except Exception:
            dividends = dividends.to_dict()

    if not isinstance(dividends, (list, tuple)):
        dividends = [dividends]

    amounts: list[float] = []
    keys = ("amount", "cash_amount", "dividend", "value")
    for entry in dividends:
        if entry is None:
            continue
        for key in keys:
            candidate = (
                entry.get(key) if isinstance(entry, dict) else getattr(entry, key, None)
            )
            if candidate is None:
                continue
            try:
                value = float(candidate)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Non-numeric dividend amount for key '{key}': {candidate!r} in entry {entry!r}"
                ) from exc
            if np.isfinite(value):
                amounts.append(value)
                break
    return amounts


def get_spot_price(symbol: str) -> float:
    try:
        response = obb.equity.price.quote(symbol=symbol)
        prices = getattr(response, "data", None) or getattr(response, "results", None)
        latest = prices[-1] if isinstance(prices, (list, tuple)) else prices
        for field in ("close", "price", "last_price", "last", "regular_market_price"):
            value = getattr(latest, field, None)
            if value is not None and np.isfinite(value):
                return float(value)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to retrieve spot price for symbol: {symbol}"
        ) from exc
    raise RuntimeError(f"Invalid price data for symbol: {symbol}")


def get_dividend_yield(symbol: str, price: float | None = None) -> float:
    try:
        start_date = date.today() - timedelta(days=365)
        response = obb.equity.fundamental.dividends(
            symbol=symbol, start_date=start_date, end_date=date.today()
        )
        dividends = getattr(response, "data", None) or getattr(
            response, "results", None
        )
        amounts = parse_dividend_amounts(dividends)
        if not amounts:
            raise ValueError("No valid dividend amounts found")

        total_dividends = sum(amounts)
        if price is None:
            price = get_spot_price(symbol)
        return total_dividends / price if price else 0.0
    except Exception as exc:
        raise RuntimeError(
            f"Failed to retrieve dividend yield for symbol: {symbol}"
        ) from exc


def get_risk_free_rate() -> float:
    try:
        start_date = date.today() - timedelta(days=10)
        response = obb.fixedincome.government.treasury_rates(
            start_date=start_date, end_date=date.today()
        )
        rates = getattr(response, "data", None) or getattr(response, "results", None)
        records = rates if isinstance(rates, (list, tuple)) else [rates]
        for entry in reversed(records):
            if entry is None:
                continue
            value = getattr(entry, "year_10", None)
            if value is None and isinstance(entry, dict):
                value = (
                    entry.get("year_10") or entry.get("year10") or entry.get("ten_year")
                )
            if value is None:
                continue
            try:
                rate = float(value)
            except (TypeError, ValueError):
                continue
            if np.isfinite(rate):
                return rate if rate < 1 else rate / 100.0
    except Exception as exc:
        raise RuntimeError("Failed to retrieve risk-free rate") from exc
    raise RuntimeError("Invalid risk-free rate data")


def fetch_underlying_data(symbol: str) -> dict:
    S = get_spot_price(symbol)
    q = get_dividend_yield(symbol, price=S)
    r = get_risk_free_rate()
    return {"symbol": symbol, "spot_price": S, "dividend_yield": q, "risk_free_rate": r}


def fetch_option_chain(
    symbol: str, filter_expiries: list | None = None
) -> pd.DataFrame:
    """Fetch the option chain for the given underlying symbol using OpenBB."""
    filter_expiries = filter_expiries or []
    try:
        response = obb.derivatives.options.chains(symbol=symbol)
        df = response.to_dataframe(index=None)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to retrieve option chain for symbol: {symbol}"
        ) from exc

    if df is None or df.empty:
        return pd.DataFrame()

    df["symbol"] = symbol
    df["expiration"] = pd.to_datetime(df["expiration"]).dt.date

    if filter_expiries:
        allowed_expirations = {pd.to_datetime(exp).date() for exp in filter_expiries}
        df = df[df["expiration"].isin(allowed_expirations)]

    if df.empty:
        return pd.DataFrame()
    df = df.copy()

    if "dte" in df.columns:
        df.loc[:, "T_years"] = pd.to_numeric(df["dte"], errors="coerce") / 365.0
    else:
        today = date.today()
        df.loc[:, "T_years"] = df["expiration"].apply(
            lambda d: (d - today).days / 365.0
        )

    price_candidates = [
        col
        for col in (
            "last_trade_price",
            "close",
            "mark",
            "theoretical_price",
            "prev_close",
        )
        if col in df.columns
    ]
    if price_candidates:
        df.loc[:, "market_price"] = (
            df[price_candidates]
            .apply(pd.to_numeric, errors="coerce")
            .bfill(axis=1)
            .iloc[:, 0]
        )
    else:
        df["market_price"] = np.nan

    keep_cols = [
        "symbol",
        "option_type",
        "expiration",
        "strike",
        "market_price",
        "bid",
        "ask",
        "volume",
        "open_interest",
        "implied_volatility",
        "T_years",
    ]
    existing = [col for col in keep_cols if col in df.columns]
    result = df[existing].copy()
    if "implied_volatility" in result.columns:
        result.rename(columns={"implied_volatility": "implied_vol"}, inplace=True)

    return result.reset_index(drop=True)


def _norm_cdf(x: np.ndarray) -> np.ndarray:
    return np.vectorize(lambda v: 0.5 * (1 + erf(v / sqrt(2))))(x).astype(float)


def _add_bs_columns(df: pd.DataFrame, S: float, r: float, q: float, option_type: str) -> pd.DataFrame:
    """Append prob_win, delta, and bid_ask_spread using Black-Scholes d1/d2."""
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


def screen(symbol: str, strategy: str = "cc", top_n: int = 20):
    strategy = strategy.lower()
    if strategy not in ("cc", "csp"):
        raise ValueError(f"Unknown strategy '{strategy}'. Use 'cc' or 'csp'.")

    strategy_label = "COVERED CALL" if strategy == "cc" else "CASH SECURED PUT"
    print(f"\n📈 {strategy_label} SCREEN FOR {symbol}\n")

    data = fetch_underlying_data(symbol)
    S, q, r = data["spot_price"], data["dividend_yield"], data["risk_free_rate"]

    metrics = (
        ("Spot Price (S)", f"${S:,.2f}"),
        ("Dividend Yield (q)", f"{q * 100:.2f}%"),
        ("Risk-Free Rate (r)", f"{r * 100:.2f}%"),
    )
    label_width = max(len(label) for label, _ in metrics)
    value_width = max(len(value) for _, value in metrics)
    print(f"{'Metric':<{label_width}}  {'Value':>{value_width}}")
    print(f"{'-' * label_width}  {'-' * value_width}")
    for label, value in metrics:
        print(f"{label:<{label_width}}  {value:>{value_width}}")
    print()

    df_chain = fetch_option_chain(symbol)
    footnotes = [f"Fetched {len(df_chain)} option contracts."]

    compute_fn = compute_cc_metrics if strategy == "cc" else compute_csp_metrics
    df_screened = compute_fn(df_chain, S, r=r, q=q)
    footnotes.append(f"Computed {strategy_label.lower()} metrics for {len(df_screened)} contracts.")

    df_screened = df_screened[(df_screened["dte"] >= 7) & (df_screened["dte"] <= 60)]
    df_best = df_screened.sort_values("annualized_yield", ascending=False)

    cols = [
        "expiration", "strike", "premium", "dte", "pct_otm",
        "breakeven", "annualized_yield", "prob_win", "delta", "bid_ask_spread",
    ]
    cols = [c for c in cols if c in df_best.columns]
    df_display = df_best[cols].head(top_n).copy()
    df_display = df_display.rename(columns=_COLUMN_LABELS)
    table = df_display.to_string(index=False, formatters=_FORMATTERS)
    lines = table.splitlines()
    if lines:
        lines.insert(1, "-" * len(lines[0]))
    print("\n".join(lines))
    print("\nNotes:")
    for idx, note in enumerate(footnotes, start=1):
        print(f"{idx}. {note}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Screen covered-call or cash-secured put candidates.")
    parser.add_argument("symbol", help="Underlying stock symbol.")
    parser.add_argument(
        "--strategy",
        choices=["cc", "csp"],
        default="csp",
        help="Screening strategy: 'cc' for covered calls, 'csp' for cash secured puts (default: cc).",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="Number of rows to show in the top candidate table (default: 20).",
    )
    args = parser.parse_args()
    screen(args.symbol, strategy=args.strategy, top_n=args.top_n)
