import numpy as np
import matplotlib.pyplot as plt


S = 1
mu = 0.05
sigma = 0.5
L = 100
T = 1
dt = T / float(L)
M = 50

tvals = np.linspace(0, T, L + 1)

Svals0 = np.ones((M, 1))
Svals = np.cumulative_prod(np.exp(
    (mu - 0.5 * sigma**2.0) * dt + sigma * np.sqrt(dt) * np.random.randn(M, L)), axis=1)
Svals = np.hstack((Svals0, Svals))

plt.figure()
plt.plot(tvals, Svals.transpose())
plt.xlabel(r'$t$')
plt.ylabel(r'$S(t)$')
plt.title('50 asset paths')

plt.show()
