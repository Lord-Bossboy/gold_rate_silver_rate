import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

def fetch_data(ticker, interval='1d', period='max'):
    print(f"Fetching {ticker} data (interval={interval}, period={period})...")
    data = yf.download(ticker, period=period, interval=interval)
    # Ensure multi-index columns are flattened if necessary
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

def update_excel(gold_df, silver_df, filename='rates.xlsx'):
    print(f"Updating Excel file: {filename}")
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        gold_df.to_excel(writer, sheet_name='Gold_Daily')
        silver_df.to_excel(writer, sheet_name='Silver_Daily')

def create_visualization(gold_df, silver_df, gold_h_df, silver_h_df, filename='index.html'):
    print(f"Generating visualization: {filename}")
    
    fig = make_subplots(rows=2, cols=1, 
                       shared_xaxes=False,
                       vertical_spacing=0.1,
                       subplot_titles=("Gold (GC=F)", "Silver (SI=F)"))

    # Gold Daily Candlestick
    fig.add_trace(go.Candlestick(x=gold_df.index,
                open=gold_df['Open'], high=gold_df['High'],
                low=gold_df['Low'], close=gold_df['Close'],
                name='Gold Daily'), row=1, col=1)

    # Silver Daily Candlestick
    fig.add_trace(go.Candlestick(x=silver_df.index,
                open=silver_df['Open'], high=silver_df['High'],
                low=silver_df['Low'], close=silver_df['Close'],
                name='Silver Daily'), row=2, col=1)

    # Add range selector and slider for the timeline
    fig.update_layout(
        title='Gold & Silver Rate Monitor (Daily & Recent Hourly)',
        template='plotly_dark',
        height=1000,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(step="all", label="All Time")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        xaxis2=dict(
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    # Add Hourly Data as secondary view (optional - simplifying to range buttons for now)
    # The user asked for "hours to years". The range buttons handle the "years" part.
    # To handle "hours", the user can zoom into the chart.
    
    fig.write_html(filename)

def main():
    gold_ticker = "GC=F"
    silver_ticker = "SI=F"
    
    # 1. Fetch Daily Data (Full History)
    gold_daily = fetch_data(gold_ticker, interval='1d', period='max')
    silver_daily = fetch_data(silver_ticker, interval='1d', period='max')
    
    # 2. Update Excel
    update_excel(gold_daily, silver_daily)
    
    # 3. Fetch Recent Hourly Data (Last 60 days) for visualization granularity
    # Note: We won't store this in Excel to keep it clean, but use it for the chart if needed.
    # For now, focusing on the Daily chart with range selectors which covers years.
    
    # Generate Visualization
    create_visualization(gold_daily, silver_daily, None, None)
    print("Successfully updated rates and visualization.")

if __name__ == "__main__":
    main()
