from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from data import fetch_option_chain, fetch_underlying_data
from llm import LLMConfig, explain_candidates
from metrics import compute_cash_secured_put_metrics, compute_covered_call_metrics


def screen(
    symbol: str,
    call_type: str = "covered_call",
    *,
    min_dte: int = 7,
    max_dte: int = 60,
    top: int = 20,
    explain: bool = False,
    risk_profile: Optional[Dict[str, Any]] = None,
    llm_cfg: Optional[LLMConfig] = None,
) -> pd.DataFrame:
    """
    Screen option contracts for a symbol and return a sorted candidate table.

    Network required (OpenBB) and optional LLM explanation (OpenAI).
    """
    if call_type not in ("covered_call", "cash_secured_put"):
        raise ValueError("call_type must be 'covered_call' or 'cash_secured_put'")

    banner = (
        f"\nCOVERED CALL SCREEN FOR {symbol}\n"
        if call_type == "covered_call"
        else f"\nCASH-SECURED PUT SCREEN FOR {symbol}\n"
    )
    print(banner)

    data = fetch_underlying_data(symbol)
    S, q, r = data["spot_price"], data["dividend_yield"], data["risk_free_rate"]

    print(f"Spot Price (S): {S:.2f}")
    print(f"Dividend Yield (q): {q}")
    print(f"Risk-Free Rate (r): {r}\n")

    df_chain = fetch_option_chain(symbol)
    print(f"Fetched {len(df_chain)} option contracts.\n")

    if call_type == "covered_call":
        df_metrics = compute_covered_call_metrics(df_chain, S)
        print(f"Computed covered-call metrics for {len(df_metrics)} contracts.\n")
    else:
        df_metrics = compute_cash_secured_put_metrics(df_chain, S)
        print(f"Computed cash-secured put metrics for {len(df_metrics)} contracts.\n")

    df_metrics = df_metrics[(df_metrics["dte"] >= min_dte) & (df_metrics["dte"] <= max_dte)]
    df_best = df_metrics.sort_values("annualized_yield", ascending=False)

    pct_col = "pct_otm" if call_type == "covered_call" else "pct_itm"
    cols = [
        "expiration",
        "strike",
        "premium",
        "dte",
        pct_col,
        "breakeven",
        "annualized_yield",
    ]
    print(df_best[cols].head(top).to_string(index=False))
    print("\nDone.\n")

    if explain:
        markdown_text = explain_candidates(
            df_best,
            risk_profile=risk_profile,
            cfg=llm_cfg or LLMConfig(),
        )
        print(markdown_text)

    return df_best

