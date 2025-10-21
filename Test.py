import yfinance as yf

dat = yf.Ticker("MSFT")

# get historical market data
data = yf.download("AAPL", start="2020-01-01", end="2021-01-01")
print(data.index)