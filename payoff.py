import numpy as np
import matplotlib.pyplot as plt


def call_payoff(asset_price, strike):
    # Call option payoff: max(S - E, 0)
    return np.maximum(asset_price - strike, 0)


def put_payoff(asset_price, strike):
    # Put option payoff: max(E - S, 0)
    return np.maximum(strike - asset_price, 0)


class Payoff(object):
    """Base payoff calculator with no plotting concerns."""

    def __init__(self, exercise_price):
        self.exercise_price = exercise_price

    def __call__(self, asset_price):
        """Return payoff for given asset prices; subclasses must override."""
        raise NotImplementedError("Subclasses must implement this method")


class CallOptionPayoff(Payoff):
    """European call option payoff."""

    def __init__(self, exercise_price):
        """Initialize call option payoff with strike price."""
        super().__init__(exercise_price)

    def __call__(self, asset_price):
        """Return call option payoff for the given asset prices."""
        return call_payoff(asset_price, self.exercise_price)


class PutOptionPayoff(Payoff):
    """European put option payoff."""

    def __init__(self, exercise_price):
        """Initialize put option payoff with strike price."""
        super().__init__(exercise_price)

    def __call__(self, asset_price):
        """Return put option payoff for the given asset prices."""
        return put_payoff(asset_price, self.exercise_price)


class BullSpreadPayoff(Payoff):
    """Bull spread constructed from two call options."""

    def __init__(self, exercise_price1, exercise_price2):
        """Initialize bull spread with lower and upper strikes."""
        super().__init__((exercise_price1, exercise_price2))

    def __call__(self, asset_price):
        """Return bull spread payoff for the given asset prices."""
        exercise_price1, exercise_price2 = self.exercise_price
        return call_payoff(asset_price, exercise_price1) - call_payoff(
            asset_price, exercise_price2
        )


class ButterflySpreadPayoff(Payoff):
    """Butterfly spread constructed from three call options."""

    def __init__(self, low_strike, mid_strike, high_strike):
        """Initialize butterfly spread with low, middle, and high strikes."""
        super().__init__((low_strike, mid_strike, high_strike))

    def __call__(self, asset_price):
        """Return butterfly spread payoff for the given asset prices."""
        low_strike, mid_strike, high_strike = self.exercise_price
        return (
            call_payoff(asset_price, low_strike)
            - 2 * call_payoff(asset_price, mid_strike)
            + call_payoff(asset_price, high_strike)
        )


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

    inferred_title = title or f"{payoff.__class__.__name__} Payoff"

    plt.figure()
    plt.plot(asset_prices, payout_values)
    plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    plt.title(inferred_title)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    # Example usage
    call_payoff_example = CallOptionPayoff(exercise_price=95)
    plot_payoff(
        call_payoff_example,
        min_asset_price=80,
        max_asset_price=120,
        ylabel=r"$C$",
        title="Call Option Payoff",
    )

    put_payoff_example = PutOptionPayoff(exercise_price=105)
    plot_payoff(
        put_payoff_example,
        min_asset_price=80,
        max_asset_price=120,
        ylabel=r"$P$",
        title="Put Option Payoff",
    )

    bull_spread = BullSpreadPayoff(exercise_price1=90, exercise_price2=110)
    plot_payoff(
        bull_spread,
        min_asset_price=80,
        max_asset_price=120,
        title="Bull Spread Payoff",
    )

    butterfly_spread = ButterflySpreadPayoff(
        low_strike=90, mid_strike=100, high_strike=110
    )
    plot_payoff(
        butterfly_spread,
        min_asset_price=80,
        max_asset_price=120,
        title="Butterfly Spread Payoff",
    )
