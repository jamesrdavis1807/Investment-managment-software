

import yfinance as yf
import pandas as pd


def load_portfolio(path="portfolio.csv"):
  
    return pd.read_csv(path)


def get_current_prices(tickers):
 
    if not tickers:
        return {}

    data = yf.download(tickers, period="5d", progress=False)["Close"]

    prices = {}
    for ticker in tickers:
        try:

            series = data[ticker] if len(tickers) > 1 else data
            prices[ticker] = float(series.dropna().iloc[-1])
        except Exception:
            prices[ticker] = None  

    return prices


def get_news(ticker, max_items=3):

    try:
        news_items = yf.Ticker(ticker).news or []
    except Exception:
        news_items = []

    cleaned = []
    for item in news_items[:max_items]:
  
        content = item.get("content", item)
        cleaned.append({
            "title": content.get("title", "Untitled"),
            "publisher": content.get("provider", {}).get("displayName", "Unknown source")
                         if isinstance(content.get("provider"), dict) else "Unknown source",
            "link": content.get("canonicalUrl", {}).get("url", "#")
                    if isinstance(content.get("canonicalUrl"), dict) else item.get("link", "#"),
        })
    return cleaned
