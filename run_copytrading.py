# %reset -f
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.insert(0, parent_dir)
# =============================================================================
# from google.cloud import storage, bigquery  # , pubsub_v1
# from google.oauth2 import service_account
# project_id = 'xtreamly-ai'
# dataset_id = 'xtreamly_raw'
# auth_file = os.path.join('settings', f'xtreamly-ai-cc418ba37b0c.json')
# credentials = None
# if os.path.isfile(auth_file):
#     credentials = service_account.Credentials.from_service_account_file(auth_file)
# else: print('no credentials')
# =============================================================================

import numpy as np
import pandas as pd
import math
import pytz
import json
import db_dtypes
from datetime import datetime, timedelta
from pprint import pprint
from dotenv import load_dotenv
from settings.gcp import client_bq
from settings.plot import tailwind, _style, _style_black, _style_white
pd.set_option('future.no_silent_downcasting', True)
pd.set_option('display.max_columns', None)
load_dotenv()

id_project = 'xtreamly-ai'
id_database = 'xtreamly_raw'
folder = 'plot_copy_trading'

owners = [
    "0x75e126db7f730fada6c3b879413bea339a357e50",
    "0x0bcc7af222cb7b848fc8f2b9c11978bc3cc6ac59",
    "0x2f4594ffe5868c25e941b5a03af3f8d0deb52505",
    "0xc76cadbbbbbc4dc6299aedb5202ae0c33b59f0a7",
    "0xc207961dc90ddc4f6c9b236964e6d6e2a495dc97",
    "0xd504bd85eb78e6f37afd2d6124edfce14c0b037b",
    "0x17ac2eeaf4eeefab2379118d8ffde37188243bbf",
    "0x020ef786f8c4d19ec3f949fd933ccd1b264c9f9a",
    "0x84754ff267164b75413ad01f35429e52125c0cdf",
    "0x8c9af878a44678b49aef8c60ab0e90ffd9271e54",
    "0x051d091b254ecdbbb4eb8e6311b7939829380b27",
    "0x077490ea44ead91c83d019b96cb9792ec04175cf",
    "0xa028bef2835cab01d39dc3ff34abc46a2f665bb4",
    "0x08e9e9424f7342618d5d66a64ad370b4bba1c25d",
    "0x85e01add9bcc25918c330c42deea69ce5be3ec5d",
    "0xaff0915364800bd6a97f1d7a23f58ee4b1225053",
    "0x965f166c972ac0ce323a9f017b11c5944eb96fd8",
    "0xb515c3052193d329b34dccfc9e25750b7df0c40b",
    "0xbf246450f226f236ffd523dd527d28c5a852d6dd"
]

time_now = datetime.strptime(f'2025-04-28 18:00:00+0000', '%Y-%m-%d %H:%M:%S%z').astimezone(pytz.UTC)
# =============================================================================
# Time
# =============================================================================
date_fr = (time_now - timedelta(minutes=1440*7)).strftime('%Y-%m-%d %H:%M:%S')
date_to = time_now.strftime('%Y-%m-%d %H:%M:%S')

time_fr = datetime.fromisoformat(date_fr).replace(tzinfo=None)
time_to = datetime.fromisoformat(date_to).replace(tzinfo=None)

timestamp_fr = int(pd.to_datetime(date_fr).timestamp())
timestamp_to = int(pd.to_datetime(date_to).timestamp())

# =============================================================================
# Load
# =============================================================================
data = {}
names_tbl = [
    'positions',
    'deposits',
    'withdrawals',
    'claimed_fees',
    'unclaimed_fees_state',
    'current_amount_state',
    ]
for name_tbl in names_tbl[:]:
    col_time = 'from_timestamp' if name_tbl == 'positions' else 'timestamp'
    sql_revert = f"""
    SELECT * 
    FROM `xtreamly-ai.xtreamly_raw.revert_{name_tbl}`
    WHERE {col_time} >= {timestamp_fr}
    """
    df_revert = client_bq.query(sql_revert).result().to_dataframe()
    #df_revert.to_csv(os.path.join('data_copytrading', f'df_copytrading_{name_tbl}.csv'), index=False)
    print(f'loaded {name_tbl} {len(df_revert)}')
# =============================================================================
# for name_tbl in names_tbl:
#     df_r = pd.read_csv(os.path.join('data_copytrading', f'df_copytrading_{name_tbl}.csv'))
# =============================================================================
    data[name_tbl] = df_revert

# =============================================================================
# Pools
# =============================================================================
data_pools = []
for chain in ['etherum', 'arbitrum']:
    with open(os.path.join('uniswap', f'pools_{chain}.json'), 'r') as f:  pools = json.load(f)
    data_pools += [{**p, 'chain': chain} for p in pools]
df_pools = pd.DataFrame(data_pools)    
df_pools['pool'] = df_pools['pool'].str.lower()

# =============================================================================
# Positions
# =============================================================================
df_pos = data['positions'].copy()
df_pos['og_owner'] = df_pos['og_owner'].str.lower()
df_pos['pool'] = df_pos['pool'].str.lower()
df_pos['_time'] = pd.to_datetime(df_pos['now_ts'], unit='s')
df_pos['to_time'] = pd.to_datetime(df_pos.pop('to_timestamp'), unit='s')
df_pos['fr_time'] = pd.to_datetime(df_pos.pop('from_timestamp'), unit='s')
df_pos = df_pos[df_pos['og_owner'].str.lower().isin([o.lower() for o in owners])]
df_pos = df_pos[df_pos['pool'].str.lower().isin([p.lower() for p in df_pools['pool'].unique()])]
df_pos = df_pos.merge(df_pools, on='pool', how='left')
df_pos = df_pos.rename(columns={'id': 'position_id'})

# =============================================================================
# Logs
# =============================================================================
Logs = []
position_ids = df_pos['position_id'].unique()
names_tbl_logs = ['deposits', 'withdrawals', 'claimed_fees']
for name_tbl in names_tbl_logs:
    df_temp = data[name_tbl]
    if df_temp.shape[0]: Logs += [df_temp]
df_log = pd.concat(Logs)
#df_log = df_log.rename(columns={'tx_hash': 'pool'})
#df_log['pool'] = df_log['pool'].str.lower()
df_log['owner'] = df_log['owner'].str.lower()
df_log['_time'] = pd.to_datetime(df_log.pop('timestamp'), unit='s')
df_log = df_log[df_log['owner'].str.lower().isin([o.lower() for o in owners])]
cols_log = [
    '_time',
    #'tx_hash',
    'owner',
    'position_id',
    'type',
    'price',
    'liquidity',
    'amount0',
    'amount1',
    'deposited_token0',
    'withdrawn_token0',
    'collected_fees_token0',
    'deposited_token1',
    'withdrawn_token1',
    'collected_fees_token1',
    ]
df_log = df_log[cols_log].sort_values(by=['owner', 'position_id', '_time', 'type']).reset_index(drop=True)
#df_log = df_log.merge(df_pools, on='pool', how='left')
df_log = df_log.merge(df_pos[['position_id', 'type', 'fee', 'version', 'chain']], on='position_id', how='left')
df_log['position_nr'] = df_log['position_id'].replace({p: i for i,p in enumerate(df_log['position_id'].unique())})
df_log['position_nr'] = df_log['position_nr'].astype(int)
#df_log.pop('position_nr')
if 'type_x' in df_log.columns:
    df_log = df_log.rename(columns={'type_x': 'type'})

# =============================================================================
# Open
# =============================================================================
df_opn = df_log.groupby(['owner', 'position_id'], as_index=False).last()
df_opn = df_opn[df_opn['type'] == 'deposits']
df_opn = df_opn[['owner', 'position_id', '_time', 'price', 'amount0', 'amount1', 'type', 'fee', 'version', 'chain']]
df_opn[['amount0', 'amount1']] = df_opn[['amount0', 'amount1']].astype(float).abs()

# send a message 
# save open to DB
# print(df_opn)

# =============================================================================
# Close
# =============================================================================
df_cls = df_log.groupby(['owner', 'position_id'], as_index=False).last()
df_cls = df_cls[df_cls['type'] != 'deposits']
df_cls = df_cls[['owner', 'position_id', '_time', 'price', 'amount0', 'amount1', 'type', 'fee', 'version', 'chain']]






# save open from DB - filter for
# print(df_cls)




# =============================================================================
# # =============================================================================
# # # Pools
# # =============================================================================
# df_pool = data['positions']
# df_pool['_time'] = pd.to_datetime(df_pool['now_ts'], unit='s')
# df_pool = df_pool[(df_pool['_time']>=time_fr) & (df_pool['_time']<=time_to)]
# df_pool = df_pool.groupby(['network', 'pool', 'token1', 'token0']).agg({
#     'og_owner': 'nunique',
#     'og_owner': 'nunique',
#     }).reset_index(drop=False).sort_values(by=['og_owner'],ascending=False)
# df_pool['pool'] = df_pool['pool'].str.lower()
# df_pool.merge(df_pools, on='pool', how='left')
# =============================================================================