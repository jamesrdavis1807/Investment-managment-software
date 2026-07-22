

import streamlit as st
import pandas as pd
import plotly.express as px

from data import load_portfolio, get_current_prices, get_news

st.set_page_config(page_title="My Investment Dashboard", layout="wide")
st.title("Investment Dashboard")
portfolio = load_portfolio("portfolio.csv")

if st.button("🔄 Refresh prices"):
    st.cache_data.clear()

@st.cache_data(ttl=300) 
def cached_prices(tickers):
    return get_current_prices(tickers)

prices = cached_prices(portfolio["ticker"].tolist())
portfolio["current_price"] = portfolio["ticker"].map(prices)

portfolio["market_value"] = portfolio["shares"] * portfolio["current_price"]
portfolio["cost_total"] = portfolio["shares"] * portfolio["cost_basis"]
portfolio["gain_loss"] = portfolio["market_value"] - portfolio["cost_total"]
portfolio["gain_loss_pct"] = (portfolio["gain_loss"] / portfolio["cost_total"]) * 100

total_value = portfolio["market_value"].sum()
total_cost = portfolio["cost_total"].sum()
total_gain = total_value - total_cost
total_gain_pct = (total_gain / total_cost * 100) if total_cost else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Value", f"${total_value:,.2f}")
col2.metric("Total Cost Basis", f"${total_cost:,.2f}")
col3.metric("Total Gain/Loss", f"${total_gain:,.2f}", f"{total_gain_pct:.1f}%")

st.divider()

left, right = st.columns([2, 1])

with left:
    st.subheader("Holdings")
    display_df = portfolio[[
        "ticker", "shares", "cost_basis", "current_price",
        "market_value", "gain_loss", "gain_loss_pct"
    ]].round(2)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with right:
    st.subheader("Allocation")
    fig = px.pie(portfolio, values="market_value", names="ticker", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("📰 Recent News")
for ticker in portfolio["ticker"]:
    with st.expander(f"{ticker} news"):
        items = get_news(ticker)
        if not items:
            st.write("No recent news found.")
        for item in items:
            st.markdown(f"**[{item['title']}]({item['link']})**  \n*{item['publisher']}*")
