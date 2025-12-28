from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from backtest import get_strategy_names, run_strategy
from backtest.data import try_load_prices_csv
from gbm import simulate_gbm_prices
from wheel_config import (
    SEED,
    commission_per_contract,
    contracts,
    dte_days,
    initial_cash,
    iv_annual,
    mu_annual,
    risk_free_annual,
    slippage_bps,
    start_price,
    target_call_delta,
    target_put_delta,
    use_csv_if_present,
    years_to_simulate,
)

def screen(symbol: str, call_type: str = "covered_call", **kwargs: Any):
    """
    Backwards-compatible import path for older code:
    `from trader import screen`.
    """
    from screening import screen as _screen

    return _screen(symbol, call_type=call_type, **kwargs)


def _cmd_screen(args: argparse.Namespace) -> int:
    from screening import screen
    from llm import LLMConfig

    llm_cfg = None
    if args.explain:
        llm_cfg = LLMConfig(model=args.llm_model, temperature=args.llm_temperature)

    risk_profile: Optional[Dict[str, Any]] = None
    if args.risk_profile_json:
        risk_profile = json.loads(args.risk_profile_json)

    screen(
        args.symbol,
        call_type=args.type,
        min_dte=args.min_dte,
        max_dte=args.max_dte,
        top=args.top,
        explain=args.explain,
        risk_profile=risk_profile,
        llm_cfg=llm_cfg,
    )
    return 0


def _cmd_backtest(args: argparse.Namespace) -> int:
    if args.prices:
        prices = try_load_prices_csv(args.prices)
        if prices is None:
            raise SystemExit(f"Failed to load prices from CSV: {args.prices}")
    else:
        prices = try_load_prices_csv() if (use_csv_if_present and not args.synthetic) else None

    if prices is None:
        prices = simulate_gbm_prices(
            S0=args.start_price,
            mu=args.mu_annual,
            sigma=args.iv_annual,
            years=args.years,
            seed=args.seed,
        )

    results = run_strategy(
        args.strategy,
        prices,
        initial_cash=args.initial_cash,
        dte_days=args.dte_days,
        iv_annual=args.iv_annual,
        risk_free_annual=args.risk_free_annual,
        target_put_delta=args.target_put_delta,
        target_call_delta=args.target_call_delta,
        contracts=args.contracts,
        commission_per_contract=args.commission_per_contract,
        slippage_bps=args.slippage_bps,
    )

    summary = results["summary"]
    print(json.dumps(summary, indent=2, default=str))

    if args.outdir:
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        prices.to_csv(outdir / "price_used.csv", index=False)
        results["trade_ledger"].to_csv(outdir / "trade_ledger.csv", index=False)
        results["equity_curve"].to_csv(outdir / "equity_curve.csv", index=False)
        (outdir / "summary.json").write_text(
            json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8"
        )

    if args.plot:
        import matplotlib.pyplot as plt

        equity_curve = results["equity_curve"]
        plt.figure(figsize=(10, 4))
        plt.plot(equity_curve["date"], equity_curve["equity"])
        plt.title(f"Equity Curve ({args.strategy})")
        plt.xlabel("Date")
        plt.ylabel("Equity ($)")
        plt.tight_layout()
        plt.show()

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="trader", description="Weekly options toolbox")
    sub = parser.add_subparsers(dest="command")

    p_screen = sub.add_parser("screen", help="Screen covered calls / CSPs (networked)")
    p_screen.add_argument("--symbol", required=True)
    p_screen.add_argument(
        "--type",
        choices=("covered_call", "cash_secured_put"),
        default="covered_call",
    )
    p_screen.add_argument("--min-dte", type=int, default=7)
    p_screen.add_argument("--max-dte", type=int, default=60)
    p_screen.add_argument("--top", type=int, default=20)
    p_screen.add_argument("--explain", action="store_true", help="Use LLM to rank/explain")
    p_screen.add_argument("--llm-model", default="gpt-4.1-mini")
    p_screen.add_argument("--llm-temperature", type=float, default=0.2)
    p_screen.add_argument(
        "--risk-profile-json",
        default=None,
        help="JSON string passed to the LLM as a risk profile",
    )
    p_screen.set_defaults(func=_cmd_screen)

    p_backtest = sub.add_parser("backtest", help="Backtest a strategy over prices")
    p_backtest.add_argument("--strategy", choices=get_strategy_names(), default="wheel")
    p_backtest.add_argument("--prices", default=None, help="CSV with columns date,close")
    p_backtest.add_argument(
        "--synthetic",
        action="store_true",
        help="Force synthetic prices (ignore price.csv auto-load)",
    )
    p_backtest.add_argument("--years", type=float, default=years_to_simulate)
    p_backtest.add_argument("--start-price", type=float, default=start_price)
    p_backtest.add_argument("--mu-annual", type=float, default=mu_annual)
    p_backtest.add_argument("--seed", type=int, default=SEED)

    p_backtest.add_argument("--initial-cash", type=float, default=initial_cash)
    p_backtest.add_argument("--dte-days", type=int, default=dte_days)
    p_backtest.add_argument("--iv-annual", type=float, default=iv_annual)
    p_backtest.add_argument("--risk-free-annual", type=float, default=risk_free_annual)
    p_backtest.add_argument("--target-put-delta", type=float, default=target_put_delta)
    p_backtest.add_argument("--target-call-delta", type=float, default=target_call_delta)
    p_backtest.add_argument("--contracts", type=int, default=contracts)
    p_backtest.add_argument(
        "--commission-per-contract", type=float, default=commission_per_contract
    )
    p_backtest.add_argument("--slippage-bps", type=float, default=slippage_bps)

    p_backtest.add_argument("--outdir", default=None)
    p_backtest.add_argument("--plot", action="store_true")
    p_backtest.set_defaults(func=_cmd_backtest)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
