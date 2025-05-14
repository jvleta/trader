import numpy as np
from scipy.special import erfinv
import matplotlib.pyplot as plt


M = 200
samples = np.random.normal(0, 1, M)
ssort = np.sort(samples)

pvals = np.linspace(1, M, M) / float(M+1)
zvals = np.sqrt(2.0) * erfinv(2.0 * pvals - 1)
xlim = np.max(np.abs(zvals)) + 1

plt.figure()
plt.plot(ssort, zvals, 'rx')
plt.plot([-xlim, xlim], [-xlim, xlim], 'g-')
plt.title(r'$N(0,1)$ quantile-quantile plot')
plt.show()
