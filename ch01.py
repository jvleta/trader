import numpy as np
import matplotlib.pyplot as plt


def make_payout_diagram(E1, E2):
    S = np.linspace(0, 6, 100)
    B = np.array([max(s - E1, 0) - max(s - E2, 0) for s in S])
    plt.plot(S, B)
    plt.ylabel('S')
    plt.xlabel('B')
    plt.show()
    plt.grid()

if __name__ == "__main__":
    E1 = 2
    E2 = 4

    make_payout_diagram(E1, E2)
