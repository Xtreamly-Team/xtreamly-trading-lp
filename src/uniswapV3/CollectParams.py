from src.web3_utils import get_web3


class CollectParams():
    def __init__(
        self,
        token_id,
        recipient,
        amount0_min,
        amount1_min
    ):
        web3 = get_web3()
        self.token_id = web3.to_int(token_id)
        self.recipient = web3.to_checksum_address(recipient)
        self.amount0_min = web3.to_int(amount0_min)
        self.amount1_min = web3.to_int(amount1_min)

        self.data = (
            self.token_id,
            self.recipient,
            self.amount0_min,
            self.amount1_min,
        )
