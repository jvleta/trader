import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from .analytics import _STRATEGIES
from .data import fetch_underlying_data, fetch_option_chain


def _payoff_cc(S: float, K: float, premium: float, prices: np.ndarray) -> np.ndarray:
    return (prices - S) + premium - np.maximum(prices - K, 0)


def _payoff_csp(K: float, premium: float, prices: np.ndarray) -> np.ndarray:
    return premium - np.maximum(K - prices, 0)


def plot_payoff(symbol: str, strategy: str = "csp", strike: float | None = None, top_n: int = 5) -> None:
    strategy = strategy.lower()
    if strategy not in _STRATEGIES:
        raise ValueError(f"Unknown strategy '{strategy}'. Choose from: {', '.join(_STRATEGIES)}.")

    strategy_label, compute_fn = _STRATEGIES[strategy]

    data = fetch_underlying_data(symbol)
    S, q, r = data["spot_price"], data["dividend_yield"], data["risk_free_rate"]

    df_chain = fetch_option_chain(symbol)
    df = compute_fn(df_chain, S, r=r, q=q)
    df = df[(df["dte"] >= 7) & (df["dte"] <= 60)]

    if strike is not None:
        df = df.iloc[(df["strike"] - strike).abs().argsort()[:1]]
    else:
        df = df.sort_values("annualized_yield", ascending=False).head(top_n)

    prices = np.linspace(S * 0.7, S * 1.3, 400)

    _, ax = plt.subplots(figsize=(10, 6))
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.axvline(S, color="gray", linewidth=0.8, linestyle=":", label=f"Spot ${S:,.2f}")

    for _, row in df.iterrows():
        K, premium, exp = row["strike"], row["premium"], row["expiration"]
        if strategy == "cc":
            payoff = _payoff_cc(S, K, premium, prices)
            label = f"CC  K=${K:.0f}  exp={exp}"
        else:
            payoff = _payoff_csp(K, premium, prices)
            label = f"CSP  K=${K:.0f}  exp={exp}"
        ax.plot(prices, payoff, label=label)

    ax.set_xlabel("Underlying Price at Expiration")
    ax.set_ylabel("P&L per Share ($)")
    ax.set_title(f"{strategy_label} Payoff Diagram — {symbol}")
    ax.legend(fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
