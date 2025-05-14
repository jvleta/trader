import numpy as np
from scipy.special import erf


def normal_cdf(x): return 0.5 * (1.0 + erf(x / np.sqrt(2.0)))


def solve_bse(S, E, r, sigma, tau):
    if tau > 0:
        d1 = (np.log(S / E) + (r + 0.5 * sigma**2.0)
              * (tau)) / (sigma * np.sqrt(tau))
        d2 = d1 - sigma * np.sqrt(tau)
        N1 = 0.5 * (1.0 + erf(d1 / np.sqrt(2.0)))
        N2 = 0.5 * (1.0 + erf(d2 / np.sqrt(2.0)))
        C = S * N1 - E * np.exp(-r * tau) * N2
        Cdelta = N1
        P = C + E * np.exp(-r * tau) - S
        Pdelta = Cdelta - 1
    else:
        C = max(S - E, 0)
        Cdelta = 0.5 * (np.sign(S - E) + 1)
        P = max(E-S, 0)
        Pdelta = Cdelta - 1
    return C, Cdelta, P, Pdelta
