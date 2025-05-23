import math
import time
from src.web3_utils import get_web3, get_wallet, build_and_send_and_check_tx
from src.uniswapV3.ABIs import nfpm_abi
from .Pool import Pool
from .MintParams import MintParams
from .ReduceParams import ReduceParams
from .CollectParams import CollectParams
from src.tokens import Token, WETH
from logging import getLogger

logger = getLogger(__name__)

NON_FUNGIBLE_POSITION_MANAGER_ADDRESS = '0xc36442b4a4522e871399cd717abdd847ab11fe88'


class UniswapV3Lp:
    def __init__(self, token0: Token, token1: Token, fee_tier: str, wallet=None):
        self.web3 = get_web3()
        self.wallet = wallet if wallet is not None else get_wallet()
        self.pool = Pool(token0, token1, fee_tier)
        self.token0 = token0
        self.token1 = token1
        self.nfpm_address = self.web3.to_checksum_address(NON_FUNGIBLE_POSITION_MANAGER_ADDRESS)
        self.nfpm_contract = self.web3.eth.contract(address=self.nfpm_address, abi=nfpm_abi)

    def get_all_positions(self):
        wallet = self.wallet.address

        nfts = self.nfpm_contract.functions.balanceOf(wallet).call()
        positions = []
        for i in range(nfts):
            token_id = self.nfpm_contract.functions.tokenOfOwnerByIndex(wallet, i).call()
            pos = self.nfpm_contract.functions.positions(token_id).call()

            token0, token1, fee, tickL, tickU, liq = pos[2], pos[3], pos[4], pos[5], pos[6], pos[7]

            positions.append({
                "tokenId": token_id,
                "token0": token0,
                "token1": token1,
                "fee": fee,
                "tickLower": tickL,
                "tickUpper": tickU,
                "liquidity": liq,
                "feeGrowthInside0LastX128": pos[8],
                "feeGrowthInside1LastX128": pos[9],
                "tokensOwed0": pos[10],
                "tokensOwed1": pos[11]
            })

        return positions

    def get_positions(self):
        all_positions = self.get_all_positions()
        pool_address = self.pool.get_address()
        return [
            {
                **p,
                "pool": pool_address
            }
            for p in all_positions
            if p["token0"].lower() == self.token0.address.lower() and p[
                "token1"].lower() == self.token1.address.lower() and p["fee"] == self.pool.fees
        ]

    def get_open_positions(self):
        positions = self.get_positions()
        return [p for p in positions if p["liquidity"] > 0]

    def get_all_open_positions(self):
        positions = self.get_all_positions()
        return [p for p in positions if p["liquidity"] > 0]

    def _get_tx_params(self):
        return {
            'from': self.wallet.address,
            'nonce': self.web3.eth.get_transaction_count(account=self.wallet.address),
            'gas': 0
        }

    def deploy_liquidity(
            self,
            amount1: float,
            price_lower: float = None,
            price_upper: float = None,
            percent_bound: int = 5
    ):
        center_price = float(self.pool.get_price())
        current_tick = float((self.pool.get_current_tick()))

        tick_lower, tick_upper = self.get_tick_range_from_current_tick(current_tick, percent_bound)

        if price_lower is not None:
            tick_lower = self.pool.get_tick_from_price(price_lower)

        if price_upper is not None:
            tick_upper = self.pool.get_tick_from_price(price_upper)

        amount0 = self.token0.to_bn(amount1 / center_price)
        amount1 = self.token1.to_bn(amount1)

        if self.token0.address == WETH.address:
            self.token0.ensure_weth(amount0)
            time.sleep(1.5)

        self.token0.approve_allowance(self.nfpm_address, amount0)
        time.sleep(1.5)
        self.token1.approve_allowance(self.nfpm_address, amount1)
        time.sleep(1.5)

        mint_params = MintParams(
            self.token0.address,
            self.token1.address,
            self.pool.fees,
            tick_lower,
            tick_upper,
            int(amount0),
            int(amount1),
            self.wallet.address,
        )
        tx = self.nfpm_contract.functions.mint(mint_params.data).build_transaction(self._get_tx_params())
        return build_and_send_and_check_tx(tx)

    def get_tick_range_from_current_tick(self, current_tick: int, percent_bound: int) -> tuple:
        ticks_per_1_percent = int(round(math.log(1.01) / math.log(1.0001)))
        bound_in_ticks = percent_bound * ticks_per_1_percent

        tick_lower = current_tick - bound_in_ticks
        tick_upper = current_tick + bound_in_ticks

        tick_lower_aligned = self.pool.align_tick(tick_lower)
        tick_upper_aligned = self.pool.align_tick(tick_upper)

        return int(tick_lower_aligned), int(tick_upper_aligned)

    def get_position(self, token_id: int):
        positions = self.get_positions()
        return next((t for t in positions if t["tokenId"] == token_id), None)

    def get_latest_position_with_liquidity(self):
        positions_w_liq = [t for t in self.get_positions() if t["liquidity"] > 0]

        if len(positions_w_liq) > 0:
            return positions_w_liq.pop()

        return None

    def reduce_liquidity(self, token_id: int = None, percentage_to_remove: int = 100):
        pos = self.get_latest_position_with_liquidity() if token_id is None else self.get_position(token_id)

        if pos is None:
            logger.info(f"There are no positions with tokenId {token_id}.")
            return False

        token_id = pos["tokenId"]

        liquidity_to_remove = pos["liquidity"]
        if liquidity_to_remove <= 0:
            logger.info(f"There is no liquidity in position {token_id}.")
            return True

        if percentage_to_remove < 100:
            liquidity_to_remove = int(liquidity_to_remove / 100 * percentage_to_remove)

        logger.info(f"Removing {liquidity_to_remove} liquidity from position {token_id}.")

        reduce_params = ReduceParams(token_id, liquidity_to_remove)
        tx = self.nfpm_contract.functions.decreaseLiquidity(reduce_params.data).build_transaction(self._get_tx_params())
        return build_and_send_and_check_tx(tx)

    def collect_liquidity(self, token_id: int):
        logger.info(f"Collecting liquidity from position {token_id}.")
        collect_params = CollectParams(
            token_id,
            self.wallet.address,
            2**128 - 1,
            2**128 - 1
        )
        tx = self.nfpm_contract.functions.collect(collect_params.data).build_transaction(self._get_tx_params())
        return build_and_send_and_check_tx(tx)

    def reduce_and_collect_liquidity(self, token_id: int = None, percentage_to_remove: int = 100):
        pos = self.get_latest_position_with_liquidity() if token_id is None else self.get_position(token_id)
        token_id = pos["tokenId"]

        if self.reduce_liquidity(token_id, percentage_to_remove):
            logger.info(f"Removed liquidity from position {token_id}.")
            if self.collect_liquidity(token_id):
                logger.info(f"Collected liquidity from position {token_id}.")
            else:
                logger.error(f"Unable to collect liquidity from position {token_id}.")
        else:
            logger.error(f"Unable to remove liquidity from position {token_id}.")

    def collect_all_liquidity(self):
        for pos in self.get_positions():
            token_id = pos["tokenId"]
            if self.collect_liquidity(token_id):
                logger.info(f"Collected liquidity from position {token_id}.")
            else:
                logger.error(f"Unable to collect liquidity from position {token_id}.")

    def reduce_and_collect_all_liquidity(self):
        for pos in self.get_positions():
            self.reduce_and_collect_liquidity(pos["tokenId"])
