from poly_eip712_structs import make_domain

from ..signer import Signer
from .derive import derive
from ..constants.constants import SAFE_FACTORY_NAME
from ..models import (
    SafeCreateTransactionArgs,
    SignatureParams,
    TransactionType,
    TransactionRequest,
)
from ..config import ContractConfig
from ..model.create_proxy import CreateProxy


def create_safe_create_signature(
    signer: Signer,
    safe_factory: str,
    chain_id: int,
    payment_token: str,
    payment: str,
    payment_receiver: str,
) -> str:
    struct_hash = create_safe_create_struct_hash(
        safe_factory, chain_id, payment_token, payment, payment_receiver
    )
    sig = signer.sign(struct_hash)
    return sig


def create_safe_create_struct_hash(
    safe_factory: str,
    chain_id: int,
    payment_token: str,
    payment: str,
    payment_receiver: str,
) -> str:

    create_proxy = CreateProxy(
        paymentToken=payment_token,
        payment=int(payment),
        paymentReceiver=payment_receiver,
    )
    struct_hash = create_proxy.generate_struct_hash(
        make_domain(
            name=SAFE_FACTORY_NAME, verifyingContract=safe_factory, chainId=chain_id
        )
    )
    return struct_hash


def build_safe_create_transaction_request(
    signer: Signer,
    args: SafeCreateTransactionArgs,
    config: ContractConfig,
):
    factory = config.safe_factory
    safe_address = derive(args.from_address, factory)

    sig = create_safe_create_signature(
        signer,
        factory,
        args.chain_id,
        args.payment_token,
        args.payment,
        args.payment_receiver,
    )

    sig_params = SignatureParams(
        payment_token=args.payment_token,
        payment=args.payment,
        payment_receiver=args.payment_receiver,
    )

    return TransactionRequest(
        type=TransactionType.SAFE_CREATE.value,
        from_address=args.from_address,
        to=factory,
        proxy=safe_address,
        data="0x",
        signature=sig,
        signature_params=sig_params,
    )
