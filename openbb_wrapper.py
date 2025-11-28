from datetime import date, timedelta
import numpy as np
import pandas as pd
from openbb import obb


def _parse_dividend_amounts(dividends) -> list[float]:
    if not dividends:
        return []

    if isinstance(dividends, dict):
        dividends = dividends.get("data") or dividends.get("results") or dividends

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
        for field in ("close", "price", "last", "regular_market_price"):
            value = getattr(latest, field, None)
            if value is not None and np.isfinite(value):
                return float(value)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to retrieve spot price for symbol: {symbol}"
        ) from exc
    raise RuntimeError(f"Invalid price data for symbol: {symbol}")


def get_dividend_yield(symbol: str) -> float:
    try:
        start_date = date.today() - timedelta(days=365)
        response = obb.equity.fundamental.dividends(
            symbol=symbol, start_date=start_date, end_date=date.today()
        )
        dividends = getattr(response, "data", None) or getattr(
            response, "results", None
        )
        amounts = _parse_dividend_amounts(dividends)
        if not amounts:
            raise ValueError("No valid dividend amounts found")

        total_dividends = sum(amounts)
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
    q = get_dividend_yield(symbol)
    r = get_risk_free_rate()
    return {"symbol": symbol, "spot_price": S, "dividend_yield": q, "risk_free_rate": r}



def fetch_option_chain(symbol: str, filter_expiries: list | None = None) -> pd.DataFrame:
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

    if "dte" in df.columns:
        df["T_years"] = pd.to_numeric(df["dte"], errors="coerce") / 365.0
    else:
        today = date.today()
        df["T_years"] = df["expiration"].apply(lambda d: (d - today).days / 365.0)

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
        df["market_price"] = (
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


if __name__ == "__main__":
    symbol = "AAPL"
    data = fetch_underlying_data(symbol)
    spot_price = data["spot_price"]
    dividend_yield = data["dividend_yield"]
    risk_free_rate = data["risk_free_rate"]
    print(f"The current spot price of {symbol} is: ${spot_price:.2f}")
    print(f"The trailing dividend yield of {symbol} is: {dividend_yield*100:.2f}%")
    print(f"The current risk-free rate is: {risk_free_rate*100:.2f}%")

    option_chain = fetch_option_chain(symbol)
    if option_chain.empty:
        print(f"No option chain data available for {symbol}.")
    else:
        print(f"Option chain for {symbol}:")
        print(option_chain.head(10))