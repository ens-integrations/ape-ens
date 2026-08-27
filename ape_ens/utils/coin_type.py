ETH_COIN_TYPE = 60
EVM_COIN_TYPE_OFFSET = 0x80000000


def coin_type_from_chain_id(chain_id: int) -> int:
    """Map an EVM chain ID to an ENSIP-9/11 coin type.

    Ethereum mainnet (chain ID 1) is SLIP-44 coin 60, not ``0x80000000 | 1``.
    Other EVM chains use ENSIP-11: ``0x80000000 | chain_id``.
    """
    if chain_id == 1:
        return ETH_COIN_TYPE
    return EVM_COIN_TYPE_OFFSET | chain_id
