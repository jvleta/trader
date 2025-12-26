import math
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from wheel_config import TRADING_DAYS_PER_YEAR

def simulate_gbm_prices(
    S0: float, mu: float, sigma: float, years: float, seed: int = 0
) -> pd.DataFrame:
    np.random.seed(seed)
    n = int(TRADING_DAYS_PER_YEAR * years)
    dt = 1.0 / TRADING_DAYS_PER_YEAR
    shocks = np.random.normal(0.0, 1.0, size=n)
    prices = [S0]
    for z in shocks:
        # GBM discretization
        next_price = prices[-1] * math.exp(
            (mu - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * z
        )
        prices.append(max(0.01, next_price))
    dates = pd.bdate_range(
        start=datetime.today().date() - timedelta(days=n * 1.5),
        periods=len(prices),
        freq="B",
    )
    df = pd.DataFrame({"date": dates, "close": prices})
    return df.reset_index(drop=True)
