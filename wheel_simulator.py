# Wheel strategy simulator (self-contained)
# - Uses synthetic GBM price data by default (no internet access).
# - You can replace with your own CSV: columns ["date","close"] in price.csv
# - Produces a trade ledger, equity curve, and summary stats.
#
# Notes:
# - Options priced with Black–Scholes; strikes picked to hit a target delta via bisection.
# - Rolls every N trading days (DTE). No early assignment modeled.
# - One contract per cycle for simplicity (scale via `contracts`).
#
# If you want to tweak parameters, scroll to the CONFIG section below.

import pandas as pd
import matplotlib.pyplot as plt

from gbm import simulate_gbm_prices
from wheel_config import (
    initial_cash,
    start_price,
    mu_annual,
    iv_annual,
    risk_free_annual,
    dte_days,
    contracts,
    target_put_delta,
    target_call_delta,
    commission_per_contract,
    slippage_bps,
    years_to_simulate,
    use_csv_if_present,
    SEED,
)
from backtest.data import try_load_prices_csv
from backtest.strategies.wheel import run_wheel


if __name__ == "__main__":
    df_prices = try_load_prices_csv() if use_csv_if_present else None
    if df_prices is None:
        df_prices = simulate_gbm_prices(
            S0=start_price,
            mu=mu_annual,
            sigma=iv_annual,
            years=years_to_simulate,
            seed=SEED,
        )

    # Run the simulation
    results = run_wheel(
        df_prices,
        initial_cash=initial_cash,
        dte_days=dte_days,
        iv_annual=iv_annual,
        risk_free_annual=risk_free_annual,
        target_put_delta=target_put_delta,
        target_call_delta=target_call_delta,
        contracts=contracts,
        commission_per_contract=commission_per_contract,
        slippage_bps=slippage_bps,
    )

    trade_ledger = results["trade_ledger"]
    equity_curve = results["equity_curve"]
    summary = results["summary"]


    # Plot equity curve
    plt.figure(figsize=(10, 4))
    plt.plot(equity_curve["date"], equity_curve["equity"])
    plt.title("Wheel Strategy Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Equity ($)")
    plt.tight_layout()
    plt.show()

    # Save outputs
    # ledger_path = "wheel_trade_ledger.csv"
    # equity_path = "wheel_equity_curve.csv"
    # chart_path = "wheel_equity_curve.png"
    # df_prices.to_csv("price_used.csv", index=False)
    # trade_ledger.to_csv(ledger_path, index=False)
    # equity_curve.to_csv(equity_path, index=False)
    # plt.savefig(chart_path)
