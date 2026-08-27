from ape_ens.utils.coin_type import ETH_COIN_TYPE, coin_type_from_chain_id


def test_coin_type_from_chain_id_ethereum_is_slip44():
    assert coin_type_from_chain_id(1) == ETH_COIN_TYPE == 60


def test_coin_type_from_chain_id_ensip11_l2():
    assert coin_type_from_chain_id(8453) == (0x80000000 | 8453)
    assert coin_type_from_chain_id(8453) == 2147492101


def test_coin_type_from_chain_id_polygon():
    assert coin_type_from_chain_id(137) == (0x80000000 | 137)
