import numpy as np
import matplotlib.pyplot as plt
from payout import compute_bull_spread_payout, compute_call_option_payout, compute_put_option_payout, compute_butterfly_spread_payout


def make_call_option_payout_diagram():
    S = np.linspace(0, 6, 100)
    E = 2
    C = compute_call_option_payout(S, E)

    plt.figure()
    plt.plot(S, C)
    plt.xlabel(r'$S(T)$')
    plt.ylabel(r'$C$')
    plt.title('Call Option Payout')
    plt.grid()


def make_put_option_payout_diagram():
    S = np.linspace(0, 6, 100)
    E = 2
    P = compute_put_option_payout(S, E)

    plt.figure()
    plt.plot(S, P)
    plt.xlabel(r'$S(T)$')
    plt.ylabel(r'$P$')
    plt.title('Put Option Payout')
    plt.grid()


def make_bull_spread_payout_diagram():
    S = np.linspace(0, 6, 100)
    E1 = 2
    E2 = 4
    B = compute_bull_spread_payout(S, E1, E2)

    plt.figure()
    plt.plot(S, B)
    plt.xlabel(r'$S(T)$')
    plt.ylabel(r'$B$')
    plt.title('Bull Spread Payout')
    plt.grid()


def make_butterfly_spread_payout_diagram():
    S = np.linspace(0, 6, 1000)
    E1 = 2
    E2 = 3
    E3 = 4

    B = compute_butterfly_spread_payout(S, E1, E2, E3)

    plt.figure()
    plt.plot(S, B)
    plt.xlabel(r'$S(T)$')
    plt.ylabel(r'$B$')
    plt.title('Butterfly Spread Payout')
    plt.grid()


if __name__ == "__main__":
    make_call_option_payout_diagram()
    make_put_option_payout_diagram()
    make_bull_spread_payout_diagram()
    make_butterfly_spread_payout_diagram()

    plt.show()
