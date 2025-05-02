from globalUtils.GlobalUtils import *
from txExecution.txExecutionUtils import *

class TxExecution():
    def __init__(self):
        pass

    def deploy_liquidity(mint_params: MintParams):
        try:
            tx = CONTRACTS.NFPM.functions.mint(mint_params).build_transaction({
                'from': EXECUTOR_ADDRESS,
                'nonce': GLOBAL_ARBITRUM_PROVIDER.eth.get_transaction_count(account=EXECUTOR_ADDRESS),
                'gas': 0
            })

            tx_receipt = build_and_send_tx(tx)
            tx_success = check_tx_success(tx_receipt)
            if not tx_success:
                raise Exception

            return tx_receipt

        except Exception as e:
            logger.error(f'txExecution.py - Error while delpoying liquidity. Error: {e}', exc_info=True)
            return None

    def remove_liquidity(reduce_params: ReduceParams):
        try:
            tx = CONTRACTS.NFPM.functions.decreaseLiquidity(reduce_params).build_transaction({
                'from': EXECUTOR_ADDRESS,
                'nonce': GLOBAL_ARBITRUM_PROVIDER.eth.get_transaction_count(account=EXECUTOR_ADDRESS),
                'gas': 0
            })

            tx_receipt = build_and_send_tx(tx)
            tx_success = check_tx_success(tx_receipt)
            if not tx_success:
                raise Exception

            return tx_receipt

        except Exception as e:
            logger.error(f'txExecution.py - Error while reducing liquidity. Error: {e}', exc_info=True)
            return None

    def increase_liquidity(increase_params: IncreaseParams):
        try:
            tx = CONTRACTS.NFPM.functions.increaseLiquidity(increase_params).build_transaction({
                'from': EXECUTOR_ADDRESS,
                'nonce': GLOBAL_ARBITRUM_PROVIDER.eth.get_transaction_count(account=EXECUTOR_ADDRESS),
                'gas': 0
            })

            tx_receipt = build_and_send_tx(tx)
            tx_success = check_tx_success(tx_receipt)
            if not tx_success:
                raise Exception

            return tx_receipt

        except Exception as e:
            logger.error(f'txExecution.py - Error while adding liquidity to position. Error: {e}', exc_info=True)
            return None