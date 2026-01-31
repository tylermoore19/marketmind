#!/usr/bin/env python3
"""
Preprocess the combined leading stocks CSV into a feature dataset ready for ML.
- Loads api/instance/leading_stocks_10y_daily.csv
- Computes features: log returns, vol-normalized returns, EMA ratios, RSI14, MACD, ATR14, BBANDS, OBV
- Computes 5-day future return and label (thresholds configurable)
- Fits per-ticker StandardScaler on selected features and saves scalers
- Computes cross-sectional z-scores for selected features per date
- Saves processed dataset to api/instance/processed_leading_stocks.parquet
- Saves scalers to api/instance/scalers/ (joblib)

Usage: python api/stocks/preprocess.py
"""

import os
import sys
import argparse
from pathlib import Path
import joblib

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
INSTANCE = ROOT.parent / 'stocks'
RAW_CSV = INSTANCE / 'leading_stocks_10y_daily.csv'
OUT_PARQUET = INSTANCE / 'processed_leading_stocks.parquet'
SCALER_DIR = INSTANCE / 'scalers'
SCALER_DIR.mkdir(parents=True, exist_ok=True)

# Config
FUTURE_DAYS = 5
UPPER_THRESH = 0.03
LOWER_THRESH = -0.03
ROLL_VOL = 20

FEATURES_TO_SCALE = [
    'logret', 'ret_vol_norm',
    'EMA13_diff_pct', 'EMA20_diff_pct', 'EMA50_diff_pct', 'EMA100_diff_pct', 'EMA200_diff_pct',
    'RSI14', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9',
    'ATR14_pct', 'BBP_20_2.0_2.0', 'log_vol', 'OBV'
]

CS_FEATURES = ['ret_vol_norm', 'EMA20_diff_pct', 'RSI14']


# indicators are expected to already exist in the CSV; we will normalize them below


def build_features(df):
    # df = full dataframe (Ticker, Date, Close, High, Low, Open, Volume, ...)
    df = df.sort_values(['Ticker', 'Date']).copy()

    # log returns per ticker
    df['logret'] = df.groupby('Ticker')['Close'].apply(lambda x: np.log(x).diff())

    # rolling vol (20d)
    df['vol20'] = df.groupby('Ticker')['logret'].transform(lambda x: x.rolling(ROLL_VOL, min_periods=5).std())
    df['ret_vol_norm'] = df['logret'] / df['vol20']

    # indicators expected in CSV: compute normalized versions for ML
    # EMA percent differences
    for e in [13, 20, 50, 100, 200]:
        ema_col = f'EMA{e}'
        out_col = f'EMA{e}_diff_pct'
        if ema_col in df.columns:
            df[out_col] = (df['Close'] - df[ema_col]) / df[ema_col]

    # ATR percent
    if 'ATR14' in df.columns:
        df['ATR14_pct'] = df['ATR14'] / df['Close']

    # log volume
    if 'Volume' in df.columns:
        df['log_vol'] = np.log1p(df['Volume'])

    # future return and label (triple barrier simplified)
    df['future_return'] = df.groupby('Ticker')['Close'].apply(lambda s: s.shift(-FUTURE_DAYS) / s - 1)
    df['label'] = np.where(df['future_return'] > UPPER_THRESH, 1,
                   np.where(df['future_return'] < LOWER_THRESH, -1, 0))

    # drop rows near the end where future_return is NA
    df = df[~df['future_return'].isna()].copy()

    return df


def fit_and_save_scalers(df, features, out_dir):
    scalers = {}
    for ticker, g in df.groupby('Ticker'):
        scaler = StandardScaler()
        sub = g[features].fillna(0)
        try:
            scaler.fit(sub)
            scalers[ticker] = scaler
            joblib.dump(scaler, out_dir / f"scaler_{ticker}.pkl")
        except Exception as e:
            print(f'warning: failed to fit scaler for {ticker}: {e}')
    return scalers


def add_cross_sectional_zscores(df, features):
    for f in features:
        if f in df.columns:
            df[f + '_cs_z'] = df.groupby('Date')[f].transform(lambda x: (x - x.mean()) / x.std(ddof=0))
    return df


def main(args):
    if not RAW_CSV.exists():
        print(f'raw CSV not found at {RAW_CSV}. Run get_stock_data first.')
        return 1

    df = pd.read_csv(RAW_CSV, parse_dates=['Date'])
    print('Loaded rows:', len(df))

    df = build_features(df)
    print('After feature build rows:', len(df))

    # save intermediate
    df.to_parquet(OUT_PARQUET, index=False)

    # fit per-ticker scalers for selected features
    features_for_scaler = [f for f in FEATURES_TO_SCALE if f in df.columns]
    fit_and_save_scalers(df, features_for_scaler, SCALER_DIR)

    # add cross-sectional z-scores
    df = add_cross_sectional_zscores(df, CS_FEATURES)

    # final save
    df.to_parquet(OUT_PARQUET, index=False)
    print('Saved processed dataset to', OUT_PARQUET)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', default=str(RAW_CSV))
    parser.add_argument('--out', default=str(OUT_PARQUET))
    parser.add_argument('--scaler-dir', default=str(SCALER_DIR))
    ns = parser.parse_args()
    sys.exit(main(ns))
