import numpy as np
import matplotlib.pyplot as plt

mu = 0.0
x = np.linspace(-10, 10, 1000)  # random variable
y = np.linspace(1, 5, 1000)  # sigma

X, Y = np.meshgrid(x, y)
Z = np.exp(-(X - mu)**2.0/(2 * Y**2.0)) / np.sqrt(2.0 * np.pi * Y**2.0)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)
ax.set_xlabel("X", fontsize=16)
ax.set_ylabel(r"$\sigma$", fontsize=16)
ax.set_zlabel(r"$f(\sigma)$", fontsize=16)
plt.show()
