import time
from src.web3_utils import get_web3


class ReduceParams():
    def __init__(
        self,
        token_id,
        liquidity,
        amount0_min=0,
        amount1_min=0,
    ):
        web3 = get_web3()
        self.token_id = web3.to_int(token_id)
        self.liquidity = web3.to_int(liquidity)
        self.amount0_min = web3.to_int(amount0_min)
        self.amount1_min = web3.to_int(amount1_min)
        self.deadline = web3.to_int(int(time.time()) + 600)

        self.data = {
            "tokenId": self.token_id,
            "liquidity": self.liquidity,
            "amount0Min": self.amount0_min,
            "amount1Min": self.amount1_min,
            "deadline": self.deadline
        }
