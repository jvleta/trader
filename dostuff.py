import yfinance as yf
import pandas as pd

# Define the ticker symbol
ticker = "AAPL"  # Change this to any stock symbol you're interested in

# Initialize the stock object
stock = yf.Ticker(ticker)

# Fetch the current asset price (S)
asset_price = stock.info['currentPrice']

# Fetch available expiration dates
expiration_dates = stock.options
if not expiration_dates:
    print(f"No options data available for {ticker}")
else:
    # Choose an expiration date (first one as an example)
    chosen_date = expiration_dates[0]

    # Fetch the options chain
    options_chain = stock.option_chain(chosen_date)

    # Extract calls and puts
    calls = options_chain.calls
    puts = options_chain.puts

    # Add the current stock price as a new column to the options data
    calls['assetPrice'] = asset_price
    puts['assetPrice'] = asset_price

    # Create tables for calls and puts
    calls_table = calls[['strike', 'lastPrice', 'assetPrice']].rename(
        columns={'assetPrice': 'Asset Price (S)', 'strike': 'Exercise Price (E)', 'lastPrice': 'Option Price (C)'}
    )
    puts_table = puts[['strike', 'lastPrice', 'assetPrice']].rename(
        columns={'assetPrice': 'Asset Price (S)', 'strike': 'Exercise Price (E)', 'lastPrice': 'Option Price (P)'}
    )

    # Display the data
    print("Calls Table:")
    print(calls_table.head())

    print("\nPuts Table:")
    print(puts_table.head())

    # Save to CSV if needed
    calls_table.to_csv("calls_table.csv", index=False)
    puts_table.to_csv("puts_table.csv", index=False)
