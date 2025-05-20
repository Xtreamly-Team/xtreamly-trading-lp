import json
from web3 import Web3
from globalUtils.GlobalUtils import USDC_ADDRESS, WETH_ADDRESS
from globalUtils.web3_utils import get_web3, get_wallet


def get_balances(private_key: str = None):
    web3 = get_web3()
    wallet = get_wallet(private_key).address

    eth_balance = web3.eth.get_balance(wallet)
    eth_balance_eth = web3.from_wei(eth_balance, 'ether')

    erc20_abi = json.load(open('./globalUtils/ABIs/USDC.json'))

    return {
        "ETH": float(eth_balance_eth),
        "USDC": _get_token_balance(USDC_ADDRESS, erc20_abi, wallet, web3),
        "WETH": _get_token_balance(WETH_ADDRESS, erc20_abi, wallet, web3),
    }


def _get_token_balance(address, erc20_abi, wallet_address, web3):
    usdc_address = Web3.to_checksum_address(address)
    usdc_contract = web3.eth.contract(address=usdc_address, abi=erc20_abi)
    usdc_balance_raw = usdc_contract.functions.balanceOf(wallet_address).call()
    usdc_decimals = usdc_contract.functions.decimals().call()
    usdc_balance = usdc_balance_raw / (10 ** usdc_decimals)
    return usdc_balance
