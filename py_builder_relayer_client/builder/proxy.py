from eth_utils import keccak, to_bytes
from hexbytes import HexBytes

from ..config import ContractConfig
from ..gas import DEFAULT_GAS_LIMIT
from ..models import (
    ProxyTransactionArgs,
    TransactionRequest,
    SignatureParams,
    TransactionType,
)
from .derive import derive_proxy_wallet
from ..signer import Signer


def create_proxy_struct_hash(
    from_address: str,
    to: str,
    data: str,
    tx_fee: str,
    gas_price: str,
    gas_limit: str,
    nonce: str,
    relay_hub_address: str,
    relay_address: str,
) -> str:
    """
    Creates a Proxy struct hash via raw byte concatenation + keccak256
    """
    prefix = b"rlx:"

    from_addr_bytes = HexBytes(from_address)  # 20 bytes
    to_addr_bytes = HexBytes(to)  # 20 bytes

    data_bytes = (
        to_bytes(hexstr=data) if data.startswith("0x") else to_bytes(hexstr="0x" + data)
    )

    tx_fee_bytes = int(tx_fee).to_bytes(32, "big")
    gas_price_bytes = int(gas_price).to_bytes(32, "big")
    gas_limit_bytes = int(gas_limit).to_bytes(32, "big")
    nonce_bytes = int(nonce).to_bytes(32, "big")

    relay_hub_bytes = HexBytes(relay_hub_address)  # 20 bytes
    relay_bytes = HexBytes(relay_address)  # 20 bytes

    message = (
        prefix
        + from_addr_bytes
        + to_addr_bytes
        + data_bytes
        + tx_fee_bytes
        + gas_price_bytes
        + gas_limit_bytes
        + nonce_bytes
        + relay_hub_bytes
        + relay_bytes
    )

    return "0x" + keccak(message).hex()


def create_proxy_signature(signer: Signer, struct_hash: str) -> str:
    """
    Signs a struct hash to generate a proxy signature
    """
    return signer.sign_eip712_struct_hash(struct_hash)


def build_proxy_transaction_request(
    signer: Signer,
    args: ProxyTransactionArgs,
    config: ContractConfig,
    metadata: str = None,
) -> TransactionRequest:
    """
    Generate a Proxy Transaction Request for the Relayer API
    """
    proxy_wallet = derive_proxy_wallet(args.from_address, config.proxy_factory)

    gas_limit = str(DEFAULT_GAS_LIMIT)
    if args.gas_limit is not None and args.gas_limit != "0":
        gas_limit = args.gas_limit

    struct_hash = create_proxy_struct_hash(
        from_address=args.from_address,
        to=config.proxy_factory,
        data=args.data,
        tx_fee="0",
        gas_price=args.gas_price,
        gas_limit=gas_limit,
        nonce=args.nonce,
        relay_hub_address=config.relay_hub,
        relay_address=args.relay,
    )

    sig = create_proxy_signature(signer, struct_hash)

    sig_params = SignatureParams(
        gas_price=args.gas_price,
        gas_limit=gas_limit,
        relayer_fee="0",
        relay_hub=config.relay_hub,
        relay=args.relay,
    )

    if metadata is None:
        metadata = ""

    return TransactionRequest(
        type=TransactionType.PROXY.value,
        from_address=args.from_address,
        to=config.proxy_factory,
        proxy=proxy_wallet,
        data=args.data,
        nonce=args.nonce,
        signature=sig,
        signature_params=sig_params,
        metadata=metadata,
    )
