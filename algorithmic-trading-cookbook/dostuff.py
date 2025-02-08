from openbb import obb

obb.user.preferences.output_type = "dataframe"

data = obb.equity.price.historical("SPY", provider="yfinance")

print(data)