from ..config import ContractConfig
from ..constants.constants import (
    DEPOSIT_WALLET_DOMAIN_NAME,
    DEPOSIT_WALLET_DOMAIN_VERSION,
)
from ..models import (
    DepositWalletBatchRequest,
    DepositWalletCall,
    DepositWalletCreateRequest,
    DepositWalletTransactionArgs,
    TransactionType,
)
from ..signer import Signer


DEPOSIT_WALLET_TYPES = {
    "EIP712Domain": [
        {"name": "name", "type": "string"},
        {"name": "version", "type": "string"},
        {"name": "chainId", "type": "uint256"},
        {"name": "verifyingContract", "type": "address"},
    ],
    "Call": [
        {"name": "target", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "data", "type": "bytes"},
    ],
    "Batch": [
        {"name": "wallet", "type": "address"},
        {"name": "nonce", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
        {"name": "calls", "type": "Call[]"},
    ],
}


def _call_to_typed_data(call: DepositWalletCall):
    return {
        "target": call.target,
        "value": int(call.value),
        "data": call.data,
    }


def sign_batch(
    signer: Signer,
    chain_id: int,
    wallet_address: str,
    nonce: str,
    deadline: str,
    calls: list[DepositWalletCall],
) -> str:
    full_message = {
        "primaryType": "Batch",
        "types": DEPOSIT_WALLET_TYPES,
        "domain": {
            "name": DEPOSIT_WALLET_DOMAIN_NAME,
            "version": DEPOSIT_WALLET_DOMAIN_VERSION,
            "chainId": chain_id,
            "verifyingContract": wallet_address,
        },
        "message": {
            "wallet": wallet_address,
            "nonce": int(nonce),
            "deadline": int(deadline),
            "calls": [_call_to_typed_data(c) for c in calls],
        },
    }
    return signer.sign_typed_data(full_message)


def build_deposit_wallet_batch_request(
    signer: Signer,
    args: DepositWalletTransactionArgs,
    config: ContractConfig,
) -> DepositWalletBatchRequest:
    signature = sign_batch(
        signer=signer,
        chain_id=args.chain_id,
        wallet_address=args.wallet_address,
        nonce=args.nonce,
        deadline=args.deadline,
        calls=args.calls,
    )

    return DepositWalletBatchRequest(
        type=TransactionType.WALLET.value,
        from_address=args.from_address,
        to=config.deposit_wallet_factory,
        nonce=args.nonce,
        signature=signature,
        deposit_wallet=args.wallet_address,
        deadline=args.deadline,
        calls=args.calls,
    )


def build_deposit_wallet_create_request(
    from_address: str,
    config: ContractConfig,
) -> DepositWalletCreateRequest:
    return DepositWalletCreateRequest(
        type=TransactionType.WALLET_CREATE.value,
        from_address=from_address,
        to=config.deposit_wallet_factory,
    )
