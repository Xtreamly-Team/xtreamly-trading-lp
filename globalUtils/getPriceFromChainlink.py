from web3 import Web3
from xtreamly_trading_lp.globalUtils.GlobalUtils import *

CHAINLINK_AGGREGATOR_ABI = [
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"internalType": "uint80", "name": "roundId", "type": "uint80"},
            {"internalType": "int256", "name": "answer", "type": "int256"},
            {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
            {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
            {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
]

class ChainlinkIDs():
    def __init__(self):
        self.eth = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address('0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612')
        self.btc = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address('0x6ce185860a4963106506C203335A2910413708e9')

CHAINLINK_IDS = ChainlinkIDs()

def get_chainlink_price(id_addr: str) -> float:
    try:
        contract = GLOBAL_ARBITRUM_PROVIDER.eth.contract(
            address=id_addr,
            abi=CHAINLINK_AGGREGATOR_ABI
        )

        decimals = contract.functions.decimals().call()
        latest_round = contract.functions.latestRoundData().call()
        price = latest_round[1] 

        return float(price) / (10 ** decimals)

    except Exception as e:
        logger.error(f"getPriceFromChainlink.py - Error fetching Chainlink price: {e}", exc_info=True)
        return None
