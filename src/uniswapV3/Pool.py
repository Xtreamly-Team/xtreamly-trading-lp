import math
from decimal import Decimal
from src.web3_utils import get_web3
from src.uniswapV3.ABIs import pool_abi, uniswap_v3_factory_abi
from src.tokens import Token

UNISWAP_FACTORY_ADDRESS = '0x1F98431c8aD98523631AE4a59f267346ea31F984'

POOLS = {
    "0.01%": {
        "fees": 100,
        "tick_spacing": 1,
    },
    "0.05%": {
        "fees": 500,
        "tick_spacing": 10,
    },
    "0.3%": {
        "fees": 3000,
        "tick_spacing": 60,
    },
    "1%": {
        "fees": 10000,
        "tick_spacing": 200,
    }
}


class Pool:
    def __init__(self, token0: Token, token1: Token, fee_tier: str):
        self.token0 = token0
        self.token1 = token1
        self.web3 = get_web3()
        self.pool = POOLS[fee_tier]
        self.fees = self.pool["fees"]
        self.tick_spacing = self.pool["tick_spacing"]
        self.contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(self.get_address()),
            abi=pool_abi
        )

    def get_address(self):
        factory = self.web3.eth.contract(
            address=self.web3.to_checksum_address(UNISWAP_FACTORY_ADDRESS),
            abi=uniswap_v3_factory_abi,
        )
        return factory.functions.getPool(
            self.web3.to_checksum_address(self.token0.address),
            self.web3.to_checksum_address(self.token1.address),
            self.pool["fees"],
        ).call()

    def get_decimals_for_pool(self) -> tuple:
        return self.token0.decimals, self.token1.decimals

    def get_price(self):
        token0_decimals, token1_decimals = self.get_decimals_for_pool()
        sqrt_price_x96 = self.contract.functions.slot0().call()[0]
        sqrt_price_decimal = Decimal(sqrt_price_x96)
        ratio_x96 = sqrt_price_decimal ** 2 / (2 ** 192)

        decimal_adjustment = Decimal(10 ** (token0_decimals - token1_decimals))
        price = ratio_x96 * decimal_adjustment

        return price

    def get_current_tick(self):
        tick = self.contract.functions.slot0().call()[1]
        return Decimal(tick)

    def get_tick_from_price(self, price: float) -> int:
        price = price / (10 ** self.token1.decimals / 10 ** self.token0.decimals)
        raw_tick = math.log(price) / math.log(1.0001)
        return int(raw_tick // self.tick_spacing * self.tick_spacing)

    def align_tick(self, tick: int) -> int:
        return tick - (tick % self.tick_spacing)
