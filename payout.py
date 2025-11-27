import numpy as np
import matplotlib.pyplot as plt

def call_payoff(asset_price, strike):
    return np.maximum(asset_price - strike, 0)

def put_payoff(asset_price, strike):
    return np.maximum(strike - asset_price, 0)

class Payoff(object):

    def __init__(self, exercise_price, name: str = ""):
        self.exercise_price = exercise_price
        self.xlabel = r"$S(T)$"
        self.ylabel = name

    def _payoff(self, asset_price):
        raise NotImplementedError("Subclasses must implement this method")
    
    def make_payoff_plot(self, min_asset_price, max_asset_price):
        asset_prices = np.linspace(min_asset_price, max_asset_price, 1000)
        payout_values = self._payoff(asset_prices)

        plt.figure()
        plt.plot(asset_prices, payout_values)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(f"{self.__class__.__name__} Payoff")
        plt.grid()
        plt.show()

class CallOptionPayoff(Payoff):

    def __init__(self, exercise_price):
        super().__init__(exercise_price, name=r"$C$")

    def _payoff(self, asset_price):
        return call_payoff(asset_price, self.exercise_price)

class PutOptionPayoff(Payoff):

    def __init__(self, exercise_price):
        super().__init__(exercise_price, name=r"$P$")

    def _payoff(self, asset_price):
        return put_payoff(asset_price, self.exercise_price)    

class BullSpreadPayoff(Payoff):

    def __init__(self, exercise_price1, exercise_price2):
        super().__init__((exercise_price1, exercise_price2), name="Bull Spread Payoff")

    def _payoff(self, asset_price):
        exercise_price1, exercise_price2 = self.exercise_price
        return call_payoff(asset_price, exercise_price1) - call_payoff(asset_price, exercise_price2)

class ButterflySpreadPayoff(Payoff):

    def __init__(self, low_strike, mid_strike, high_strike):
        super().__init__((low_strike, mid_strike, high_strike), name="Butterfly Spread Payoff")

    def _payoff(self, asset_price):
        low_strike, mid_strike, high_strike = self.exercise_price
        return (call_payoff(asset_price, low_strike)
                - 2 * call_payoff(asset_price, mid_strike)
                + call_payoff(asset_price, high_strike))

if __name__ == "__main__":
    # Example usage
    call_payoff_example = CallOptionPayoff(exercise_price=95)
    call_payoff_example.make_payoff_plot(min_asset_price=80, max_asset_price=120)

    put_payoff_example = PutOptionPayoff(exercise_price=105)
    put_payoff_example.make_payoff_plot(min_asset_price=80, max_asset_price=120)

    bull_spread = BullSpreadPayoff(exercise_price1=90, exercise_price2=110)
    bull_spread.make_payoff_plot(min_asset_price=80, max_asset_price=120)

    butterfly_spread = ButterflySpreadPayoff(low_strike=90, mid_strike=100, high_strike=110)
    butterfly_spread.make_payoff_plot(min_asset_price=80, max_asset_price=120)
