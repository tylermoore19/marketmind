#!/usr/bin/env python3
import sys, os
import yfinance as yf
import pandas as pd
try:
    import pandas_ta as ta
except Exception:
    ta = None
sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))

# TODO : when you are collecting stock data, need to add indicator data as well,
# but also need to add in boolean value of if QQQ/SPY is above or below EMA 8
# to show relative market strength

def get_stock_data():
    # leading_stocks = [
    #     "AAPL","AMZN","GOOGL","META","NFLX","MSFT","TSLA", # FAANG
    #     "XLE","CVX","OXY","XOM", # OIL
    #     "LCID","LI","NIO","RIVN","XPEV", # EVS
    #     "BTCUSD","CLSK","COIN","CORZ","HUT","IREN","RIOT","MARA","BTDR", # BLOCKCHAIN
    #     "XLF","GS","USB","WFC","BAC","JPM","C", # BANKS
    #     "AFRM","PYPL","UPST","XYZ", # PAYMENT PROCESSING
    #     "AXP","MA","V", # CREDIT
    #     "ARRY","ENPH","FSLR","NXT","SEDG","TAN","RUN", # SOLAR
    #     "AAL","BA","DAL","LUV","UAL", # AIRLINE
    #     "CCL","NCLH","RCL", # CRUISES
    #     "H","HLT","MAR", # HOTELS
    #     "CAT","FDX","HON","LMT","GE","RTX","UNP","UPS","WM", # INDUSTRIALS
    #     "ABBV","JNJ","LLY","UNH","VKTX","VRTX","HIMS","OSCR", # HEALTH
    #     "MRNA","NVAX","PFE", # HEALTH/VACCINE
    #     "COST","DG","DLTR","KO","KR","MO","NKE","PEP","TGT","WMT","XRT", # RETAIL
    #     "AEP","D","NEE","PEG","SO", # UTILITIES
    #     "AMAT","AMD","ARM","AVGO","DELL","IBM","INTC","MRVL","MU","NVDA","QCOM","SMCI","SMH","TSM","ALAB", # CHIPS
    #     "DKNG","FUBO","PENN", # SPORTS BETTING
    #     "ADBE","CRM","CRWD","DDOG","IGV","NOW","ORCL","PANW","SNOW","TEAM","TTWO","ZM","ZS","TWLO","U","APP","RBRK", # SOFTWARE
    #     "CART","LYFT","UBER", # DELIVERY
    #     "BABA","BIDU","FUTU","FXI","JD","PDD", # CHINA NAMES
    #     "OKLO","SMR","CEG","LEU", # NUCLEAR
    #     "ASTS","LUNR","RKLB","AVAV","ACHR", # AERODEFENSE
    #     "RDDT","LMND","W","CAVA","CELH","RBLX", # GROWTH
    #     "QS","GEV","AMPX","BE", # BATTERIES
    #     "Z","OPEN","RKT","SOFI","OPAD", # RATE SENSITIVE
    #     "AI","APLD","SOUN","PONY","BBAI", # AI
    #     "IONQ","QBTS","RGTI","QUBT","QSI", # QUANTUM
    #     "UMAC","RCAT","KTOS","AEHR", # DRONES
    #     "RR","SERV","PDYN","SYM","JOBY" # ROBOTICS
    # ]
    
    leading_stocks = [
        "AAPL","AMZN","GOOGL","META","NFLX","MSFT","TSLA", # FAANG
    ]

    # Prepare date range: explicit start Jan 1, 2015 to tomorrow
    end = (pd.Timestamp.today() + pd.Timedelta(days=1)).normalize()
    start = pd.Timestamp('2015-01-01')

    all_data = pd.DataFrame()
    successful = []
    failed = []

    for ticker in leading_stocks:
        try:
            # yfinance expects some symbols like BTC-USD instead of BTCUSD; try a few fallbacks
            yf_ticker = ticker
            if ticker.upper().endswith('USD') and 'BTC' in ticker.upper():
                yf_ticker = ticker.replace('USD', '-USD')

            print(f"Fetching {yf_ticker} from {start.date()} to {end.date()}")
            df = yf.download(yf_ticker, start=start.date(), end=end.date(), interval='1d', progress=False, auto_adjust=False)

            if df is None or df.empty:
                print(f"Failed to fetch data for {ticker}")
                failed.append(ticker)
                continue

            # Convert to tidy long format: one row per (Date, Ticker) with OHLCV columns
            try:
                if isinstance(df.columns, pd.MultiIndex):
                    # stack the ticker (or symbol) level into rows
                    try:
                        # prefer new pandas API when available to avoid FutureWarning
                        df_long = df.stack(level=-1, future_stack=True).rename_axis(['Date', 'Ticker']).reset_index()
                    except TypeError:
                        # older pandas versions don't accept future_stack kwarg
                        df_long = df.stack(level=-1).rename_axis(['Date', 'Ticker']).reset_index()
                    except Exception:
                        df_long = df.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index()
                else:
                    # single-ticker DataFrame
                    df_long = df.rename_axis('Date').reset_index()
                    df_long['Ticker'] = ticker
            except Exception as e:
                print(f"Failed to normalize data for {ticker}: {e}")
                failed.append(ticker)
                continue

            # Add indicators using pandas_ta if available
            if ta is not None:
                try:
                    # Ensure chronological order
                    if 'Date' in df_long.columns:
                        df_long = df_long.sort_values('Date')

                    close = df_long['Close']
                    # EMAs
                    df_long['EMA13'] = ta.ema(close, length=13)
                    df_long['EMA20'] = ta.ema(close, length=20)
                    df_long['EMA50'] = ta.ema(close, length=50)
                    df_long['EMA100'] = ta.ema(close, length=100)
                    df_long['EMA200'] = ta.ema(close, length=200)
                    # SMA
                    df_long['SMA50'] = ta.sma(close, length=50)
                    # RSI
                    df_long['RSI14'] = ta.rsi(close, length=14)
                    # MACD (returns dataframe with MACD, MACDh, MACDs by default names)
                    macd_df = ta.macd(close, fast=12, slow=26, signal=9)
                    if isinstance(macd_df, pd.DataFrame):
                        for col in macd_df.columns:
                            df_long[col] = macd_df[col].values
                    # ATR (needs High, Low)
                    if 'High' in df_long.columns and 'Low' in df_long.columns:
                        df_long['ATR14'] = ta.atr(df_long['High'], df_long['Low'], close, length=14)
                    # Bollinger Bands
                    bb = ta.bbands(close, length=20, std=2)
                    if isinstance(bb, pd.DataFrame):
                        for col in bb.columns:
                            df_long[col] = bb[col].values
                    # OBV
                    if 'Volume' in df_long.columns:
                        df_long['OBV'] = ta.obv(close, df_long['Volume'])
                except Exception as e:
                    print(f"Warning: failed to compute indicators for {ticker}: {e}")
            else:
                print("pandas_ta not installed; skipping indicator calculations")

            # Reorder columns: Ticker, Date, then the rest
            cols = df_long.columns.tolist()
            front = [c for c in ['Ticker', 'Date'] if c in cols]
            rest = [c for c in cols if c not in front]
            df_long = df_long[front + rest]

            # Append to the accumulating DataFrame
            all_data = pd.concat([all_data, df_long], ignore_index=True)
            successful.append(ticker)
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            failed.append(ticker)

    if all_data.empty:
        print("No data fetched for any tickers")
        return None
    
    # Ensure Date is datetime then sort by Date then Ticker
    if 'Date' in all_data.columns:
        all_data['Date'] = pd.to_datetime(all_data['Date'])
    if 'Ticker' in all_data.columns:
        all_data = all_data.sort_values(['Date', 'Ticker'])
    else:
        all_data = all_data.sort_values(['Date'])
        
    # Ensure instance directory exists
    instance_dir = os.path.join(os.path.dirname(__file__), '..', 'stocks')
    os.makedirs(instance_dir, exist_ok=True)
    out_path = os.path.join(instance_dir, 'leading_stocks_10y_daily.csv')

    # Reset index to have Ticker and Date as columns for CSV
    combined_reset = all_data.reset_index(drop=True)
    combined_reset.to_csv(out_path, index=False)

    print(f"Saved combined data for {len(successful)} tickers, failed for {len(failed)} tickers to {out_path}")
    return out_path

if __name__ == '__main__':
    get_stock_data()