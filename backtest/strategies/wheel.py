from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd

from gbm import TRADING_DAYS_PER_YEAR
from pricing import bs_call_price, bs_put_price, find_strike_for_target_delta


def run_wheel(
    prices: pd.DataFrame,
    initial_cash: float = 25_000.0,
    dte_days: int = 30,
    iv_annual: float = 0.25,
    risk_free_annual: float = 0.02,
    target_put_delta: float = 0.25,
    target_call_delta: float = 0.25,
    contracts: int = 1,
    commission_per_contract: float = 0.65,
    slippage_bps: float = 2.0,
) -> Dict[str, Any]:
    """
    Simple wheel backtest over a price series.

    prices: DataFrame with ['date','close'] business days.
    Returns dict with trade_ledger, equity_curve, summary.
    """
    prices = prices.copy().reset_index(drop=True)
    prices["date"] = pd.to_datetime(prices["date"])

    cash = initial_cash
    shares = 0
    reserved_cash = 0.0  # informational for CSP
    on_put = False
    on_call = False
    current_put: dict[str, Any] = {}
    current_call: dict[str, Any] = {}

    ledger: list[dict[str, Any]] = []
    equity: list[dict[str, Any]] = []

    r = risk_free_annual
    sigma = iv_annual

    i = 0
    N = len(prices)
    while i < N:
        date_i = prices.at[i, "date"]
        S = float(prices.iloc[i]["close"])

        equity_value = cash + shares * S
        equity.append(
            {"date": date_i, "equity": equity_value, "cash": cash, "shares": shares}
        )

        if on_put and i == current_put["expiry_idx"]:
            K = current_put["K"]
            qty = current_put["contracts"]
            premium = current_put["premium"]
            fees = current_put["fees"]
            if S < K:
                buy_cost = 100 * qty * K
                shares += 100 * qty
                cash -= buy_cost
            on_put = False
            reserved_cash = 0.0
            ledger.append(
                {
                    "date": date_i,
                    "action": "PUT_EXPIRY",
                    "S": S,
                    "K": K,
                    "premium": premium,
                    "fees": fees,
                    "assigned": int(S < K),
                    "qty": qty,
                }
            )

        if on_call and i == current_call["expiry_idx"]:
            K = current_call["K"]
            qty = current_call["contracts"]
            premium = current_call["premium"]
            fees = current_call["fees"]
            if S > K:
                sell_value = 100 * qty * K
                cash += sell_value
                shares -= 100 * qty
            on_call = False
            ledger.append(
                {
                    "date": date_i,
                    "action": "CALL_EXPIRY",
                    "S": S,
                    "K": K,
                    "premium": premium,
                    "fees": fees,
                    "called_away": int(S > K),
                    "qty": qty,
                }
            )

        if not on_put and not on_call:
            if shares >= 100 * contracts:
                T = dte_days / TRADING_DAYS_PER_YEAR
                Kc = find_strike_for_target_delta(
                    S, r, sigma, T, target_call_delta, "call"
                )
                call_price = bs_call_price(S, Kc, r, sigma, T)
                call_credit = call_price * 100 * contracts * (1 - slippage_bps / 1e4)
                fees = commission_per_contract * contracts
                cash += call_credit - fees
                on_call = True
                current_call = {
                    "open_idx": i,
                    "expiry_idx": min(N - 1, i + dte_days),
                    "K": Kc,
                    "premium": call_credit,
                    "fees": fees,
                    "contracts": contracts,
                }
                ledger.append(
                    {
                        "date": date_i,
                        "action": "SELL_CC",
                        "S": S,
                        "K": Kc,
                        "premium": call_credit,
                        "fees": fees,
                        "qty": contracts,
                    }
                )
            else:
                T = dte_days / TRADING_DAYS_PER_YEAR
                Kp = find_strike_for_target_delta(
                    S, r, sigma, T, target_put_delta, "put"
                )
                put_price = bs_put_price(S, Kp, r, sigma, T)
                required_cash = 100 * contracts * Kp
                if cash < required_cash:
                    i += 1
                    continue
                put_credit = put_price * 100 * contracts * (1 - slippage_bps / 1e4)
                fees = commission_per_contract * contracts
                cash += put_credit - fees
                reserved_cash = required_cash
                on_put = True
                current_put = {
                    "open_idx": i,
                    "expiry_idx": min(N - 1, i + dte_days),
                    "K": Kp,
                    "premium": put_credit,
                    "fees": fees,
                    "contracts": contracts,
                }
                ledger.append(
                    {
                        "date": date_i,
                        "action": "SELL_CSP",
                        "S": S,
                        "K": Kp,
                        "premium": put_credit,
                        "fees": fees,
                        "qty": contracts,
                    }
                )

        i += 1

    S_last = float(prices.iloc[N - 1]["close"])
    equity_value = cash + shares * S_last
    equity.append(
        {
            "date": prices.at[N - 1, "date"],
            "equity": equity_value,
            "cash": cash,
            "shares": shares,
        }
    )

    ledger_df = pd.DataFrame(ledger)
    equity_df = pd.DataFrame(equity).drop_duplicates(subset=["date"], keep="last")

    total_premium = ledger_df.loc[
        ledger_df["action"].isin(["SELL_CSP", "SELL_CC"]), "premium"
    ].sum()
    total_fees = ledger_df["fees"].sum() if not ledger_df.empty else 0.0
    assigned = (
        int(ledger_df.get("assigned", pd.Series(dtype=int)).sum())
        if "assigned" in ledger_df.columns
        else 0
    )
    called = (
        int(ledger_df.get("called_away", pd.Series(dtype=int)).sum())
        if "called_away" in ledger_df.columns
        else 0
    )

    equity_df = equity_df.sort_values("date")
    equity_series = np.array(equity_df["equity"].values)
    peak = np.maximum.accumulate(equity_series) if len(equity_series) else equity_series
    drawdown = (equity_series - peak) / peak if len(peak) else np.array([])
    max_dd = float(drawdown.min()) if len(drawdown) else 0.0

    total_return = (
        (equity_series[-1] - initial_cash) / initial_cash if len(equity_series) else 0.0
    )
    days = max(1, (equity_df["date"].iloc[-1] - equity_df["date"].iloc[0]).days)
    annualized_return = (
        (1 + total_return) ** (365.25 / days) - 1 if days > 0 else float("nan")
    )

    summary = {
        "initial_cash": initial_cash,
        "ending_equity": (
            float(equity_series[-1]) if len(equity_series) else initial_cash
        ),
        "total_return_pct": 100 * total_return,
        "annualized_return_pct": 100 * annualized_return,
        "max_drawdown_pct": 100 * max_dd,
        "premium_collected": float(total_premium) if not np.isnan(total_premium) else 0.0,
        "fees_paid": float(total_fees),
        "assignments": assigned,
        "call_aways": called,
        "final_shares": int(shares),
        "final_price": S_last,
    }

    return {"trade_ledger": ledger_df, "equity_curve": equity_df, "summary": summary}

