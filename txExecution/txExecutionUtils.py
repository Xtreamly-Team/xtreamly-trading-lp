import os
from globalUtils.GlobalUtils import *
import time
from web3.types import TxReceipt

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
        self.token0 = token0_address,
        self.token1 = token1_address
        self.fee = 3000
        self.tickLower = tickLower
        self.tickUpper = tickUpper
        self.amount0Desired = amount0
        self.amount1Desired = amount1
        self.amount0Min = int(amount0 * 0.995) # 0.5% slippage tolerance 
        self.amount1Min = int(amount1 * 0.995)
        self.recipient = wallet_address
        self.deadline = int(time.time()) + 600  # 10 minutes from now

class ReduceParams():
    def __init__(self,
        token_id,
        liquidity,
        amount0_min,
        amount1_min,
        deadline):
        self.token_id = token_id
        self.liquidity = liquidity
        self.amount0_min = amount0_min
        self.amount1_min = amount1_min
        self.deadline = deadline

class IncreaseParams():
    def __init__(self,
        token_id,
        amount0_desired,
        amount1_desired,
        amount0_min,
        amount1_min,
        deadline):
        self.token_id = token_id
        self.amount0_desired = amount0_desired
        self.amount1_desired = amount1_desired
        self.amount0_min = amount0_min
        self.amount1_min = amount1_min
        self.deadline = deadline


def build_and_send_tx(tx_data: dict):
    try:
        priv_key = os.getenv('EXECUTOR_PRIV_KEY')
        estimated_gas = GLOBAL_ARBITRUM_PROVIDER.eth.estimate_gas(tx_data)
        tx_data['gas'] = estimated_gas

        fee_history = GLOBAL_ARBITRUM_PROVIDER.eth.fee_history(1, "latest")
        base_fee_per_gas = fee_history["baseFeePerGas"][-1]
        max_priority_fee_per_gas = GLOBAL_ARBITRUM_PROVIDER.eth.max_priority_fee
        max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas
        tx_data["maxFeePerGas"] = int(max_fee_per_gas * 1.05)

        signed_place_market_order_tx = GLOBAL_ARBITRUM_PROVIDER.eth.account.sign_transaction(tx_data, private_key=priv_key)
        tx_hash_place_market_order = GLOBAL_ARBITRUM_PROVIDER.eth.send_raw_transaction(signed_place_market_order_tx.rawTransaction)
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