from src.web3_utils import get_wallet, build_and_send_and_check_tx
from src.tokens.token import Token
from logging import getLogger

logger = getLogger(__name__)


class USDCTokenCls(Token):
    def __init__(self):
        super().__init__(token="USDC")


class WETHTokenCls(Token):
    def __init__(self):
        super().__init__(token="WETH")

    def wrap(self, amount: float, executor: str = None):
        executor = get_wallet().address if executor is None else executor
        tx = self.contract.functions.deposit().build_transaction({
            'from': executor,
            'value': self.to_bn(amount),
            'nonce': self.web3.eth.get_transaction_count(account=executor),
            'gas': 0
        })

        return build_and_send_and_check_tx(tx)

    def unwrap(self, amount: float, executor: str = None):
        executor = get_wallet().address if executor is None else executor
        tx = self.contract.functions.withdraw().build_transaction({
            'from': executor,
            'value': self.to_bn(amount),
            'nonce': self.web3.eth.get_transaction_count(account=executor),
            'gas': 0
        })

        return build_and_send_and_check_tx(tx)

    def ensure_weth(self, amount: int, wallet_address: str = None):
        wallet_address = get_wallet().address if wallet_address is None else wallet_address

        balance = self.balance(wallet_address)
        amount_to_wrap = amount - balance
        if balance < amount:
            logger.info(f'Not enough WETH: {balance}, need {amount}, wrapping {amount_to_wrap}')
            self.wrap(amount_to_wrap)


class WBTCTokenCls(Token):
    def __init__(self):
        super().__init__(token="WBTC")
