import numpy as np


def compute_call_option_payout(asset_price_range, exercise_price):
    return np.array([max(s, exercise_price, 0) for s in asset_price_range])


def compute_put_option_payout(asset_price_range, exercise_price):
    return np.array([max(exercise_price - s, 0) for s in asset_price_range])


def compute_bull_spread_payout(asset_price_range, exercise_price1, exercise_price2):
    return np.array([max(s - exercise_price1, 0) - max(s - exercise_price2, 0) for s in asset_price_range])


def compute_butterfly_spread_payout(asset_price_range, low_strike, mid_strike, high_strike):
    return np.array([
        max(s - low_strike, 0)
        - 2 * max(s - mid_strike, 0)
        + max(s - high_strike, 0)
        for s in asset_price_range
    ])
