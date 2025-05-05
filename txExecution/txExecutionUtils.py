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
        self.token0 = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(token0_address)
        self.token1 = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(token1_address)
        self.fee = GLOBAL_ARBITRUM_PROVIDER.to_int(fee)
        self.tickLower = GLOBAL_ARBITRUM_PROVIDER.to_int(tickLower)
        self.tickUpper = GLOBAL_ARBITRUM_PROVIDER.to_int(tickUpper)
        self.amount0Desired = GLOBAL_ARBITRUM_PROVIDER.to_int(amount0)
        self.amount1Desired = GLOBAL_ARBITRUM_PROVIDER.to_int(amount1)
        self.amount0Min = GLOBAL_ARBITRUM_PROVIDER.to_int(amount0 * 0.995) # 0.5% slippage tolerance 
        self.amount1Min = GLOBAL_ARBITRUM_PROVIDER.to_int(amount1 * 0.995)
        self.recipient = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(wallet_address)
        self.deadline = GLOBAL_ARBITRUM_PROVIDER.to_int(time.time()) + 600  # 10 minutes from now

        self.data = [
            self.token0, 
            self.token1, 
            self.fee, 
            self.tickLower, 
            self.tickUpper, 
            self.amount0Desired, 
            self.amount1Desired, 
            self.amount0Min, 
            self.recipient, 
            self.deadline
            ]


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

        self.data = [
            self.token_id, 
            self.liquidity, 
            self.amount0_min, 
            self.amount1_min, 
            self.deadline
            ]

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

        self.data = [
        self.token_id, 
        self.amount0_desired, 
        self.amount1_desired,
        self.amount0_min, 
        self.amount1_min, 
        self.deadline
        ]


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

