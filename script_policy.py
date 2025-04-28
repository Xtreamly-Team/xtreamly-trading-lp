# %reset -f
import os
import sys
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
import time
import pytz
import joblib
import db_dtypes
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

import ccxt.pro as ccxt
import asyncio
import nest_asyncio
nest_asyncio.apply()
# =============================================================================
# if os.name == 'nt':  # 'nt' means Windows # Check if the platform is Windows and set the event loop policy
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# =============================================================================

from gcp.func import client_bq, client_st
from codes.features import _beta, _ema
from codes.ccxt import _data_ccxt_1sec
from codes.polygon import run_polygon_agg

time_now = datetime.now()
time_now = datetime.strptime('2024-11-06 04:02:00.000123 UTC', 
                             '%Y-%m-%d %H:%M:%S.%f %Z')

# =============================================================================
# Data
# =============================================================================
# ccxt
time_to = time_now
symbol = 'ETHUSDT'
sec_window = 300
df_ccxt = asyncio.run(_data_ccxt_1sec(time_to, symbol, sec_window))

# polygon
time_to = time_now
t = "X:ETHUSD"
timespan = 'minute'
since = int((time_to - timedelta(minutes=1440 + 1)).timestamp() * 1000)
until = int(time_to.timestamp() * 1000)
df_poly = run_polygon_agg(t, timespan, since,until)

# =============================================================================
# Features
# =============================================================================
df_ccxt_1 = df_ccxt[df_ccxt["_time"] >= df_ccxt["_time"].max() - timedelta(minutes=1)]
df_ccxt_5 = df_ccxt[df_ccxt["_time"] >= df_ccxt["_time"].max() - timedelta(minutes=5)]
df_poly_15 = df_poly[df_poly["_time"] >= df_poly["_time"].max() - timedelta(minutes=15)]
df_poly_60 = df_poly[df_poly["_time"] >= df_poly["_time"].max() - timedelta(minutes=60)]
df_poly_1440 = df_poly[df_poly["_time"] >= df_poly["_time"].max() - timedelta(minutes=1440)]

def _dm(
        df_ccxt_1, df_ccxt_5,
        df_poly_15, df_poly_60, df_poly_1440
        ):

    json_ccxt = {
        f"ids_1min_"+f"mean": df_ccxt_1['ids'].mean(),
        f"ids_5min_"+f"mean": df_ccxt_5['ids'].mean(),
        f"price_1min_"+f"stddev": df_ccxt_1['price'].std(),
        f"price_5min_"+f"ema": _ema(df_ccxt_5['price']),
        f"price_5min_"+f"perc90": df_ccxt_5['price'].quantile(.9),
        f"price_5min_"+f"stddev": df_ccxt_5['price'].std(),
        f"price_5min_"+f"min": df_ccxt_5['price'].min(),
        f"price_5min_"+f"bollingerupper": df_ccxt_5['price'].mean() + df_ccxt_5['price'].std(),
        }
    json_poly = {
        f"price_15min_"+f"stddev": df_poly_15['close'].std(),
        f"price_60min_"+f"stddev": df_poly_60['close'].std(),
        f"price_1440min_"+f"stddev": df_poly_1440['close'].std(),
        f"transactions_60min_"+f"mean": df_poly_60['transactions'].mean(),
        f"vwap_15min_"+f"mean": df_poly_15['vwap'].mean(),
        f"vwap_60min_"+f"mean": df_poly_60['vwap'].mean(),
        }
    json_dm = {**json_ccxt, **json_poly}
    
    standardise_zero = ['stddev', 'gain', 'loss']
    standardise_one = ['perc10', 'perc90', 'max', 'mean', 'min', 'max', 'ema', 'bollingerlower', 'bollingerupper']
    standardise_log = ["ids", "volume", "vwap", "transactions"]
    
    price_ccxt = df_ccxt['price'].iloc[-1]
    price_poly = df_poly['close'].iloc[-1]
    for k in list(json_dm.keys())[:]:
        if "price_" in k:
            if "1min" in k or "5min" in k: 
                price = price_ccxt
            if "15min" in k or "60min" in k or "1440min" in k: 
                price = price_poly
                
            if k.split('_')[-1] in standardise_zero:
                json_dm[k] = json_dm[k]/price
            if k.split('_')[-1] in standardise_one:
                json_dm[k] = (json_dm[k]/price-1)
        for k.split('_')[0] in standardise_log:
            # first scores etc. (none hfor now)
            # next:
            if "_mean" in k:
                json_dm[k] = np.log(json_dm[k]+1)  
    df_dm = pd.DataFrame(pd.Series(json_dm)).T
    return df_dm

df_dm = _dm(df_ccxt_1, df_ccxt_5, df_poly_15, df_poly_60, df_poly_1440)

# =============================================================================
# Predict
# =============================================================================
model_stddev_1min = joblib.load(os.path.join('models', 'v11-model_xgb_y_1min_stddev.joblib'))
col_stddev_1min = [
    "ids_" + "5min_" + "mean",
    "price_" + "60min_" + "stddev",
    "price_" + "1min_" + "stddev",
    "ids_" + "1min_" + "mean",
    "price_" + "1440min_" + "stddev",
    "transactions_" + "60min_" + "mean",
    "price_" + "15min_" + "stddev",
    "vwap_" + "60min_" + "mean",
    "price_" + "5min_" + "ema",
    "price_" + "5min_" + "perc90",
    "vwap_" + "15min_" + "mean",
    "price_" + "5min_" + "stddev",
    "price_" + "5min_" + "min",
    "price_" + "5min_" + "bollingerupper"
    ]
df_dm_stddev_1min = df_dm[col_stddev_1min]
pred_stddev_1min = model_stddev_1min.predict(df_dm_stddev_1min)[0]

# =============================================================================
# Score
# =============================================================================
# fetch last 240 min stdev - from BQ db feed first
symbol = "ETHUSDT"
time_to = time_now.strftime('%Y-%m-%d %H:%M:%S')
time_fr = (time_now - timedelta(minutes=240)).strftime('%Y-%m-%d %H:%M:%S')

sql_std = f"""
SELECT 
    symbol,
    TIMESTAMP_TRUNC(timestamp, MINUTE) as _time,
    ARRAY_AGG(price ORDER BY timestamp LIMIT 1)[OFFSET(0)] as price,
    STDDEV(price) as std, 
    COUNT(*) as nr_rows, 
    COUNT(id) as ids
FROM `xtreamly-ai.xtreamly_raw.futures_um_trades`
WHERE symbol = "{symbol}"
  AND timestamp >= TIMESTAMP("{time_fr}")
  AND timestamp <= TIMESTAMP("{time_to}")
GROUP BY TIMESTAMP_TRUNC(timestamp, MINUTE), symbol
ORDER BY _time ASC
"""
df_sql = client_bq.query(sql_std).result().to_dataframe()
mean_stddev_1min = np.mean(df_sql['std']/df_sql['price'])
score_stddev_1min = (pred_stddev_1min-mean_stddev_1min)/mean_stddev_1min

# =============================================================================
# Policy
# =============================================================================
market_stddev_low_prv = True # need to fetch previous market state

def _marktet_vol_low(pred_stddev_1min, score_stddev_1min, market_stddev_low_prv):
    thres_open_pred = 0.000155
    thres_open_score = -0.003509
    thres_close_pred = 0.000709
    thres_close_score = 0.018872
    
    market_stddev_low_now = market_stddev_low_prv
    if market_stddev_low_prv:
        if pred_stddev_1min >= thres_close_pred and score_stddev_1min >= thres_close_score:
            market_stddev_low_now = False
    else:
        if pred_stddev_1min <= thres_open_pred or score_stddev_1min <= thres_open_score:
            market_stddev_low_now = True
    return market_stddev_low_now
        
market_stddev_low_now = _marktet_vol_low(pred_stddev_1min, score_stddev_1min, market_stddev_low_prv)

print("market_stddev_low_now", market_stddev_low_now)
print("Need to save this value for next market state prediction")

# =============================================================================
# Interaction
# =============================================================================











