from typing import List, Optional

from eth_abi import encode
from eth_abi.packed import encode_packed
from eth_utils import keccak, to_bytes, to_checksum_address, to_hex

from ..config import ContractConfig
from ..constants.constants import PROXY_INIT_CODE_HASH
from ..models import (
    ProxyTransactionArgs,
    SignatureParams,
    TransactionRequest,
    TransactionType,
)
from ..signer import Signer
from .derive import get_create2_address

DEFAULT_GAS_LIMIT = 10_000_000


def derive_proxy(address: str, proxy_factory: str) -> str:
    """
    Derive proxy wallet address from signer address and proxy factory
    """
    address = to_checksum_address(address)
    proxy_factory = to_checksum_address(proxy_factory)

    # Salt is keccak256(encodePacked(["address"], [address]))
    salt = keccak(encode_packed(["address"], [address]))

    proxy_address = get_create2_address(
        bytecode_hash=PROXY_INIT_CODE_HASH, from_address=proxy_factory, salt=salt
    )
    return to_checksum_address(proxy_address)


def create_struct_hash(
    from_addr: str,
    to_addr: str,
    data: str,
    tx_fee: str,
    gas_price: str,
    gas_limit: str,
    nonce: str,
    relay_hub_address: str,
    relay_address: str,
) -> bytes:
    """
    Create struct hash for proxy transaction
    """
    relay_hub_prefix = b"rlx:"
    encoded_from = (
        to_bytes(hexstr=from_addr)
        if from_addr.startswith("0x")
        else to_bytes(hexstr="0x" + from_addr)
    )
    encoded_to = (
        to_bytes(hexstr=to_addr)
        if to_addr.startswith("0x")
        else to_bytes(hexstr="0x" + to_addr)
    )
    encoded_data = (
        to_bytes(hexstr=data) if data.startswith("0x") else to_bytes(hexstr="0x" + data)
    )

    # Encode as 32-byte big-endian integers
    encoded_tx_fee = int(tx_fee).to_bytes(32, "big")
    encoded_gas_price = int(gas_price).to_bytes(32, "big")
    encoded_gas_limit = int(gas_limit).to_bytes(32, "big")
    encoded_nonce = int(nonce).to_bytes(32, "big")

    encoded_relay_hub = (
        to_bytes(hexstr=relay_hub_address)
        if relay_hub_address.startswith("0x")
        else to_bytes(hexstr="0x" + relay_hub_address)
    )
    encoded_relay = (
        to_bytes(hexstr=relay_address)
        if relay_address.startswith("0x")
        else to_bytes(hexstr="0x" + relay_address)
    )

    data_to_hash = (
        relay_hub_prefix
        + encoded_from
        + encoded_to
        + encoded_data
        + encoded_tx_fee
        + encoded_gas_price
        + encoded_gas_limit
        + encoded_nonce
        + encoded_relay_hub
        + encoded_relay
    )
    return keccak(data_to_hash)


def create_proxy_signature(signer: Signer, struct_hash: bytes) -> str:
    """
    Create proxy signature by signing the struct hash
    """
    return signer.sign_message(struct_hash)


def get_gas_limit(signer: Signer, to: str, args: ProxyTransactionArgs) -> str:
    """
    Get gas limit for proxy transaction
    Uses provided gasLimit if available, otherwise estimates or uses default
    """
    if args.gas_limit and args.gas_limit != "0":
        return args.gas_limit

    try:
        # Try to estimate gas if RPC URL is available
        gas_limit_bigint = signer.estimate_gas(
            from_address=args.from_address,
            to=to,
            data=args.data,
        )
        return str(gas_limit_bigint)
    except (ValueError, AttributeError) as e:
        # If estimation fails (no RPC URL or RPC error), use default
        print(
            f"Error estimating gas for proxy transaction, using default gas limit: {e}"
        )
        return str(DEFAULT_GAS_LIMIT)


def build_proxy_transaction_request(
    signer: Signer,
    args: ProxyTransactionArgs,
    config: ContractConfig,
    metadata: Optional[str] = None,
) -> TransactionRequest:
    """
    Generate a Proxy Transaction Request for the Relayer API
    """
    if config.proxy_factory is None or config.relay_hub is None:
        raise ValueError(
            "proxy_factory and relay_hub are required for PROXY transaction type"
        )

    proxy_wallet_factory = config.proxy_factory
    to = proxy_wallet_factory
    proxy = derive_proxy(args.from_address, proxy_wallet_factory)
    relayer_fee = "0"
    relay_hub = config.relay_hub
    gas_limit_str = get_gas_limit(signer, to, args)

    sig_params = SignatureParams(
        gas_price=args.gas_price,
        gas_limit=gas_limit_str,
        relayer_fee=relayer_fee,
        relay_hub=relay_hub,
        relay=args.relay,
    )

    tx_hash = create_struct_hash(
        args.from_address,
        to,
        args.data,
        relayer_fee,
        args.gas_price,
        gas_limit_str,
        args.nonce,
        relay_hub,
        args.relay,
    )

    sig = create_proxy_signature(signer, tx_hash)

    if metadata is None:
        metadata = ""

    return TransactionRequest(
        type=TransactionType.PROXY.value,
        from_address=args.from_address,
        to=to,
        proxy=proxy,
        data=args.data,
        nonce=args.nonce,
        signature=sig,
        signature_params=sig_params,
        metadata=metadata,
    )
