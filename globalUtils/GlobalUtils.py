from web3 import Web3
from dotenv import load_dotenv
import os
import json
import logging

load_dotenv()

ARB_RPC_URL = os.getenv('ARBITRUM_RPC_URL')
PRIVATE_KEY = os.getenv('PRIV_KEY')

GLOBAL_ARBITRUM_PROVIDER = Web3(Web3.HTTPProvider(ARB_RPC_URL))
EXECUTOR_ADDRESS = GLOBAL_ARBITRUM_PROVIDER.eth.account.from_key(PRIVATE_KEY).address

NON_FUNGIBLE_POSITION_MANAGER_ADDRESS = '0xc36442b4a4522e871399cd717abdd847ab11fe88'
WETH_ADDRESS = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'
WBTC_ADDRESS = '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f'
USDC_ADDRESS = '0xaf88d065e77c8cC2239327C5EDb3A432268e5831'

ETH_USDC_3BPS_ADDR = '0xC1A31dC7Bc2e06aA0228D2Ea58dF4F92C3A16998'

with open('xtreamly_trading_lp/globalUtils/ABIs/NonFungiblePositionManager.json', 'r') as f:
    NFPM_abi = json.load(f)

with open('xtreamly_trading_lp/globalUtils/ABIs/WETH.json', 'r') as f:
    weth_abi = json.load(f)

with open('xtreamly_trading_lp/globalUtils/ABIs/WBTC.json', 'r') as f:
    wbtc_abi = json.load(f)

with open('xtreamly_trading_lp/globalUtils/ABIs/USDC.json', 'r') as f:
    usdc_abi = json.load(f)

NFPM_CONTRACT = GLOBAL_ARBITRUM_PROVIDER.eth.contract(address=GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(NON_FUNGIBLE_POSITION_MANAGER_ADDRESS), abi=NFPM_abi)
WETH_CONTRACT = GLOBAL_ARBITRUM_PROVIDER.eth.contract(address=GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(WETH_ADDRESS), abi=weth_abi)
WBTC_CONTRACT = GLOBAL_ARBITRUM_PROVIDER.eth.contract(address=GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(WBTC_ADDRESS), abi=wbtc_abi)
USDC_CONTRACT = GLOBAL_ARBITRUM_PROVIDER.eth.contract(address=GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(USDC_ADDRESS), abi=usdc_abi)


class Contracts:
    def __init__(self):
        self.NFPM = NFPM_CONTRACT
        self.weth = WETH_CONTRACT
        self.wbtc = WBTC_CONTRACT
        self.usdc = USDC_CONTRACT

CONTRACTS = Contracts()

# Setup for the general application logger
logger = logging.getLogger(__name__)
app_handler = logging.FileHandler('app.log')
app_handler.setLevel(logging.INFO)
app_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app_handler.setFormatter(app_formatter)
logger.addHandler(app_handler)
logger.setLevel(logging.INFO)