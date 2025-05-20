import os
from web3 import Web3


def get_web3():
    return Web3(Web3.HTTPProvider(os.getenv("ARBITRUM_RPC_URL")))


def get_wallet(private_key: str = None):
    private_key = os.getenv("PRIV_KEY") if private_key is None else private_key
    return get_web3().eth.account.from_key(private_key)
