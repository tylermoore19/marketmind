#!/usr/bin/env python3
"""
Train a simple classifier on the processed stocks dataset.
- Loads api/instance/processed_leading_stocks.parquet
- Uses CS z-score columns if present, otherwise scaled/raw features
- Splits by time (train/val/test)
- Trains a RandomForestClassifier (default)
- Saves model to api/instance/models/
- Prints evaluation metrics (classification report & confusion matrix counts)

Usage: python api/stocks/train.py
"""

from pathlib import Path
import argparse
import joblib
import json

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent
INSTANCE = ROOT.parent / 'instance'
PROCESSED = INSTANCE / 'processed_leading_stocks.parquet'
MODELDIR = INSTANCE / 'models'
MODELDIR.mkdir(parents=True, exist_ok=True)

# Basic split dates (can be CLI args)
TRAIN_END = '2021-12-31'
VAL_END = '2023-12-31'

LABEL_COL = 'label'

def pick_features(df):
    # prefer cross-sectional z (suffix _cs_z) for features, fall back to _scaled or raw
    candidates = []
    for f in [
        'ret_vol_norm',
        'EMA20_diff_pct',
        'RSI14',
        'MACD_12_26_9',
        'ATR14_pct',
        'log_vol',
    ]:
        cs = f + '_cs_z'
        sc = f + '_scaled'
        if cs in df.columns:
            candidates.append(cs)
        elif sc in df.columns:
            candidates.append(sc)
        elif f in df.columns:
            candidates.append(f)
    return candidates


def load_data(path=PROCESSED):
    if not Path(path).exists():
        raise FileNotFoundError(f'Processed dataset not found at {path}. Run preprocess first.')
    df = pd.read_parquet(path)
    df = df.sort_values(['Date', 'Ticker']).copy()
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def split_by_date(df):
    train = df[df['Date'] <= TRAIN_END]
    val = df[(df['Date'] > TRAIN_END) & (df['Date'] <= VAL_END)]
    test = df[df['Date'] > VAL_END]
    return train, val, test


def train_and_eval(df, features, model_path):
    # Drop NA but include label 0 for multiclass (0 = do not trade / sideways)
    df = df.dropna(subset=features + [LABEL_COL])

    X = df[features].values
    y = df[LABEL_COL].values

    if len(np.unique(y)) < 2:
        raise RuntimeError('Not enough classes in training set')

    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(X, y)
    joblib.dump(clf, model_path)
    return clf


def evaluate(clf, df, features):
    # Include label 0 in evaluation as a valid class
    df = df.dropna(subset=features + [LABEL_COL])
    X = df[features].values
    y = df[LABEL_COL].values
    preds = clf.predict(X)
    print(classification_report(y, preds))
    print('Confusion matrix counts:')
    print(confusion_matrix(y, preds))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--processed', default=str(PROCESSED))
    parser.add_argument('--model-out', default=str(MODELDIR / 'rf_model.pkl'))
    ns = parser.parse_args()

    df = load_data(ns.processed)
    features = pick_features(df)
    if not features:
        raise RuntimeError('No features found to train on. Ensure preprocess generated scaled or cs_z features.')

    print('Using features:', features)
    train, val, test = split_by_date(df)
    print('Split sizes:', len(train), len(val), len(test))

    model = train_and_eval(train, features, ns.model_out)
    print('Trained model saved to', ns.model_out)

    print('\nValidation metrics:')
    evaluate(model, val, features)
    print('\nTest metrics:')
    evaluate(model, test, features)

    # save feature list and meta
    meta = {'features': features}
    with open(MODELDIR / 'meta.json', 'w') as f:
        json.dump(meta, f)


if __name__ == '__main__':
    main()
