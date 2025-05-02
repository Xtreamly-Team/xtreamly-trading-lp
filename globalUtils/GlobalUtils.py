from web3 import Web3
from dotenv import load_dotenv
import os
import json
import logging

load_dotenv()

ARB_RPC_URL = os.getenv('ARBITRUM_RPC_URL')
PRIVATE_KEY = os.getenv('PRIV_KEY')
EXECUTOR_ADDRESS: str = Web3.eth.account.from_key(PRIVATE_KEY).address

GLOBAL_ARBITRUM_PROVIDER = Web3(Web3.HTTPProvider(ARB_RPC_URL))
WALLET_ADDR = GLOBAL_ARBITRUM_PROVIDER.eth.account.from_key(PRIVATE_KEY).address

NON_FUNGIBLE_POSITION_MANAGER_ADDRESS = '0xb53294289E43519102f0aCD356DD18a6D63B359D'
WETH_ADDRESS = '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'
WBTC_ADDRESS = '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f'
USDC_ADDRESS = '0xaf88d065e77c8cC2239327C5EDb3A432268e5831'

with open('xtreamly-trading-lp/globalUtils/ABIs/NonFungiblePositionManager.json', 'r') as f:
    NFPM_abi = json.load(f)

with open('xtreamly-trading-lp/globalUtils/ABIs/WETH.json', 'r') as f:
    weth_abi = json.load(f)

with open('xtreamly-trading-lp/globalUtils/ABIs/WBTC.json', 'r') as f:
    wbtc_abi = json.load(f)

with open('xtreamly-trading-lp/globalUtils/ABIs/USDC.json', 'r') as f:
    usdc_abi = json.load(f)

NFPM_CONTRACT = GLOBAL_ARBITRUM_PROVIDER.eth.contract(address=NON_FUNGIBLE_POSITION_MANAGER_ADDRESS, abi=NFPM_abi)
WETH_CONTRACT = GLOBAL_ARBITRUM_PROVIDER.eth.contract(address=WETH_ADDRESS, abi=weth_abi)
WBTC_CONTRACT = GLOBAL_ARBITRUM_PROVIDER.eth.contract(address=WBTC_ADDRESS, abi=wbtc_abi)
USDC_CONTRACT = GLOBAL_ARBITRUM_PROVIDER.eth.contract(address=USDC_ADDRESS, abi=usdc_abi)


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