from data import fetch_option_chain, fetch_underlying_data
from metrics import compute_covered_call_metrics, compute_cash_secured_put_metrics
from llm import explain_candidates, LLMConfig


def screen(symbol: str, call_type: str = "covered_call"):
    if call_type not in ("covered_call", "cash_secured_put"):
        raise ValueError("call_type must be 'covered_call' or 'cash_secured_put'")

    if call_type == "covered_call":
        print(f"\n📈 COVERED CALL SCREEN FOR {symbol}\n")
    else:
        print(f"\n📉 CASH-SECURED PUT SCREEN FOR {symbol}\n")

    # Underlying data
    data = fetch_underlying_data(symbol)
    S, q, r = data["spot_price"], data["dividend_yield"], data["risk_free_rate"]

    print(f"Spot Price (S): {S:.2f}")
    print(f"Dividend Yield (q): {q}")
    print(f"Risk-Free Rate (r): {r}\n")

    # Option chain
    df_chain = fetch_option_chain(symbol)
    print(f"Fetched {len(df_chain)} option contracts.\n")

    if call_type == "covered_call":
        # Compute covered-call metrics
        df_metrics = compute_covered_call_metrics(df_chain, S)
        print(f"Computed covered-call metrics for {len(df_metrics)} contracts.\n")
    else:
        # Compute cash-secured put metrics
        df_metrics = compute_cash_secured_put_metrics(df_chain, S)
        print(f"Computed cash-secured put metrics for {len(df_metrics)} contracts.\n")

    # Restrict to reasonable expirations (7–60 DTE)
    df_metrics = df_metrics[(df_metrics["dte"] >= 7) & (df_metrics["dte"] <= 60)]

    # Sort by annualized yield
    df_best = df_metrics.sort_values("annualized_yield", ascending=False)

    # Display top 20
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
    print(df_best[cols].head(20).to_string(index=False))

    print("\nDone.\n")
    return df_best


def main():
    df_candidates = screen("F", call_type="cash_secured_put")
    risk_profile = {
        "capital_per_trade": 5000,
        "max_drawdown_tolerance_pct": 15,
        "prefer_sectors": ["XLU", "XLP"],
        "avoid_underlying_price_below": 15,
    }

    markdown_text = explain_candidates(
        df_candidates,
        risk_profile=risk_profile,
        cfg=LLMConfig(model="gpt-4.1-mini", temperature=0.2),
    )

    print(markdown_text)


if __name__ == "__main__":
    main()
