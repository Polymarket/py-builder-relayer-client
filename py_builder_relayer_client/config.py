from dataclasses import dataclass

from eth_utils import to_checksum_address

from .exceptions import RelayerClientException


@dataclass
class ContractConfig:
    """
    Contract Configuration
    """

    safe_factory: str

    safe_multisend: str

    proxy_factory: str = None

    relay_hub: str = None


CONFIG = {
    137: ContractConfig(
        safe_factory=to_checksum_address("0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b"),
        safe_multisend=to_checksum_address(
            "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761"
        ),
        proxy_factory=to_checksum_address("0xaB45c5A4B0c941a2F231C04C3f49182e1A254052"),
        relay_hub=to_checksum_address("0xD216153c06E857cD7f72665E0aF1d7D82172F494"),
    ),
    80002: ContractConfig(
        safe_factory=to_checksum_address("0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b"),
        safe_multisend=to_checksum_address(
            "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761"
        ),
        # Proxy factory unsupported on Amoy testnet
        proxy_factory=None,
        relay_hub=None,
    ),
}


def get_contract_config(chain_id: int) -> ContractConfig:
    """
    Gets the contract config
    """
    config = CONFIG.get(chain_id)
    if config is None:
        raise RelayerClientException(f"Invalid chainID: {chain_id}")

    return config
