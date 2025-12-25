import pandas as pd


def compute_covered_call_metrics(df: pd.DataFrame, spot_price: float):
    """Compute covered-call metrics for each contract."""
    df = df.copy()

    # Filter for calls only
    df = df[df["option_type"] == "call"]

    # Mid price = (bid + ask)/2
    df["premium"] = (df["bid"] + df["ask"]) / 2

    # Remove contracts with no liquidity
    df = df[df["premium"] > 0]

    # % OTM
    df["pct_otm"] = (df["strike"] - spot_price) / spot_price * 100

    # Breakeven point
    df["breakeven"] = spot_price - df["premium"]

    # Days to expiration
    df["dte"] = (pd.to_datetime(df["expiration"]) - pd.Timestamp.today()).dt.days

    # Annualized yield from premium
    df["annualized_yield"] = (df["premium"] / spot_price) * (365.0 / df["dte"])

    # Filter for strikes at or above spot price
    df = df[df["strike"] >= spot_price]

    return df


def compute_cash_secured_put_metrics(df: pd.DataFrame, spot_price: float):
    """Compute cash-secured put metrics for each contract."""
    df = df.copy()

    # Filter for puts only
    df = df[df["option_type"] == "put"]

    # Mid price = (bid + ask)/2
    df["premium"] = (df["bid"] + df["ask"]) / 2

    # Remove contracts with no liquidity
    df = df[df["premium"] > 0]

    # % ITM
    df["pct_itm"] = (spot_price - df["strike"]) / spot_price * 100

    # Breakeven point
    df["breakeven"] = spot_price + df["premium"]

    # Days to expiration
    df["dte"] = (pd.to_datetime(df["expiration"]) - pd.Timestamp.today()).dt.days

    # Annualized yield from premium
    df["annualized_yield"] = (df["premium"] / spot_price) * (365.0 / df["dte"])

    # Filter for strikes at or below spot price
    df = df[df["strike"] <= spot_price]

    return df
