import os
from xtreamly_trading_lp.globalUtils.GlobalUtils import *
import time
from web3.types import TxReceipt
from uniswappy import *
import math


fee = UniV3Utils.FeeAmount.MEDIUM
tick_spacing = UniV3Utils.TICK_SPACINGS[fee]
lwr_tick = UniV3Utils.getMinTick(tick_spacing)
upr_tick = UniV3Utils.getMaxTick(tick_spacing)

ETH = ERC20("WETH", WETH_ADDRESS)
BTC = ERC20("WBTC", WBTC_ADDRESS)
USDC = ERC20("USDC", USDC_ADDRESS)

exchg_data = UniswapExchangeData(tkn0 = ETH, tkn1 = USDC, symbol="LP", 
                                   address="0xC1A31dC7Bc2e06aA0228D2Ea58dF4F92C3A16998", version = 'V3', 
                                   tick_spacing = tick_spacing, 
                                   fee = fee)

def get_tick_range(center_price: float, percent_bound: int, tick_spacing: int) -> tuple:
    if percent_bound <= 0:
        raise ValueError("percent_bound must be greater than 0")

    lower_price = center_price * (1 - percent_bound / 100)
    upper_price = center_price * (1 + percent_bound / 100)

    def price_to_tick(price: float) -> int:
        return int(round(math.log(price) / math.log(1.0001)))

    tick_lower = price_to_tick(lower_price)
    tick_upper = price_to_tick(upper_price)

    def align_tick(tick: int, spacing: int) -> int:
        return tick - (tick % spacing)

    tick_lower_aligned = align_tick(tick_lower, tick_spacing)
    tick_upper_aligned = align_tick(tick_upper, tick_spacing)

    return tick_lower_aligned, tick_upper_aligned


class MintParams():
    def __init__(self,
        token0_address,
        token1_address,
        fee,
        tickLower,
        tickUpper,
        amount0,
        amount1,
        wallet_address
        ):
        self.token0 = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(token0_address)
        self.token1 = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(token1_address)
        self.fee = GLOBAL_ARBITRUM_PROVIDER.to_int(fee)
        self.tickLower = GLOBAL_ARBITRUM_PROVIDER.to_int(tickLower)
        self.tickUpper = GLOBAL_ARBITRUM_PROVIDER.to_int(tickUpper)
        self.amount0Desired = GLOBAL_ARBITRUM_PROVIDER.to_int(amount0)
        self.amount1Desired = GLOBAL_ARBITRUM_PROVIDER.to_int(amount1)
        self.amount0Min = GLOBAL_ARBITRUM_PROVIDER.to_int(int(amount0 * 0.97)) # 0.1% slippage tolerance 
        self.amount1Min = GLOBAL_ARBITRUM_PROVIDER.to_int(int(amount1 * 0.97))
        self.recipient = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(wallet_address)
        self.deadline = GLOBAL_ARBITRUM_PROVIDER.to_int(int(time.time()) + 600)  # 10 minutes from now

        self.data = (
            self.token0, 
            self.token1, 
            self.fee, 
            self.tickLower, 
            self.tickUpper, 
            self.amount0Desired, 
            self.amount1Desired, 
            self.amount0Min,
            self.amount1Min,
            self.recipient, 
            self.deadline
        )


class ReduceParams():
    def __init__(self,
        token_id,
        liquidity,
        amount0_min,
        amount1_min,
        deadline
        ):
        self.token_id = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(token_id)
        self.liquidity = GLOBAL_ARBITRUM_PROVIDER.to_int(liquidity)
        self.amount0_min = GLOBAL_ARBITRUM_PROVIDER.to_int(amount0_min)
        self.amount1_min = GLOBAL_ARBITRUM_PROVIDER.to_int(amount1_min)
        self.deadline = GLOBAL_ARBITRUM_PROVIDER.to_int(deadline)

        self.data = (
            self.token_id, 
            self.liquidity, 
            self.amount0_min, 
            self.amount1_min, 
            self.deadline
        )

class IncreaseParams():
    def __init__(self,
        token_id,
        amount0_desired,
        amount1_desired,
        amount0_min,
        amount1_min,
        deadline):
        self.token_id = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(token_id)
        self.amount0_desired = GLOBAL_ARBITRUM_PROVIDER.to_int(amount0_desired)
        self.amount1_desired = GLOBAL_ARBITRUM_PROVIDER.to_int(amount1_desired)
        self.amount0_min = GLOBAL_ARBITRUM_PROVIDER.to_int(amount0_min)
        self.amount1_min = GLOBAL_ARBITRUM_PROVIDER.to_int(amount1_min)
        self.deadline = GLOBAL_ARBITRUM_PROVIDER.to_int(deadline)

        self.data = (
        self.token_id, 
        self.amount0_desired, 
        self.amount1_desired,
        self.amount0_min, 
        self.amount1_min, 
        self.deadline
        )


def build_and_send_tx(tx_data: dict):
    try:
        priv_key = os.getenv('PRIV_KEY')
        estimated_gas = GLOBAL_ARBITRUM_PROVIDER.eth.estimate_gas(tx_data)
        tx_data['gas'] = estimated_gas

        fee_history = GLOBAL_ARBITRUM_PROVIDER.eth.fee_history(1, "latest")
        base_fee_per_gas = fee_history["baseFeePerGas"][-1]
        max_priority_fee_per_gas = GLOBAL_ARBITRUM_PROVIDER.eth.max_priority_fee
        max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas
        tx_data["maxFeePerGas"] = int(max_fee_per_gas * 1.05)

        signed_place_market_order_tx = GLOBAL_ARBITRUM_PROVIDER.eth.account.sign_transaction(tx_data, private_key=priv_key)
        tx_hash_place_market_order = GLOBAL_ARBITRUM_PROVIDER.eth.send_raw_transaction(signed_place_market_order_tx.raw_transaction)
        tx_receipt = GLOBAL_ARBITRUM_PROVIDER.eth.wait_for_transaction_receipt(tx_hash_place_market_order)

        return tx_receipt
    
    except Exception as e:
            logger.error(f'txExecutionUtils.py - Error while sending transaction. Error: {e}', exc_info=True)
            return None

def check_tx_success(tx_receipt: TxReceipt) -> bool:
    try:
        time.sleep(0.5)
        if tx_receipt['status'] != 1:
            return False
        else:
            return True
    
    except Exception as e:
        logger.error(f'txExecutionUtils.py - Error checking for Tx success. Error: {e}', exc_info=True)
        return None  

