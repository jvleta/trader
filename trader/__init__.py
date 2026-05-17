from .data import fetch_underlying_data, fetch_option_chain
from .analytics import compute_cc_metrics, compute_csp_metrics, _STRATEGIES
from .plots import plot_payoff

__all__ = [
    "screen",
    "plot_payoff",
    "compute_cc_metrics",
    "compute_csp_metrics",
    "fetch_underlying_data",
    "fetch_option_chain",
]

import pandas as pd

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


def _print_key_value_table(rows: tuple[tuple[str, str], ...]) -> None:
    label_width = max(len(label) for label, _ in rows)
    value_width = max(len(value) for _, value in rows)
    print(f"{'Metric':<{label_width}}  {'Value':>{value_width}}")
    print(f"{'-' * label_width}  {'-' * value_width}")
    for label, value in rows:
        print(f"{label:<{label_width}}  {value:>{value_width}}")


def screen(symbol: str, strategy: str = "cc", top_n: int = 20) -> None:
    strategy = strategy.lower()
    if strategy not in _STRATEGIES:
        raise ValueError(f"Unknown strategy '{strategy}'. Choose from: {', '.join(_STRATEGIES)}.")

    strategy_label, compute_fn = _STRATEGIES[strategy]
    print(f"\n📈 {strategy_label} SCREEN FOR {symbol}\n")

    data = fetch_underlying_data(symbol)
    S, q, r = data["spot_price"], data["dividend_yield"], data["risk_free_rate"]

    _print_key_value_table((
        ("Spot Price (S)", f"${S:,.2f}"),
        ("Dividend Yield (q)", f"{q * 100:.2f}%"),
        ("Risk-Free Rate (r)", f"{r * 100:.2f}%"),
    ))
    print()

    df_chain = fetch_option_chain(symbol)
    footnotes = [f"Fetched {len(df_chain)} option contracts."]

    df_screened = compute_fn(df_chain, S, r=r, q=q)
    footnotes.append(f"Computed {strategy_label.lower()} metrics for {len(df_screened)} contracts.")

    df_screened = df_screened[(df_screened["dte"] >= 7) & (df_screened["dte"] <= 60)]
    df_best = df_screened.sort_values("annualized_yield", ascending=False)

    cols = [
        "expiration", "strike", "premium", "dte", "pct_otm",
        "breakeven", "annualized_yield", "prob_win", "delta", "bid_ask_spread",
    ]
    cols = [c for c in cols if c in df_best.columns]
    df_display = df_best[cols].head(top_n).rename(columns=_COLUMN_LABELS)
    table = df_display.to_string(index=False, formatters=_FORMATTERS)
    lines = table.splitlines()
    if lines:
        lines.insert(1, "-" * len(lines[0]))
    print("\n".join(lines))
    print("\nNotes:")
    for idx, note in enumerate(footnotes, start=1):
        print(f"{idx}. {note}")
