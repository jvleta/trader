import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-4, 4, 1000)
y = np.exp(-0.5 * x**2.0) / np.sqrt(2.0 * np.pi)

n = 500
M = 10000
mu = 2.0
sigma = np.sqrt(0.5 * (np.exp(2.0) - 7.0))

S = np.zeros((M), float)
for i in range(M):
    S[i] = (np.sum(np.exp(np.sqrt(np.random.rand(n, 1)))) -
            n * mu) / (sigma * np.sqrt(n))

plt.figure()
plt.hist(S, density=True, label="sample data")
plt.plot(x, y, label="density")
plt.legend()
plt.xlim(-4.1, 4.1)
plt.grid()
plt.show()