from globalUtils.GlobalUtils import *
from txExecution.txExecutionUtils import *

class TxExecution():
    def __init__(self):
        pass

    def deploy_liquidity(self, mint_params: MintParams):
        try:
            enough_WETH: bool = self.ensure_wrapped_eth(mint_params)
            if not enough_WETH:
                raise Exception
            
            tx = CONTRACTS.NFPM.functions.mint(mint_params.data).build_transaction({
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

    def remove_liquidity(self, reduce_params: ReduceParams):
        try:
            tx = CONTRACTS.NFPM.functions.decreaseLiquidity(reduce_params.data).build_transaction({
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

    def increase_liquidity(self, increase_params: IncreaseParams):
        try:
            enough_WETH: bool = self.ensure_wrapped_eth(increase_params)
            if not enough_WETH:
                raise Exception
            
            tx = CONTRACTS.NFPM.functions.increaseLiquidity(increase_params.data).build_transaction({
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

    def wrap_eth(self, amount: int):
        try:
            tx = CONTRACTS.weth.functions.deposit().build_transaction({
                'from': EXECUTOR_ADDRESS,
                'value': amount,
                'nonce': GLOBAL_ARBITRUM_PROVIDER.eth.get_transaction_count(account=EXECUTOR_ADDRESS),
                'gas': 0 
            })

            tx_receipt = build_and_send_tx(tx)
            tx_success = check_tx_success(tx_receipt)
            if not tx_success:
                raise Exception

            return tx_receipt

        except Exception as e:
            logger.error(f'txExecution.py - Error while wrapping ETH. Error: {e}', exc_info=True)
            return None

    def ensure_wrapped_eth(self, params) -> bool:
        try:
            token0 = params.data['token0']
            token1 = params.data['token1']
            amount0_desired = params.data['amount0Desired']
            amount1_desired = params.data['amount1Desired']

            ETH_ADDRESS = GLOBAL_ARBITRUM_PROVIDER.to_checksum_address("0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")

            weth_balance = CONTRACTS.weth.functions.balanceOf(EXECUTOR_ADDRESS).call()
            eth_balance = GLOBAL_ARBITRUM_PROVIDER.eth.get_balance(EXECUTOR_ADDRESS)

            if token0 == ETH_ADDRESS or token0 == WETH_ADDRESS:
                required_amount = amount0_desired
                if weth_balance < required_amount:
                    logger.info(f'TxExecution.py - Not enough WETH for token0: have {weth_balance}, need {required_amount}')
                    if eth_balance >= (required_amount - weth_balance):
                        wrap_amount = required_amount - weth_balance
                        logger.info(f'Wrapping {wrap_amount} wei of ETH to WETH for token0')
                        self.wrap_eth(wrap_amount)
                    else:
                        logger.error('TxExecution.py - Not enough ETH to wrap the required WETH for token0.', exc_info=True)
                        return False

            if token1 == ETH_ADDRESS or token1 == WETH_ADDRESS:
                required_amount = amount1_desired
                if weth_balance < required_amount:
                    logger.info(f'TxExecution.py - Not enough WETH for token1: have {weth_balance}, need {required_amount}')
                    if eth_balance >= (required_amount - weth_balance):
                        wrap_amount = required_amount - weth_balance
                        logger.info(f'Wrapping {wrap_amount} wei of ETH to WETH for token1')
                        self.wrap_eth(wrap_amount)
                    else:
                        logger.error('TxExecution.py - Not enough ETH to wrap the required WETH for token1.', exc_info=True)
                        return False
            return True

        except Exception as e:
            logger.error(f'TxExecution.py - Failed while checking if sufficient WETH for trade. Error: {e}', exc_info=True)
            return False
