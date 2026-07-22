"""
data.py
-------
This file is the "backend" of our tool: it talks to Yahoo Finance
(via the yfinance library) and hands back clean, simple data for
app.py to display. Keeping this separate from app.py is good practice —
it means the "get data" logic is separate from the "show data" logic.
"""

import yfinance as yf
import pandas as pd


def load_portfolio(path="portfolio.csv"):
    """Read your holdings from the CSV file into a pandas DataFrame."""
    return pd.read_csv(path)


def get_current_prices(tickers):
    """
    Given a list of tickers like ["AAPL", "MSFT"], return a dict mapping
    ticker -> current price.

    yfinance lets us fetch many tickers in a single call, which is much
    faster than looping and calling the API one ticker at a time.
    """
    if not tickers:
        return {}

    # download() pulls recent price history for all tickers at once.
    # period="5d" gives us a small buffer in case markets were closed
    # yesterday (weekends, holidays).
    data = yf.download(tickers, period="5d", progress=False)["Close"]

    prices = {}
    for ticker in tickers:
        try:
            # If multiple tickers, `data` has one column per ticker.
            # If there's only one ticker, `data` is a plain Series.
            series = data[ticker] if len(tickers) > 1 else data
            prices[ticker] = float(series.dropna().iloc[-1])
        except Exception:
            prices[ticker] = None  # couldn't fetch — we'll show this as N/A

    return prices


def get_news(ticker, max_items=3):
    """
    Return a small list of recent news items for a ticker.
    Each item is a dict with 'title', 'publisher', and 'link'.
    """
    try:
        news_items = yf.Ticker(ticker).news or []
    except Exception:
        news_items = []

    cleaned = []
    for item in news_items[:max_items]:
        # yfinance's news format has shifted between versions, so we
        # defensively pull from a couple of possible shapes.
        content = item.get("content", item)
        cleaned.append({
            "title": content.get("title", "Untitled"),
            "publisher": content.get("provider", {}).get("displayName", "Unknown source")
                         if isinstance(content.get("provider"), dict) else "Unknown source",
            "link": content.get("canonicalUrl", {}).get("url", "#")
                    if isinstance(content.get("canonicalUrl"), dict) else item.get("link", "#"),
        })
    return cleaned
