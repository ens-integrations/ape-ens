from ens.exceptions import ResolverNotFound  # type: ignore[import-untyped]

from ape_ens.ens import ENS

BASE_COIN_TYPE = 2147492101  # 0x80000000 | 8453


def test_resolve(ens, vitalik):
    assert ens.resolve("vitalik.eth") == vitalik


def test_resolve_forwards_coin_type(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", coin_type=BASE_COIN_TYPE, use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_coin_type_does_not_use_eth_cache(ens, mock_web3_ens, address, vitalik):
    ens.local_registry["vitalik.eth"] = address
    actual = ens.resolve("vitalik.eth", coin_type=BASE_COIN_TYPE)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_coin_type_60_matches_default_eth(ens, mock_web3_ens, address):
    ens.local_registry["vitalik.eth"] = address
    actual = ens.resolve("vitalik.eth", coin_type=60)
    assert actual == address
    mock_web3_ens.address.assert_not_called()
    assert "vitalik.eth:60" not in ens.local_registry


def test_resolve_coin_type_60_calls_default_address(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", coin_type=60, use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth")


def test_get_text(ens, mock_web3_ens):
    mock_web3_ens.get_text.return_value = "Blockchain & Backend Developer"
    assert ens.get_text("vitalik.eth", "description") == "Blockchain & Backend Developer"
    mock_web3_ens.get_text.assert_called_once_with("vitalik.eth", "description")


def test_get_text_empty(ens, mock_web3_ens):
    mock_web3_ens.get_text.return_value = ""
    assert ens.get_text("vitalik.eth", "url") is None


def test_get_text_resolver_not_found(ens, mock_web3_ens):
    mock_web3_ens.get_text.side_effect = ResolverNotFound("missing")
    assert ens.get_text("missing.eth", "url") is None


def test_create_web3_ens_uses_configured_registry_address(project, accounts, mocker):
    fake_registry = accounts[0].address
    mock_backend = mocker.MagicMock()
    from_web3 = mocker.patch("ape_ens.ens.Web3ENS.from_web3", return_value=mock_backend)

    with project.temp_config(ens={"registry_address": fake_registry}):
        wrapper = ENS()
        wrapper.__dict__["_mainnet_provider"] = mocker.MagicMock()
        actual = wrapper._create_web3_ens()

    assert actual is mock_backend
    assert from_web3.call_args.args[1] == fake_registry
