import math

def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_d1(S: float, K: float, r: float, sigma: float, T: float) -> float:
    if S <= 0 or K <= 0 or sigma <= 0 or T <= 0:
        return float("nan")
    return (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))


def bs_call_price(S: float, K: float, r: float, sigma: float, T: float) -> float:
    d1 = bs_d1(S, K, r, sigma, T)
    d2 = d1 - sigma * math.sqrt(T)
    return S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)


def bs_put_price(S: float, K: float, r: float, sigma: float, T: float) -> float:
    d1 = bs_d1(S, K, r, sigma, T)
    d2 = d1 - sigma * math.sqrt(T)
    return K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)


def bs_call_delta(S: float, K: float, r: float, sigma: float, T: float) -> float:
    d1 = bs_d1(S, K, r, sigma, T)
    return _norm_cdf(d1)


def bs_put_delta(S: float, K: float, r: float, sigma: float, T: float) -> float:
    # Put delta = Call delta - 1
    return bs_call_delta(S, K, r, sigma, T) - 1.0


def find_strike_for_target_delta(
    S: float, r: float, sigma: float, T: float, target_delta: float, option_type: str
) -> float:
    """
    Find strike K such that the option's (absolute) delta ~= target_delta for puts,
    or delta ~= target_delta for calls. Uses bisection on K.
    """
    # Reasonable bounds around spot
    K_low = max(0.01, 0.5 * S)
    K_high = 1.5 * S

    def delta_given_K(K):
        if option_type == "put":
            return abs(bs_put_delta(S, K, r, sigma, T))
        else:
            return bs_call_delta(S, K, r, sigma, T)

    # Expand bounds if needed to ensure target lies within
    for _ in range(30):
        d_low = delta_given_K(K_low)
        d_high = delta_given_K(K_high)
        if (d_low - target_delta) * (d_high - target_delta) <= 0:
            break
        # expand range
        K_low *= 0.8
        K_high *= 1.2

    # Bisection
    for _ in range(100):
        K_mid = 0.5 * (K_low + K_high)
        d_mid = delta_given_K(K_mid)
        if abs(d_mid - target_delta) < 1e-4:
            return K_mid
        # For puts, delta decreases with higher strikes in abs terms; for calls, delta decreases with higher K.
        # We'll just compare d_mid vs target and move bounds accordingly using monotonicity.
        if d_mid > target_delta:
            # need lower delta -> increase K
            K_low = K_mid
        else:
            K_high = K_mid
    return K_mid
