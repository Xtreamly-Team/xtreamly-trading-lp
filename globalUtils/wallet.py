import os
import json
from web3 import Web3
from globalUtils.GlobalUtils import USDC_ADDRESS, WETH_ADDRESS


def get_balances(private_key: str = None):
    private_key = os.getenv("PRIV_KEY") if private_key is None else private_key

    web3 = Web3(Web3.HTTPProvider(os.getenv("ARBITRUM_RPC_URL")))

    account = web3.eth.account.from_key(private_key)
    wallet_address = account.address

    eth_balance = web3.eth.get_balance(wallet_address)
    eth_balance_eth = web3.from_wei(eth_balance, 'ether')

    erc20_abi = json.load(open('./globalUtils/ABIs/USDC.json'))

    return {
        "ETH": float(eth_balance_eth),
        "USDC": _get_token_balance(USDC_ADDRESS, erc20_abi, wallet_address, web3),
        "WETH": _get_token_balance(WETH_ADDRESS, erc20_abi, wallet_address, web3),
    }


def _get_token_balance(address, erc20_abi, wallet_address, web3):
    usdc_address = Web3.to_checksum_address(address)
    usdc_contract = web3.eth.contract(address=usdc_address, abi=erc20_abi)
    usdc_balance_raw = usdc_contract.functions.balanceOf(wallet_address).call()
    usdc_decimals = usdc_contract.functions.decimals().call()
    usdc_balance = usdc_balance_raw / (10 ** usdc_decimals)
    return usdc_balance
