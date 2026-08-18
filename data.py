"""Market data retrieval and formatting via Yahoo Finance."""

import yfinance as yf


def get_price_data(ticker: str) -> str:
    """Fetch recent daily prices and 50-day moving average formatted for LLM consumption."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period="3mo")

    if hist.empty:
        return f"No price data found for {ticker}."

    recent = hist["Close"].tail(10)
    latest = hist["Close"].iloc[-1]
    ma50 = hist["Close"].tail(50).mean()
    lines = [f"{d.date()}: {p:.2f}" for d, p in recent.items()]
    return (
        f"Ticker: {ticker}\n"
        f"Latest close: {latest:.2f}\n"
        f"50-day average: {ma50:.2f}\n"
        f"Last 10 closes:\n" + "\n".join(lines)
    )


def get_volatility_data(ticker: str) -> str:
    """Fetch 3-month price volatility metrics and peak-to-trough drawdown formatted for LLM consumption."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period="3mo")

    if hist.empty:
        return f"No price data found for {ticker}."

    closes = hist["Close"]
    returns = closes.pct_change().dropna()
    vol = returns.std() * 100
    drawdown = ((closes - closes.cummax()) / closes.cummax()).min() * 100

    return (
        f"Ticker: {ticker}\n"
        f"Daily volatility: {vol:.2f}%\n"
        f"Max drawdown (3mo): {drawdown:.2f}%\n"
        f"Range: {closes.min():.2f} to {closes.max():.2f}"
    )
