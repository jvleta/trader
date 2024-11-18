import numpy as np
import matplotlib.pyplot as plt


def eval_lognormal_pdf(mu, sigma, x):
    tempa = ((np.log(x / S) - (mu - 0.5 * sigma**2.0)*t)**2) / \
        (2 * t * sigma**2.0)
    tempb = x * sigma * np.sqrt(2.0 * np.pi * t)
    return np.exp(-tempa) / tempb


x = np.linspace(0.01, 4, 500)
t = 1
S = 1
mu = 0.05
sigma = 0.3
y1 = eval_lognormal_pdf(mu, 0.3, x)
y2 = eval_lognormal_pdf(mu, 0.5, x)

plt.plot(x, y1, 'r-', label=r'$\sigma = 0.3$')
plt.plot(x, y2, 'b:', label=r'$\sigma = 0.5$')
plt.legend()
plt.grid()
plt.title(r'Lognormal density, t = 1, S = 1, $\mu=0.05$')
plt.xlabel(r'$X$')
plt.ylabel(r'$f(X)$')
plt.ylim([0, 1.5])
plt.show()
