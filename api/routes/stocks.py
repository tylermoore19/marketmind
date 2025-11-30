from clients.GeminiClient import GeminiClientError
from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required
from tradingview_screener import Query, col
from utils.helpers import error_response, ok_response
from google import genai
from datetime import date
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
from app import logger

stocks_bp = Blueprint('stocks', __name__)

leading_stocks = [
    "AAPL","AMZN","GOOGL","META","NFLX","MSFT","TSLA", # FAANG
    "XLE","CVX","OXY","XOM", # OIL
    "LCID","LI","NIO","RIVN","XPEV", # EVS
    # "BTCUSD","CLSK","COIN","CORZ","HUT","IREN","RIOT","MARA","BTDR", # BLOCKCHAIN
    "CLSK","COIN","CORZ","HUT","IREN","RIOT","MARA","BTDR", # BLOCKCHAIN
    "XLF","GS","USB","WFC","BAC","JPM","C", # BANKS
    "AFRM","PYPL","UPST","XYZ", # PAYMENT PROCESSING
    "AXP","MA","V", # CREDIT
    "ARRY","ENPH","FSLR","NXT","SEDG","TAN","RUN", # SOLAR
    "AAL","BA","DAL","LUV","UAL", # AIRLINE
    "CCL","NCLH","RCL", # CRUISES
    "H","HLT","MAR", # HOTELS
    "CAT","FDX","HON","LMT","GE","RTX","UNP","UPS","WM", # INDUSTRIALS
    "ABBV","JNJ","LLY","UNH","VKTX","VRTX","HIMS","OSCR", # HEALTH
    "MRNA","NVAX","PFE", # HEALTH/VACCINE
    "COST","DG","DLTR","KO","KR","MO","NKE","PEP","TGT","WMT","XRT", # RETAIL
    "AEP","D","NEE","PEG","SO", # UTILITIES
    "AMAT","AMD","ARM","AVGO","DELL","IBM","INTC","MRVL","MU","NVDA","QCOM","SMCI","SMH","TSM","ALAB", # CHIPS
    "DKNG","FUBO","PENN", # SPORTS BETTING
    "ADBE","CRM","CRWD","DDOG","IGV","NOW","ORCL","PANW","SNOW","TEAM","TTWO","ZM","ZS","TWLO","U","APP","RBRK", # SOFTWARE
    "CART","LYFT","UBER", # DELIVERY
    "BABA","BIDU","FUTU","FXI","JD","PDD", # CHINA NAMES
    "OKLO","SMR","CEG","LEU", # NUCLEAR
    "ASTS","LUNR","RKLB","AVAV","ACHR", # AERODEFENSE
    "RDDT","LMND","W","CAVA","CELH","RBLX", # GROWTH
    "QS","GEV","AMPX","BE", # BATTERIES
    "Z","OPEN","RKT","SOFI","OPAD", # RATE SENSITIVE
    "AI","APLD","SOUN","PONY","BBAI", # AI
    "IONQ","QBTS","RGTI","QUBT","QSI", # QUANTUM
    "UMAC","RCAT","KTOS","AEHR", # DRONES
    "RR","SERV","PDYN","SYM","JOBY" # ROBOTICS
]

# helper: download data for tickers and return a concatenated DataFrame
def fetch_stock_data(tickers, days=90, interval='1d'):
    matched = []
    for t in tickers:
        try:
            df_t = yf.download(t, period=f"{days}d", interval=interval, auto_adjust=False, progress=False)
            if df_t is None or df_t.empty:
                logger.info(f'no data for {t}')
                continue

            # Normalize MultiIndex outputs (yfinance can return MultiIndex when multiple tickers or adjustments)
            try:
                if isinstance(df_t.columns, pd.MultiIndex):
                    try:
                        df_long = df_t.stack(level=-1, future_stack=True).rename_axis(['Date', 'Ticker']).reset_index()
                    except TypeError:
                        df_long = df_t.stack(level=-1).rename_axis(['Date', 'Ticker']).reset_index()
                    except Exception:
                        df_long = df_t.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index()
                else:
                    df_long = df_t.rename_axis('Date').reset_index()
                    df_long['Ticker'] = t
            except Exception as e:
                logger.exception(f'failed to normalize yfinance output for {t}: {e}')
                continue

            # ensure Date column exists and is datetime
            if 'Date' in df_long.columns:
                df_long['Date'] = pd.to_datetime(df_long['Date'])

            # compute indicators: ema_13, ema_45, rsi_14 (on Close), ma_20 (on Volume)
            if ta is not None:
                try:
                    if 'Close' in df_long.columns:
                        df_long['ema_13'] = ta.ema(df_long['Close'], length=13)
                        df_long['ema_45'] = ta.ema(df_long['Close'], length=45)
                        df_long['rsi_14'] = ta.rsi(df_long['Close'], length=14)
                    if 'Volume' in df_long.columns:
                        df_long['ma_20'] = ta.sma(df_long['Volume'], length=20)
                except Exception as e:
                    logger.warning(f'warning: pandas_ta failed for {t}: {e}')

            # apply filter: require last 30 days Open and Close > ema_45 (no NaNs), and ema_13 crossed above ema_45 > check_window days ago
            try:
                check_window = 30
                if 'ema_45' in df_long.columns and 'Open' in df_long.columns and 'Close' in df_long.columns:
                    tail = df_long.tail(check_window)
                    if len(tail) < check_window:
                        logger.info(f'{t} filtered out: insufficient history ({len(tail)} < {check_window})')
                        continue
                    # if any NaNs in required cols in the tail, filter out
                    if tail[['ema_45', 'Open', 'Close']].isna().any().any():
                        logger.info(f'{t} filtered out: NaNs present in last {check_window} rows')
                        continue

                    if not ((tail['Open'] > tail['ema_45']).all() and (tail['Close'] > tail['ema_45']).all()):
                        logger.info(f'{t} filtered out: not above ema_45 for last {check_window} days')
                        continue

                    # check ema_13 crossover happened more than `check_window` days ago
                    if 'ema_13' in df_long.columns:
                        try:
                            cross = (df_long['ema_13'] > df_long['ema_45'])
                            true_pos = np.flatnonzero(cross.values)
                            if true_pos.size == 0:
                                logger.info(f'{t} filtered out: ema_13 never above ema_45')
                                continue
                            first_true = int(true_pos[0])
                            tail_start_pos = len(df_long) - check_window
                            # require the first True to be strictly before the tail window
                            if first_true <= tail_start_pos - 1:
                                # compute volume boolean (do not gate on it)
                                last_row = df_long.iloc[-1]
                                vol_bool = False
                                if 'ma_20' in df_long.columns and 'Volume' in df_long.columns:
                                    try:
                                        vol_bool = bool(last_row['Volume'] > last_row['ma_20'])
                                    except Exception:
                                        vol_bool = False
                                else:
                                    # missing data, keep vol_bool False
                                    vol_bool = False

                                # RSI cross: must have crossed above 50 in last 4 days to be included
                                if 'rsi_14' in df_long.columns:
                                    rsi = df_long['rsi_14']
                                    cross_up = (rsi > 50) & (rsi.shift(1) <= 50)
                                    if cross_up.tail(4).any():
                                        # include latest volume value
                                        try:
                                            latest_vol = int(last_row['Volume']) if 'Volume' in last_row.index and not pd.isna(last_row['Volume']) else None
                                        except Exception:
                                            latest_vol = None
                                        matched.append({"ticker": t, "buy_signal": "Buy" if vol_bool else "Wait", "volume": latest_vol})
                                    else:
                                        logger.info(f"{t} filtered out: RSI did not cross above 50 in last 3 days")
                                        continue
                                else:
                                    logger.info(f"{t} filtered out: missing rsi_14 for RSI check")
                                    continue
                            else:
                                logger.info(f"{t} filtered out: ema_13 crossed above ema_45 only {len(df_long)-first_true} days ago")
                                continue
                        except Exception as e:
                            logger.exception(f'error evaluating ema_13 crossover for {t}: {e}')
                            continue
            except Exception as e:
                logger.exception(f'error applying ema_45 filter for {t}: {e}')
        except Exception as e:
            logger.exception(f'error downloading {t}: {e}')

    # sort matched: buy_signal 'Buy' first, then by volume descending (treat None as -1)
    try:
        def sort_key(x):
            # buy_signal priority: 'Buy' should come first
            buy = x.get('buy_signal')
            buy_rank = 0 if buy == 'Buy' else 1
            vol = x.get('volume') if x.get('volume') is not None else -1
            return (buy_rank, -vol)

        matched.sort(key=sort_key)
    except Exception:
        # fallback: leave unsorted if any unexpected structure
        pass

    return matched


# TODO : maybe try to adjust this so close is -3% <= 1 month high <= +3%

@stocks_bp.route('/top', methods=['GET'])
@jwt_required()
def get_top_stocks():
    try:
        # Step 1: build query
        q = (
            Query()
            .select(
                'name', 'close', 'volume', 'high', 'High.1M',
                'EMA50', 'EMA20', 'ADRP', 'relative_volume_10d_calc',
                'average_volume_10d_calc', 'change', 'market_cap_basic'
            )
            .where(
                col('close').between(3, 150),                # Price
                col('change') > 1,                          # Change > 1%
                col('market_cap_basic') >= 300_000_000,     # Market Cap >= 300M
                col('EMA50') < col('close'),                # EMA50 < Price
                col('EMA20') < col('close'),                # EMA20 < Price
                col('ADRP') >= 2,     # ADR >= 2%
                col('average_volume_10d_calc') > 2_000_000,   # Avg Volume 10D
                # col('High.1M') >= col('high'),              # High 1M higher than or equal 1D High
                col('relative_volume_10d_calc') > 1         # Relative volume > 1
            )
            .limit(1000)  # pull a large candidate set
        )

        # Step 2: fetch results
        _, df = q.get_scanner_data() or []

        # Step 3: filter 1-month high ≤ 3% above 1-day high
        # df_filtered = df[(df['High.1M'] > df['high']) & ((df['High.1M'] - df['high']) / df['high'] <= 0.05)]
        df_filtered = df[((df['High.1M'] - df['high']) / df['high'] <= 0.03)]

        # Step 4: sort by volume descending, take top 30
        top_stocks = df.sort_values('volume', ascending=False).head(30)

        pd.set_option('display.max_rows', None) # print all rows

        print(top_stocks[['name', 'change', 'close', 'volume', 'high', 'High.1M', 'relative_volume_10d_calc']])

        return jsonify(ok_response(top_stocks.to_dict(orient='records'))), 200
        # raise Exception("Simulated error for testing")
    except Exception as e:
        logger.exception(f'Unexpected error: {e}')
        return jsonify(error_response('Failed to fetch top stocks', 'fetch_error')), 500

@stocks_bp.route('/bullish', methods=['GET'])
@jwt_required()
def get_bullish_stocks():
    try:
        # Step 1: build query
        q = (
            Query()
            .select(
                'name', 'close', 'volume', 'EMA50', 'EMA30', 'ADRP',
                'average_volume_10d_calc', 'market_cap_basic', 'RSI'
            )
            .where(
                col('close').between(3, 100),                 # Price
                col('market_cap_basic') >= 300_000_000,       # Market Cap >= 300M
                col('EMA50') < col('close'),                  # EMA50 < Price
                col('EMA30') < col('close'),                  # EMA30 < Price
                col('EMA50') < col('EMA30'),                  # EMA50 < EMA30
                col('ADRP') >= 2,                             # ADR >= 2%
                col('average_volume_10d_calc') > 1_000_000,   # Avg Volume 10D
                col('RSI') < 55                               # RSI < 55
            )
            .limit(1000)  # pull a large candidate set
        )

        # Step 2: fetch results
        _, df = q.get_scanner_data() or []

        # Step 3: sort by volume descending
        bullish_df = df.sort_values('volume', ascending=False)

        # pd.set_option('display.max_rows', None) # print all rows

        # Step 4: merge with leading stocks list (make a list of names, bullish first, preserve order)
        bullish_stocks = list(bullish_df['name'].astype(str).values)
        # bullish_stocks = bullish_stocks + [s for s in leading_stocks if s not in bullish_stocks]

        # fetch recent data for all merged bullish tickers (returns list of matched tickers)
        matched = fetch_stock_data(bullish_stocks, days=90, interval='1d')

        # print('\n----------------------------')
        # print('matched tickers count:', len(matched))
        # print(matched)

        return jsonify(ok_response(matched)), 200
    except Exception as e:
        logger.exception(f'Unexpected error: {e}')
        return jsonify(error_response('Failed to fetch bullish stocks', 'fetch_error')), 500

@stocks_bp.route('/up-trend', methods=['GET'])
@jwt_required()
def get_up_trend_stocks():
    try:
        # Step 1: build query
        q = (
            Query()
            .select(
                'name', 'close', 'volume', 'high', 'High.1M',
                'EMA50', 'EMA20', 'ADRP', 'relative_volume_10d_calc',
                'average_volume_10d_calc', 'change', 'market_cap_basic'
            )
            .where(
                col('close').between(3, 150),                # Price
                col('change') > 1,                          # Change > 1%
                col('market_cap_basic') >= 300_000_000,     # Market Cap >= 300M
                col('EMA50') < col('close'),                # EMA50 < Price
                col('EMA20') < col('close'),                # EMA20 < Price
                col('ADRP') >= 2,     # ADR >= 2%
                col('average_volume_10d_calc') > 2_000_000,   # Avg Volume 10D
                # col('High.1M') >= col('high'),              # High 1M higher than or equal 1D High
                col('relative_volume_10d_calc') > 1         # Relative volume > 1
            )
            .limit(1000)  # pull a large candidate set
        )

        # Step 2: fetch results
        _, df = q.get_scanner_data() or []

        # Step 3: filter 1-month high ≤ 3% above 1-day high
        df_filtered = df[((df['High.1M'] - df['high']) / df['high'] <= 0.03)]

        # Step 4: sort by volume descending, take top 30
        top_stocks = df.sort_values('volume', ascending=False).head(30)

        pd.set_option('display.max_rows', None) # print all rows

        print(top_stocks[['name', 'change', 'close', 'volume', 'high', 'High.1M', 'relative_volume_10d_calc']])

        return jsonify(ok_response(top_stocks.to_dict(orient='records'))), 200
    except Exception as e:
        logger.exception(f'Unexpected error: {e}')
        return jsonify(error_response('Failed to fetch up trend stocks', 'fetch_error')), 500