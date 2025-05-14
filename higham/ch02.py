import numpy as np
import matplotlib.pyplot as plt


dzero = 5
r = 0.15  # compound interest rate
T = 5  # 5 year period
m = 60  # 60 months

d_discrete = [dzero]
t_discrete = [0]
for i in range(m):
    nth_month = float(i + 1)
    time_in_years = nth_month / 12.0
    d = dzero * (1.0 + r * time_in_years / nth_month)**nth_month
    d_discrete.append(d)
    t_discrete.append(time_in_years)
    
t_continuous = np.linspace(0, T, 10000)
d_continuous = dzero * np.exp(r * t_continuous)
    
plt.plot(t_discrete, d_discrete, 'o')
plt.plot(t_continuous, d_continuous)
plt.show()
