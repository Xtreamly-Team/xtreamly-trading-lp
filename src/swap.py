import os
import requests
from src.web3_utils import get_web3, get_wallet, build_and_send_and_check_tx
from src.tokens.token import Token


class Swap:
    def __init__(self):
        self.signer = get_wallet()
        self.web3 = get_web3()

    def swap(self, from_token: Token, to_token: Token, amount: float):
        amount_bn = from_token.to_bn(amount)
        [spender, tx_data] = self.get_0x_api_quote(from_token.address, to_token.address, amount_bn)

        from_token.approve_allowance(spender, amount, self.signer.address)

        return self.build_0x_transaction(spender, tx_data)

    def get_0x_api_quote(self, from_token: str, to_token: str, amount: int):
        api_key = os.getenv('0xAPI_KEY')

        price_params = {
            "chainId": 42161,
            "sellToken": from_token,
            "buyToken": to_token,
            "sellAmount": amount,
            "taker": self.signer.address
        }

        headers = {
            "0x-api-key": api_key,
            "0x-version": "v2",
        }

        res = requests.get("https://api.0x.org/swap/allowance-holder/quote?", params=price_params, headers=headers)
        res.raise_for_status()
        data = res.json()

        transaction = data.get("transaction", {})

        return [
            transaction.get("to", None),
            transaction.get("data", None)
        ]

    def build_0x_transaction(self, spender: str, tx_data: str) -> bool:
        tx = {
            'from': self.signer.address,
            'to': self.web3.to_checksum_address(spender),
            'data': tx_data,
            'nonce': self.web3.eth.get_transaction_count(self.signer.address),
            'chainId': 42161
        }

        return build_and_send_and_check_tx(tx)