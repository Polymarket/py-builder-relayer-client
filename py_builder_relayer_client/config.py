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


CONFIG = {
    137: ContractConfig(
        safe_factory=to_checksum_address("0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b"),
        safe_multisend=to_checksum_address(
            "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761"
        ),
    ),
    80002: ContractConfig(
        safe_factory=to_checksum_address("0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b"),
        safe_multisend=to_checksum_address(
            "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761"
        ),
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
