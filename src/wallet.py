from src.web3_utils import get_web3, get_wallet
from src.tokens import WETH, USDC, WBTC


def get_balances(private_key: str = None):
    web3 = get_web3()
    wallet = get_wallet(private_key).address

    eth_balance = web3.eth.get_balance(wallet)
    eth_balance_eth = web3.from_wei(eth_balance, 'ether')

    return {
        "ETH": float(eth_balance_eth),
        "USDC": USDC.balance_readable(wallet),
        "WETH": WETH.balance_readable(wallet),
        "WBTC": WBTC.balance_readable(wallet),
    }
