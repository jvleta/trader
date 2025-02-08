import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("data/AAPL_call_data.csv")

plt.plot(df.strike, df.impliedVolatility)
E = df.strike
S = df.lastPrice

plt.show()