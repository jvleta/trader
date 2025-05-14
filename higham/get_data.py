import yfinance as yf
import pandas as pd


def get_data(ticker):
    # Fetch the options chain for a specific expiration date
    stock = yf.Ticker(ticker)

    # Get the expiration dates available
    expiration_dates = stock.options
    print("Available Expiration Dates:", expiration_dates)

    # Choose an expiration date (for demonstration, we'll use the first available)
    chosen_date = expiration_dates[0]

    # Fetch the options chain for the chosen date
    options_chain = stock.option_chain(chosen_date)

    # Separate calls and puts
    calls = pd.DataFrame(options_chain.calls)
    calls.to_csv(f"data/{ticker}_call_data.csv", index=False)

    puts = pd.DataFrame(options_chain.puts)
    puts.to_csv(f"data/{ticker}_put_data.csv", index=False)


if __name__ == "__main__":
    # Define the ticker symbol
    tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "KO", "JPM", "BAC", "PFE", "JNJ"]
    for ticker in tickers:
        get_data(ticker)

