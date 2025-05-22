import time
from src.web3_utils import get_web3


class MintParams:
    def __init__(
        self,
        token0_address,
        token1_address,
        fee,
        tickLower,
        tickUpper,
        amount0,
        amount1,
        wallet_address
    ):
        web3 = get_web3()
        self.token0 = web3.to_checksum_address(token0_address)
        self.token1 = web3.to_checksum_address(token1_address)
        self.fee = web3.to_int(fee)
        self.tickLower = web3.to_int(tickLower)
        self.tickUpper = web3.to_int(tickUpper)
        self.amount0Desired = web3.to_int(amount0)
        self.amount1Desired = web3.to_int(amount1)
        self.amount0Min = 0  # web3.to_int(int(amount0 * 1)) # 0.1% slippage tolerance
        self.amount1Min = 0  # web3.to_int(int(amount1 * 1))
        self.recipient = web3.to_checksum_address(wallet_address)
        self.deadline = web3.to_int(int(time.time()) + 600)  # 10 minutes from now

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
