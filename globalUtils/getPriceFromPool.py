from decimal import Decimal
from web3 import Web3
from xtreamly_trading_lp.globalUtils.GlobalUtils import *

ETH_USDC_5BPS = '0xC6962004f452bE9203591991D15f6b388e09E8D0'
ETH_USDT_5BPS = '0x641c00a822e8b671738d32a431a4fb6074e5c79d'
WBTC_USDC_5BPS = '0xac70bd92f89e6739b3a08db9b6081a923912f73d'
WBTC_USDT_5BPS = '0x5969efdde3cf5c0d9a88ae51e47d721096a97203'

POOL_ABI = [
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
            {"internalType": "int24", "name": "tick", "type": "int24"},
            {"internalType": "uint16", "name": "observationIndex", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"},
            {"internalType": "uint8", "name": "feeProtocol", "type": "uint8"},
            {"internalType": "bool", "name": "unlocked", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

ETH_USDC_POOL = GLOBAL_ARBITRUM_PROVIDER.eth.contract(address=GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(ETH_USDC_5BPS), abi=POOL_ABI)
ETH_USDT_POOL = GLOBAL_ARBITRUM_PROVIDER.eth.contract(address=GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(ETH_USDT_5BPS), abi=POOL_ABI)
WBTC_USDC_POOL = GLOBAL_ARBITRUM_PROVIDER.eth.contract(address=GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(WBTC_USDC_5BPS), abi=POOL_ABI)
WBTC_USDT_POOL = GLOBAL_ARBITRUM_PROVIDER.eth.contract(address=GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(WBTC_USDT_5BPS), abi=POOL_ABI)

class PoolContracts():
    def __init__(self):
        self.ETH_USDC = ETH_USDC_POOL
        self.ETH_USDT = ETH_USDT_POOL
        self.WBTC_USDC = WBTC_USDC_POOL
        self.WBTC_USDT = WBTC_USDT_POOL

POOL_CONTRACTS = PoolContracts()

def get_decimals_for_pool(pool_contract) -> tuple:
    try:
        pool_address = pool_contract.address.lower()

        if pool_address == ETH_USDC_5BPS.lower():
            return (18, 6)
        elif pool_address == ETH_USDT_5BPS.lower():
            return (18, 6)
        elif pool_address == WBTC_USDC_5BPS.lower():
            return (8, 6)
        elif pool_address == WBTC_USDT_5BPS.lower():
            return (8, 6)
        else:
            raise ValueError(f"Unknown or unsupported pool address: {pool_address}")

    except Exception as e:
        logger.error(f"getPriceFromPool - Error getting decimals for pool {pool_address}: {e}", exc_info=True)
        return (None, None)


def get_price_from_pool(pool_contract) -> Decimal:
    try:
        token0_decimals, token1_decimals = get_decimals_for_pool(pool_contract)
        sqrt_price_x96 = pool_contract.functions.slot0().call()[0]
        sqrt_price_decimal = Decimal(sqrt_price_x96)
        ratio_x96 = sqrt_price_decimal ** 2 / (2 ** 192)

        decimal_adjustment = Decimal(10 ** (token0_decimals - token1_decimals))
        price = ratio_x96 * decimal_adjustment

        return price

    except Exception as e:
        logger.error(f"getPriceFromPool - Error reading price from pool: {e}")
        return None

def get_current_tick(pool_contract) -> Decimal:
    try:
        tick = pool_contract.functions.slot0().call()[1]
        return Decimal(tick)

    except Exception as e:
        logger.error(f"getPriceFromPool - Error reading price from pool: {e}")
        return None

y = get_price_from_pool(POOL_CONTRACTS.ETH_USDC)
print(y)