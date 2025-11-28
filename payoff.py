import numpy as np
import matplotlib.pyplot as plt


def long_call_payoff(asset_price, strike):
    """Long call payoff: max(S - E, 0)."""
    return np.maximum(asset_price - strike, 0)


def long_put_payoff(asset_price, strike):
    """Long put payoff: max(E - S, 0)."""
    return np.maximum(strike - asset_price, 0)


def short_call_payoff(asset_price, strike):
    """Short call payoff: -max(S - E, 0)."""
    return -long_call_payoff(asset_price, strike)


def short_put_payoff(asset_price, strike):
    """Short put payoff: -max(E - S, 0)."""
    return -long_put_payoff(asset_price, strike)


def bull_spread_payoff(asset_price, lower_strike, upper_strike):
    """Bull spread from long lower-strike call and short higher-strike call."""
    return long_call_payoff(asset_price, lower_strike) - long_call_payoff(
        asset_price, upper_strike
    )


def butterfly_spread_payoff(asset_price, low_strike, mid_strike, high_strike):
    """Butterfly spread from long low/high calls and short twice mid call."""
    return (
        long_call_payoff(asset_price, low_strike)
        - 2 * long_call_payoff(asset_price, mid_strike)
        + long_call_payoff(asset_price, high_strike)
    )

# TODO: Implement straddle payoff diagram.
# TODO: Implement strangle payoff diagram.
# TODO: Implement covered call payoff diagram.
# TODO: Implement protective put payoff diagram.
# TODO: Implement collar payoff diagram.
# TODO: Implement iron condor payoff diagram.
# TODO: Implement iron butterfly payoff diagram.
# TODO: Implement calendar spread payoff diagram.
# TODO: Implement ratio spread payoff diagram.
# TODO: Implement condor payoff diagram.

def make_payoff(payoff_fn, *args, **kwargs):
    """
    Generic factory: returns a callable that binds payoff params except asset_price.
    Assumes payoff_fn takes asset_price as its first parameter.
    """
    return lambda asset_price: payoff_fn(asset_price, *args, **kwargs)


def plot_payoff(
    payoff,
    min_asset_price,
    max_asset_price,
    xlabel=r"$S(T)$",
    ylabel=None,
    title=None,
):
    """Plot a payoff callable over a range of asset prices."""
    asset_prices = np.linspace(min_asset_price, max_asset_price, 1000)
    payout_values = payoff(asset_prices)

    payoff_name = getattr(payoff, "__name__", payoff.__class__.__name__)
    inferred_title = title or f"{payoff_name} Payoff"

    plt.figure()
    plt.plot(asset_prices, payout_values)
    plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    plt.title(inferred_title)
    plt.grid()
    plt.show()

# TODO: Add unit tests for payoff functions and plotting.

# TODO: Add type hints for all functions.

# TODO: Add docstrings with examples for all functions.

# TODO: Add a plotting function that supports multiple payoffs on the same graph.
if __name__ == "__main__":
    # Example usage
    call_payoff_example = make_payoff(long_call_payoff, strike=95)
    plot_payoff(
        call_payoff_example,
        min_asset_price=80,
        max_asset_price=120,
        ylabel=r"$C$",
        title="Call Option Payoff",
    )

    put_payoff_example = make_payoff(long_put_payoff, strike=105)
    plot_payoff(
        put_payoff_example,
        min_asset_price=80,
        max_asset_price=120,
        ylabel=r"$P$",
        title="Put Option Payoff",
    )

    bull_spread = make_payoff(bull_spread_payoff, lower_strike=90, upper_strike=110)
    plot_payoff(
        bull_spread,
        min_asset_price=80,
        max_asset_price=120,
        title="Bull Spread Payoff",
    )

    butterfly_spread = make_payoff(
        butterfly_spread_payoff, low_strike=90, mid_strike=100, high_strike=110
    )
    plot_payoff(
        butterfly_spread,
        min_asset_price=80,
        max_asset_price=120,
        title="Butterfly Spread Payoff",
    )
