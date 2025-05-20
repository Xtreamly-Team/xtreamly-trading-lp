import json
from web3 import Web3
from globalUtils.GlobalUtils import NON_FUNGIBLE_POSITION_MANAGER_ADDRESS
from globalUtils.web3_utils import get_web3, get_wallet


def get_positions(private_key: str = None):
    web3 = get_web3()
    position_manager_abi = json.load(open('./globalUtils/ABIs/NonFungiblePositionManager.json'))
    position_manager_address = Web3.to_checksum_address(NON_FUNGIBLE_POSITION_MANAGER_ADDRESS)
    contract = web3.eth.contract(address=position_manager_address, abi=position_manager_abi)
    wallet = get_wallet(private_key).address

    nfts = contract.functions.balanceOf(wallet).call()
    positions = []
    for i in range(nfts):
        token_id = contract.functions.tokenOfOwnerByIndex(wallet, i).call()
        pos = contract.functions.positions(token_id).call()
        positions.append({
            "tokenId": token_id,
            "token0": pos[2],
            "token1": pos[3],
            "fee": pos[4],
            "tickLower": pos[5],
            "tickUpper": pos[6],
            "liquidity": pos[7],
            "feeGrowthInside0LastX128": pos[8],
            "feeGrowthInside1LastX128": pos[9],
            "tokensOwed0": pos[10],
            "tokensOwed1": pos[11]
        })

    return positions
