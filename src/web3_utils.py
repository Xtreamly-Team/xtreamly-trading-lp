import os
import time
from web3 import Web3
from web3.types import TxReceipt


def get_web3():
    return Web3(Web3.HTTPProvider(os.getenv("ARBITRUM_RPC_URL")))


def get_wallet(private_key: str = None):
    private_key = os.getenv("PRIV_KEY") if private_key is None else private_key
    return get_web3().eth.account.from_key(private_key)


def build_and_send_tx(tx_data: dict):
    priv_key = os.getenv('PRIV_KEY')
    web3 = get_web3()

    estimated_gas = web3.eth.estimate_gas(tx_data)
    tx_data['gas'] = estimated_gas

    fee_history = web3.eth.fee_history(1, "latest")
    base_fee_per_gas = fee_history["baseFeePerGas"][-1]
    max_priority_fee_per_gas = web3.eth.max_priority_fee
    max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas
    tx_data["maxFeePerGas"] = int(max_fee_per_gas * 1.05)
    tx_data["maxPriorityFeePerGas"] = web3.to_wei(0.1, "gwei")

    signed_place_market_order_tx = web3.eth.account.sign_transaction(tx_data, private_key=priv_key)
    tx_hash_place_market_order = web3.eth.send_raw_transaction(signed_place_market_order_tx.raw_transaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash_place_market_order)

    return tx_receipt


def check_tx_success(tx_receipt: TxReceipt) -> bool:
    time.sleep(0.5)
    return tx_receipt['status'] == 1


def build_and_send_and_check_tx(tx_data: dict):
    return check_tx_success(build_and_send_tx(tx_data))
