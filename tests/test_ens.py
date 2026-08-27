import pytest
from ens.exceptions import ResolverNotFound  # type: ignore[import-untyped]

from ape_ens.ens import ENS
from ape_ens.exceptions import (
    AmbiguousNetworkError,
    ApeENSException,
    ConflictingResolveOptionsError,
    LocalNetworkCoinTypeError,
)

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


def test_resolve_ape_network_ethereum_mainnet(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", ecosystem="ethereum", network="mainnet", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth")


def test_resolve_ape_network_base_mainnet(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", ecosystem="base", network="mainnet", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_ape_network_base_shorthand(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", network="base", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_ape_network_combined_choice(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", network="base:mainnet", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_ape_network_ecosystem_only_uses_mainnet(ens, mock_web3_ens, vitalik):
    actual = ens.resolve("vitalik.eth", ecosystem="base", use_cache=False)
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth", coin_type=BASE_COIN_TYPE)


def test_resolve_ape_network_mainnet_fork_uses_upstream_eth(ens, mock_web3_ens, vitalik):
    actual = ens.resolve(
        "vitalik.eth", ecosystem="ethereum", network="mainnet-fork", use_cache=False
    )
    assert actual == vitalik
    mock_web3_ens.address.assert_called_with("vitalik.eth")


def test_resolve_rejects_coin_type_and_network(ens):
    with pytest.raises(ConflictingResolveOptionsError):
        ens.resolve("vitalik.eth", coin_type=60, ecosystem="base")


def test_resolve_network_mainnet_is_ambiguous(ens):
    with pytest.raises(AmbiguousNetworkError, match="ambiguous"):
        ens.resolve("vitalik.eth", network="mainnet")


def test_resolve_local_network_coin_type(ens):
    with pytest.raises(LocalNetworkCoinTypeError):
        ens.resolve("vitalik.eth", ecosystem="ethereum", network="local")


def test_resolve_unknown_ape_network(ens):
    with pytest.raises(ApeENSException, match="Unknown Ape ecosystem or network"):
        ens.resolve("vitalik.eth", network="not-a-real-chain-xyz")


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
