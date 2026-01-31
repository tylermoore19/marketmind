#!/usr/bin/env python3
import sys, os
import yfinance as yf
import pandas as pd
from tradingview_screener import Query, col
sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from clients.GeminiClient import GeminiClient

# TODO : when you are collecting stock data, need to add indicator data as well,
# but also need to add in boolean value of if QQQ/SPY is above or below EMA 8
# to show relative market strength

def find_stocks():
    gemini_client = GeminiClient()
        
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
    # df_filtered = df[((df['High.1M'] - df['high']) / df['high'] <= 0.03)]

    # Step 4: sort by volume descending, take top 30
    top_stocks = df.sort_values('volume', ascending=False).head(30)
    
    pd.set_option('display.max_rows', None) # print all rows
    
    print('Top Stocks:')
    print(top_stocks[['name', 'change', 'close', 'volume', 'high', 'High.1M', 'relative_volume_10d_calc']])
    
    leading_stocks = [
        "AAPL","AMZN","GOOGL","META","NFLX","MSFT","TSLA", # FAANG
        "XLE","CVX","OXY","XOM", # OIL
        "LCID","LI","NIO","RIVN","XPEV", # EVS
        "BTCUSD","CLSK","COIN","CORZ","HUT","IREN","RIOT","MARA","BTDR", # BLOCKCHAIN
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
    
    swaggy_stocks = gemini_client.get_swaggy_stocks()
    # print("\nSwaggy Stocks Results:")
    # print(swaggy_stocks)
    
    stocks = list(set(list(top_stocks['name']) + leading_stocks + swaggy_stocks))
    print("Combined stocks list:")
    print(stocks)

if __name__ == '__main__':
    find_stocks()