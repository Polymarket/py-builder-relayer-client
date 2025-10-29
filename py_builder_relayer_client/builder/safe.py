from typing import List
from poly_eip712_structs import make_domain
from eth_abi.packed import encode_packed
from hexbytes import HexBytes

from ..config import ContractConfig
from ..models import (
    SafeTransaction,
    OperationType,
    TransactionRequest,
    SafeTransactionArgs,
    SplitSig,
    SignatureParams,
    TransactionType,
)
from ..encode.safe import create_safe_multisend_transaction
from .derive import derive
from ..signer import Signer
from ..model.safe_tx import SafeTx
from ..constants.constants import ZERO_ADDRESS


def aggregate_transaction(
    txns: List[SafeTransaction], safe_multisend: str
) -> SafeTransaction:
    """Aggregate multiple transactions into a single transaction"""
    if len(txns) == 1:
        return txns[0]
    else:
        return create_safe_multisend_transaction(txns, safe_multisend)


def split_signature(sig_hex: str) -> SplitSig:
    sig = HexBytes(sig_hex)
    if len(sig) != 65:
        raise ValueError(f"Invalid signature length: expected 65 bytes, got {len(sig)}")

    r = int.from_bytes(sig[0:32], "big")
    s = int.from_bytes(sig[32:64], "big")
    v_raw = sig[64]

    if v_raw in (0, 1):
        v = v_raw + 31
    elif v_raw in (27, 28):
        v = v_raw + 4
    else:
        raise ValueError("Invalid signature 'v' (expected 0,1,27,28)")

    return SplitSig(r=r, s=s, v=v)


def split_and_pack_sig(sig_hex: str) -> str:
    split_sig = split_signature(sig_hex)
    r = int(split_sig.r)
    s = int(split_sig.s)
    v = int(split_sig.v)
    packed = encode_packed(["uint256", "uint256", "uint8"], [r, s, v])
    return "0x" + packed.hex()


def create_safe_signature(signer: Signer, struct_hash: str) -> str:
    """
    Signs a struct hash to generate a safe signature
    """
    return signer.sign_eip712_struct_hash(struct_hash)


def create_struct_hash(
    chain_id: int,
    safe: str,
    to: str,
    value: str,
    data: str,
    operation: OperationType,
    safe_tx_gas: str,
    base_gas: str,
    gas_price: str,
    gas_token: str,
    refund_receiver: str,
    nonce: str,
) -> bytes:
    """
    Creates a Safe struct hash
    """
    safe_tx = SafeTx(
        to=to,
        value=int(value),
        data=data,
        operation=operation.value,
        safeTxGas=int(safe_tx_gas),
        baseGas=int(base_gas),
        gasPrice=int(gas_price),
        gasToken=gas_token,
        refundReceiver=refund_receiver,
        nonce=int(nonce),
    )
    return safe_tx.generate_struct_hash(
        make_domain(verifyingContract=safe, chainId=chain_id)
    )


def build_safe_transaction_request(
    signer: Signer,
    args: SafeTransactionArgs,
    config: ContractConfig,
    metadata: str = None,
) -> TransactionRequest:
    """
    Generate a Safe Transaction Request for the Relayer API
    """
    factory = config.safe_factory
    multisend = config.safe_multisend
    transaction = aggregate_transaction(args.transactions, multisend)
    safe_txn_gas = "0"
    base_gas = "0"
    gas_price = "0"
    gas_token = ZERO_ADDRESS
    refund_receiver = ZERO_ADDRESS
    safe_address = derive(args.from_address, factory)

    # generate the safe struct hash
    struct_hash = create_struct_hash(
        args.chain_id,
        safe_address,
        transaction.to,
        transaction.value,
        transaction.data,
        transaction.operation,
        safe_txn_gas,
        base_gas,
        gas_price,
        gas_token,
        refund_receiver,
        args.nonce,
    )

    sig = create_safe_signature(signer, struct_hash)

    packed_sig = split_and_pack_sig(sig)

    sig_params = SignatureParams(
        gas_price=gas_price,
        operation=str(transaction.operation.value),
        safe_txn_gas=safe_txn_gas,
        base_gas=base_gas,
        gas_token=gas_token,
        refund_receiver=refund_receiver,
    )

    if metadata is None:
        metadata = ""

    return TransactionRequest(
        type=TransactionType.SAFE.value,
        from_address=args.from_address,
        to=transaction.to,
        proxy=safe_address,
        value=transaction.value,
        data=transaction.data,
        nonce=args.nonce,
        signature=packed_sig,
        signature_params=sig_params,
        metadata=metadata,
    )
