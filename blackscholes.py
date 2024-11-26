import numpy as np
from scipy.special import erf


def normal_cdf(x): return 0.5 * (1.0 + erf(x / np.sqrt(2.0)))


def evalute_black_scholes_formula(asset_price, expiry_price, interest_rate, volatility, time_to_expiry):
    if time_to_expiry > 0:
        d1 = (np.log(asset_price / expiry_price) + (interest_rate + 0.5 * volatility**2.0)
              * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)

        N1 = normal_cdf(d1)
        N2 = normal_cdf(d2)

        call = asset_price * N1 - expiry_price * \
            np.exp(-interest_rate * time_to_expiry) * N2
        call_delta = N1
        call_vega = asset_price * np.sqrt(time_to_expiry) * \
            np.exp(-0.5 * d1**2) / np.sqrt(2 * np.pi)
        put = call + expiry_price * \
            np.exp(-interest_rate * time_to_expiry) - asset_price
        put_delta = call_delta - 1
        put_vega = call_vega
    else:
        call = max(asset_price - expiry_price, 0)
        call_delta = 0.5 * (np.sign(asset_price - expiry_price) + 1)
        call_vega = 0
        put = max(expiry_price - asset_price, 0)
        put_delta = call_delta - 1
        put_vega = 0
    return call, call_delta, call_vega, put, put_delta, put_vega
