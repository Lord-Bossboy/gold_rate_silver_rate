import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime, timedelta

TICKERS = [
    "GC=F", "SI=F", "PL=F", "PA=F", "HG=F", # Futures
    "GLD", "SLV", "PPLT", "PALL", "CPER", # ETFs
    "LIT", "REMX", "BATT", "URA", "COPX", # Sector ETFs
    "SIL", "SILJ", "GDX", "GDXJ", "PICK",
    "XME", "DBB", "JJCTF", "FCX", "BHP", # Industrial/Mining
    "RIO", "VALE", "AA", "NEM", "GOLD",
    "GLNCY", "SCCO", "AEM", "WPM", "FNV",
    "KGC", "AU", "GFI", "PAAS", "SSRM",
    "CDE", "AGI", "RGLD", "SAND", "OR",
    "MP", "CLF", "X", "TECK", "HMY", 
    "EGO", "IAG"
]

def get_trend_analysis(ticker_obj):
    try:
        news = ticker_obj.news
        if news:
            return news[0].get('title', "No recent news.")
        return "Steady market activity."
    except:
        return "Market data processing."

def calculate_performance(df_daily, df_hourly):
    perf = {"1h": 0.0, "1d": 0.0, "1w": 0.0, "1m": 0.0, "1y": 0.0}
    try:
        if not df_daily.empty:
            current = df_daily['Close'].iloc[-1]
            perf["1d"] = ((current - df_daily['Close'].iloc[-2]) / df_daily['Close'].iloc[-2]) * 100 if len(df_daily) > 1 else 0
            perf["1w"] = ((current - df_daily['Close'].iloc[-5]) / df_daily['Close'].iloc[-5]) * 100 if len(df_daily) > 5 else 0
            perf["1m"] = ((current - df_daily['Close'].iloc[-21]) / df_daily['Close'].iloc[-21]) * 100 if len(df_daily) > 21 else 0
            perf["1y"] = ((current - df_daily['Close'].iloc[-252]) / df_daily['Close'].iloc[-252]) * 100 if len(df_daily) > 252 else 0
        
        if not df_hourly.empty:
            current_h = df_hourly['Close'].iloc[-1]
            perf["1h"] = ((current_h - df_hourly['Close'].iloc[-2]) / df_hourly['Close'].iloc[-2]) * 100 if len(df_hourly) > 1 else 0
    except Exception:
        pass
    return perf

def add_technical_indicators(df):
    try:
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        return df
    except:
        return df

def process_ticker(ticker):
    print(f"Processing {ticker}...")
    try:
        t_obj = yf.Ticker(ticker)
        df_daily = t_obj.history(period="max", interval="1d")
        df_hourly = t_obj.history(period="60d", interval="1h")
        
        if df_daily.empty: return None

        if isinstance(df_daily.columns, pd.MultiIndex):
            df_daily.columns = df_daily.columns.get_level_values(0)
        if isinstance(df_hourly.columns, pd.MultiIndex):
            df_hourly.columns = df_hourly.columns.get_level_values(0)

        df_daily = add_technical_indicators(df_daily)
        perf = calculate_performance(df_daily, df_hourly)
        cause = get_trend_analysis(t_obj)
        
        # Technical summary for AI
        tech_summary = {
            "SMA20": float(df_daily['SMA20'].iloc[-1]) if not pd.isna(df_daily['SMA20'].iloc[-1]) else None,
            "SMA50": float(df_daily['SMA50'].iloc[-1]) if not pd.isna(df_daily['SMA50'].iloc[-1]) else None,
            "High52w": float(df_daily['High'].iloc[-252:].max()) if len(df_daily) >= 252 else float(df_daily['High'].max()),
            "Low52w": float(df_daily['Low'].iloc[-252:].min()) if len(df_daily) >= 252 else float(df_daily['Low'].min())
        }
        
        ohlc = []
        for index, row in df_daily.iterrows():
            ohlc.append({
                "time": index.strftime('%Y-%m-%d'),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close'])
            })
        
        data = {
            "ticker": ticker,
            "name": t_obj.info.get('longName', ticker),
            "currentPrice": float(df_daily['Close'].iloc[-1]),
            "performance": perf,
            "technical": tech_summary,
            "cause": cause,
            "history": ohlc
        }
        
        with open(f"data/{ticker}.json", 'w') as f:
            json.dump(data, f)
        return data
    except Exception as e:
        print(f"Error {ticker}: {e}")
        return None

def main():
    if not os.path.exists('data'): os.makedirs('data')
    all_summaries = []
    for ticker in TICKERS:
        result = process_ticker(ticker)
        if result:
            all_summaries.append({
                "ticker": result["ticker"],
                "name": result["name"],
                "price": result["currentPrice"],
                "change1h": result["performance"]["1h"],
                "change1d": result["performance"]["1d"],
                "change1w": result["performance"]["1w"],
                "change1m": result["performance"]["1m"]
            })
    with open('data/assets.json', 'w') as f:
        json.dump(all_summaries, f)
    print("Done.")

if __name__ == "__main__":
    main()
