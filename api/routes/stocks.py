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
def fetch_stock_data(tickers, days=90, interval='1d', direction='bullish'):
    matched = []
    
    logger.info(f"------------ Finding trending stocks in {direction} direction ------------")
    
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

            # compute indicators: ema_13, ema_45, rsi_14 (on Close), ma_10 (on Volume)
            if ta is not None:
                try:
                    if 'Close' in df_long.columns:
                        df_long['ema_13'] = ta.ema(df_long['Close'], length=13)
                        df_long['ema_45'] = ta.ema(df_long['Close'], length=45)
                        df_long['rsi_14'] = ta.rsi(df_long['Close'], length=14)
                    if 'Volume' in df_long.columns:
                        df_long['ma_10'] = ta.sma(df_long['Volume'], length=10)
                except Exception as e:
                    logger.warning(f'warning: pandas_ta failed for {t}: {e}')

            # apply filter:
            # Parameterize the small differences between bullish and bearish checks so the main flow is shared.
            # For bullish: tail Open/Close > ema_45, ema_13 crossed above ema_45 before tail, RSI crossed above 50 recently -> label 'Buy'
            # For bearish: tail Open/Close < ema_45, ema_13 crossed below ema_45 before tail, RSI crossed below 50 recently -> label 'Sell'
            try:
                check_window = 45
                if 'ema_45' in df_long.columns and 'Open' in df_long.columns and 'Close' in df_long.columns:
                    tail = df_long.tail(check_window)
                    if len(tail) < check_window:
                        logger.info(f'{t} filtered out: insufficient history ({len(tail)} < {check_window})')
                        continue
                    # if any NaNs in required cols in the tail, filter out
                    if tail[['ema_45', 'Open', 'Close']].isna().any().any():
                        logger.info(f'{t} filtered out: NaNs present in last {check_window} rows')
                        continue

                    # set up comparison lambdas and labels based on direction
                    if direction == 'bullish':
                        tail_cmp = lambda a, b: (a > b).all()
                        cross_cmp = lambda df: (df['ema_13'] > df['ema_45'])
                        rsi_check_fn = lambda rsi: (rsi > 50) & (rsi.shift(1) <= 50)
                        signal_label = 'Buy'
                    elif direction == 'bearish':
                        tail_cmp = lambda a, b: (a < b).all()
                        cross_cmp = lambda df: (df['ema_13'] < df['ema_45'])
                        rsi_check_fn = lambda rsi: (rsi < 50) & (rsi.shift(1) >= 50)
                        signal_label = 'Sell'
                    else:
                        logger.info(f'Unknown direction parameter: {direction} for {t}, skipping')
                        continue

                    # validate tail price relation to ema_45
                    if not (tail_cmp(tail['Open'], tail['ema_45']) and tail_cmp(tail['Close'], tail['ema_45'])):
                        logger.info(f"{t} filtered out: tail price vs ema_45 check failed")
                        continue

                    # check ema_13 crossing occurred more than check_window days ago
                    if 'ema_13' in df_long.columns:
                        try:
                            cross = cross_cmp(df_long)
                            true_pos = np.flatnonzero(cross.values)
                            if true_pos.size == 0:
                                logger.info(f'{t} filtered out: ema_13 never satisfied cross condition')
                                continue
                            first_true = int(true_pos[0])
                            tail_start_pos = len(df_long) - check_window
                            if first_true <= tail_start_pos - 1:
                                # compute volume boolean (do not gate on it)
                                last_row = df_long.iloc[-1]
                                vol_bool = False
                                if 'ma_10' in df_long.columns and 'Volume' in df_long.columns:
                                    try:
                                        vol_bool = bool(last_row['Volume'] > last_row['ma_10'])
                                    except Exception:
                                        vol_bool = False
                                else:
                                    vol_bool = False

                                # RSI cross: must have the appropriate crossing in last 2 days
                                if 'rsi_14' in df_long.columns:
                                    rsi = df_long['rsi_14']
                                    if rsi_check_fn(rsi).tail(2).any():
                                        try:
                                            latest_vol = int(last_row['Volume']) if 'Volume' in last_row.index and not pd.isna(last_row['Volume']) else None
                                        except Exception:
                                            latest_vol = None
                                        matched.append({"ticker": t, "buy_signal": signal_label if vol_bool else "Wait", "volume": latest_vol})
                                    else:
                                        logger.info(f"{t} filtered out: RSI did not perform required crossing in last 4 days")
                                        continue
                                else:
                                    logger.info(f"{t} filtered out: missing rsi_14 for RSI check")
                                    continue
                            else:
                                logger.info(f"{t} filtered out: ema_13 crossing happened only {len(df_long)-first_true} days ago")
                                continue
                        except Exception as e:
                            logger.exception(f'error evaluating ema_13 crossover for {t} (direction={direction}): {e}')
                            continue
                    else:
                        logger.info(f'{t} filtered out: missing ema_13 for crossover check')
                        continue
            except Exception as e:
                logger.exception(f'error applying ema_45 filter for {t}: {e}')
        except Exception as e:
            logger.exception(f'error downloading {t}: {e}')

    # sort matched: prefer primary signal_label (Buy or Sell) first, then by volume descending (treat None as -1)
    try:
        preferred = 'Buy' if direction == 'bullish' else 'Sell'

        def sort_key(x):
            sig = x.get('buy_signal')
            rank = 0 if sig == preferred else 1
            vol = x.get('volume') if x.get('volume') is not None else -1
            return (rank, -vol)

        matched.sort(key=sort_key)
    except Exception:
        # fallback: leave unsorted if any unexpected structure
        pass

    return matched

def fetch_stock_data2(tickers, days=90, interval='1d', direction='bullish'):
    matched = []
    
    logger.info(f"------------ Finding trending stocks in {direction} direction ------------")
    
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

            # compute indicators: ema_13, ema_45, rsi_14 (on Close), ma_10 (on Volume)
            if ta is not None:
                try:
                    if 'Close' in df_long.columns:
                        df_long['ema_13'] = ta.ema(df_long['Close'], length=13)
                        df_long['ema_45'] = ta.ema(df_long['Close'], length=45)
                        df_long['rsi_14'] = ta.rsi(df_long['Close'], length=14)
                    if 'Volume' in df_long.columns:
                        df_long['ma_10'] = ta.sma(df_long['Volume'], length=10)
                except Exception as e:
                    logger.warning(f'warning: pandas_ta failed for {t}: {e}')

            # Apply RSI reversal + candle + volume rule specifically for fetch_stock_data2
            try:
                # minimal history: need at least 7 days to compute 5-day avg (previous 5 days) + prev + today
                if len(df_long) < 7:
                    logger.info(f'{t} filtered out: insufficient history for RSI/volume check ({len(df_long)} < 7)')
                    continue

                # required columns
                required_cols = ['rsi_14', 'Open', 'Close', 'Volume']
                if not all(col in df_long.columns for col in required_cols):
                    logger.info(f"{t} filtered out: missing required cols for RSI/volume rule: {required_cols}")
                    continue

                # work with the last several rows
                rsi = df_long['rsi_14'].reset_index(drop=True)
                vol = df_long['Volume'].reset_index(drop=True)

                # indexes: -1 = today, -2 = previous day, -3 = day before previous
                try:
                    rsi_today = float(rsi.iloc[-1])
                    rsi_prev = float(rsi.iloc[-2])
                    rsi_prev_prev = float(rsi.iloc[-3])
                except Exception:
                    logger.info(f"{t} filtered out: insufficient RSI history or NaNs")
                    continue

                # check previous day RSI went down and today it goes up
                prev_went_down = rsi_prev < rsi_prev_prev
                today_went_up = rsi_today > rsi_prev

                # require previous RSI to be below 55
                if not (rsi_prev < 55 and prev_went_down and today_went_up):
                    logger.info(f"{t} filtered out: RSI reversal condition not met (rsi_prev={rsi_prev}, rsi_today={rsi_today})")
                    continue

                # candle condition: today's close > previous day's open
                try:
                    close_today = float(df_long.iloc[-1]['Close'])
                    prev_open = float(df_long.iloc[-2]['Open'])
                except Exception:
                    logger.info(f"{t} filtered out: missing Open/Close values for candle check")
                    continue

                if not (close_today > prev_open):
                    logger.info(f"{t} filtered out: candle condition failed (close_today={close_today} <= prev_open={prev_open})")
                    continue

                # sustained EMA requirement: require ema_13 > ema_45 for at least the last 25 days
                # This ensures the shorter-term trend has been consistently above the longer-term trend
                try:
                    if 'ema_13' not in df_long.columns or 'ema_45' not in df_long.columns:
                        logger.info(f"{t} filtered out: missing ema_13/ema_45 for sustained EMA check")
                        continue

                    # Look at the last 20 days (excluding any NaNs). If there are fewer than 20 valid rows, reject.
                    ema_check_window = 20
                    tail_ema = df_long[['ema_13', 'ema_45']].tail(ema_check_window)
                    if len(tail_ema) < ema_check_window or tail_ema.isna().any().any():
                        logger.info(f"{t} filtered out: insufficient EMA history for sustained EMA check ({len(tail_ema)} < {ema_check_window})")
                        continue

                    # All of the last ema_check_window rows must satisfy ema_13 > ema_45
                    ema_sustained = (tail_ema['ema_13'] > tail_ema['ema_45']).all()
                    if not ema_sustained:
                        logger.info(f"{t} filtered out: sustained EMA condition failed (ema_13 not > ema_45 for last {ema_check_window} days)")
                        continue
                except Exception as e:
                    logger.exception(f'error evaluating sustained EMA requirement for {t}: {e}')
                    continue

                # volume condition: today's volume > average of previous 5 days (exclude today)
                try:
                    vol_today = float(vol.iloc[-1])
                    # prefer the computed ma_10 column if present (use previous day's ma_10)
                    if 'ma_10' in df_long.columns and not pd.isna(df_long['ma_10'].iloc[-2]):
                        prev5_avg = float(df_long['ma_10'].iloc[-2])
                    else:
                        prev5_avg = float(vol.iloc[-6:-1].mean())
                except Exception:
                    logger.info(f"{t} filtered out: error computing average volume")
                    continue

                if not (vol_today > prev5_avg):
                    logger.info(f"{t} filtered out: volume condition failed (vol_today={vol_today} <= prev5_avg={prev5_avg})")
                    continue

                # passed all checks — add to matched
                matched.append({
                    "ticker": t,
                    "reason": "rsi_reversal_candle_volume",
                    "rsi_prev": rsi_prev,
                    "rsi_today": rsi_today,
                    "close_today": close_today,
                    "prev_open": prev_open,
                    "volume_today": int(vol_today),
                    "avg_prev5_volume": int(prev5_avg)
                })
            except Exception as e:
                logger.exception(f'error applying RSI/candle/volume rule for {t}: {e}')
        except Exception as e:
            logger.exception(f'error downloading {t}: {e}')

    # sort matched: prefer primary signal_label (Buy or Sell) first, then by volume descending (treat None as -1)
    try:
        preferred = 'Buy' if direction == 'bullish' else 'Sell'

        def sort_key(x):
            sig = x.get('buy_signal')
            rank = 0 if sig == preferred else 1
            vol = x.get('volume') if x.get('volume') is not None else -1
            return (rank, -vol)

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
            .limit(100)  # pull a large candidate set
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
        matched = fetch_stock_data2(bullish_stocks, days=90, interval='1d', direction='bullish')

        # print('\n----------------------------')
        # print('matched tickers count:', len(matched))
        # print(matched)

        return jsonify(ok_response(matched)), 200
    except Exception as e:
        logger.exception(f'Unexpected error: {e}')
        return jsonify(error_response('Failed to fetch bullish stocks', 'fetch_error')), 500
    
@stocks_bp.route('/bearish', methods=['GET'])
@jwt_required()
def get_bearish_stocks():
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
                col('EMA50') > col('close'),                  # EMA50 > Price
                col('EMA30') > col('close'),                  # EMA30 > Price
                col('EMA50') > col('EMA30'),                  # EMA50 > EMA30
                col('ADRP') >= 2,                             # ADR >= 2%
                col('average_volume_10d_calc') > 1_000_000,   # Avg Volume 10D
                col('RSI') > 45                               # RSI > 45
            )
            .limit(100)  # pull a large candidate set
        )

        # Step 2: fetch results
        _, df = q.get_scanner_data() or []

        # Step 3: sort by volume descending
        bearish_df = df.sort_values('volume', ascending=False)

        # pd.set_option('display.max_rows', None) # print all rows

        # Step 4: merge with leading stocks list (make a list of names, bearish first, preserve order)
        bearish_stocks = list(bearish_df['name'].astype(str).values)
        # bearish_stocks = bearish_stocks + [s for s in leading_stocks if s not in bearish_stocks]

        # fetch recent data for all merged bearish tickers (returns list of matched tickers)
        matched = fetch_stock_data2(bearish_stocks, days=90, interval='1d', direction='bearish')

        # print('\n----------------------------')
        # print('matched tickers count:', len(matched))
        # print(matched)

        return jsonify(ok_response(matched)), 200
    except Exception as e:
        logger.exception(f'Unexpected error: {e}')
        return jsonify(error_response('Failed to fetch bearish stocks', 'fetch_error')), 500

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