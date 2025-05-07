from xtreamly_trading_lp.globalUtils.GlobalUtils import *
from xtreamly_trading_lp.txExecution.txExecutionUtils import *

class TxExecution():
    def __init__(self):
        pass

    def deploy_liquidity(self, mint_params: MintParams):
        try:
            enough_WETH: bool = self.ensure_wrapped_eth(mint_params)
            if not enough_WETH:
                raise Exception
            print('made it to here 2')

            approved_weth: bool = self.ensure_approved_weth(mint_params.amount0Desired)
            if not approved_weth:
                raise Exception
            print('made it to here 3')

            enough_USDC: bool = self.ensure_approved_usdc(mint_params.amount1Desired)
            if not enough_USDC:
                raise Exception
            print('made it to here 4')
            
            tx = CONTRACTS.NFPM.functions.mint(mint_params.data).build_transaction({
                'from': EXECUTOR_ADDRESS,
                'nonce': GLOBAL_ARBITRUM_PROVIDER.eth.get_transaction_count(account=EXECUTOR_ADDRESS),
                'gas': 0
            })

            print(tx)

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
            token0 = params.token0
            token1 = params.token1
            amount0_desired = params.amount0Desired
            amount1_desired = params.amount1Desired
            print(token0, token1, amount0_desired, amount1_desired)

            weth_balance = CONTRACTS.weth.functions.balanceOf(EXECUTOR_ADDRESS).call()
            eth_balance = GLOBAL_ARBITRUM_PROVIDER.eth.get_balance(EXECUTOR_ADDRESS)
            print(weth_balance, eth_balance)

            if token0 == GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(WETH_ADDRESS):
                print('case 1 hit')
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

            if token1 == GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(WETH_ADDRESS):
                print('case 2 hit')
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

    def ensure_approved_weth(self, required_amount: int) -> bool:
        try:
            spender = CONTRACTS.NFPM.address
            weth_contract = CONTRACTS.weth

            current_allowance = weth_contract.functions.allowance(
                EXECUTOR_ADDRESS,
                spender
            ).call()

            logger.info(f"Current WETH allowance for spender {spender}: {current_allowance}")

            if current_allowance >= required_amount:
                return True

            logger.info(f"Approving WETH: {required_amount} to spender {spender}")

            tx = weth_contract.functions.approve(
                spender,
                required_amount
            ).build_transaction({
                'from': EXECUTOR_ADDRESS,
                'nonce': GLOBAL_ARBITRUM_PROVIDER.eth.get_transaction_count(account=EXECUTOR_ADDRESS),
                'gas': 0  
            })

            tx_receipt = build_and_send_tx(tx)
            tx_success = check_tx_success(tx_receipt)
            if not tx_success:
                raise Exception("WETH approval transaction failed")

            return True

        except Exception as e:
            logger.error(f"ensure_approved_weth() - Error ensuring approval: {e}", exc_info=True)
            return None

    def ensure_approved_usdc(self, required_amount: int) -> bool:
        try:
            current_allowance = CONTRACTS.usdc.functions.allowance(
                EXECUTOR_ADDRESS,
                GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(NON_FUNGIBLE_POSITION_MANAGER_ADDRESS)
            ).call()

            logger.info(f'Current USDC allowance for spender {NON_FUNGIBLE_POSITION_MANAGER_ADDRESS}: {current_allowance}')

            print(current_allowance, required_amount)
            if current_allowance >= required_amount:
                return True 
            
            self.approve_usdc(required_amount)
            return True

        except Exception as e:
            logger.error(f'txExecution.py - Error checking/ensuring USDC approval. Error: {e}', exc_info=True)
            return None


    def approve_usdc(self, amount: int):
        try:
            tx = CONTRACTS.usdc.functions.approve(
                GLOBAL_ARBITRUM_PROVIDER.to_checksum_address(NON_FUNGIBLE_POSITION_MANAGER_ADDRESS),
                amount
            ).build_transaction({
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
            logger.error(f'txExecution.py - Error approving USDC. Error: {e}', exc_info=True)
            return None

