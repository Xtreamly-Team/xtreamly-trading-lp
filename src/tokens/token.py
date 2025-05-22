from src.web3_utils import get_web3, get_wallet, build_and_send_and_check_tx
from src.tokens.addresses import TOKEN_ADDRESSES
from src.tokens.ABIs import TOKEN_ABIs
import logging

logger = logging.getLogger(__name__)


class Token:
    def __init__(self, token: str):
        self.token = token
        self.address = TOKEN_ADDRESSES[token]
        self.abi = TOKEN_ABIs[token]
        self.web3 = get_web3()
        self.contract = self.web3.eth.contract(address=self.web3.to_checksum_address(self.address), abi=self.abi)
        self.decimals = self.contract.functions.decimals().call()

    def to_bn(self, amount: float) -> int:
        return int(amount * 10 ** self.decimals)

    def approve_allowance(self, spender: str, required_amount: float = None, executor: str = None) -> int:
        executor = get_wallet().address if executor is None else executor
        spender = self.web3.to_checksum_address(spender)

        # If not provided it will provide access to all tokens in the wallet
        required_amount = 2 ** 256 - 1 if required_amount is None else self.to_bn(required_amount)

        current_allowance = self.contract.functions.allowance(executor, spender).call()

        if current_allowance >= required_amount:
            logger.info(f"There is enough {self.token} allowance for spender {spender}: {current_allowance}")
            return True

        logger.info(f"Approving {self.token}: {required_amount} to spender {spender}")

        tx = self.contract.functions.approve(spender, required_amount).build_transaction({
            'from': executor,
            'nonce': self.web3.eth.get_transaction_count(account=executor),
            'gas': 0
        })

        tx_success = build_and_send_and_check_tx(tx)

        if not tx_success:
            logger.error(f"Unable to approve {self.token}: {required_amount} to spender {spender}")
            return False

        logger.info(f"Approved {self.token}: {required_amount} to spender {spender}")
        return True

    def balance(self, wallet_address: str = None):
        wallet_address = get_wallet().address if wallet_address is None else wallet_address
        return self.contract.functions.balanceOf(wallet_address).call()

    def balance_readable(self, wallet_address: str = None):
        return self.balance(wallet_address) / (10 ** self.decimals)
