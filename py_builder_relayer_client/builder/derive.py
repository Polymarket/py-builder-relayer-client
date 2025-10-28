from eth_abi import encode
from eth_utils import to_bytes, to_checksum_address, keccak

from ..constants.constants import SAFE_INIT_CODE_HASH


def get_create2_address(bytecode_hash: str, from_address: str, salt: bytes) -> str:
    # Remove 0x prefix if present
    if bytecode_hash.startswith("0x"):
        bytecode_hash = bytecode_hash[2:]
    if from_address.startswith("0x"):
        from_address = from_address[2:]

    # Convert to bytes
    bytecode_hash_bytes = to_bytes(hexstr=bytecode_hash)
    from_address_bytes = to_bytes(hexstr=from_address)

    prefix = b"\xff"

    # CREATE2: keccak256(0xff + from + salt + keccak256(initCode))
    address_hash = keccak(prefix + from_address_bytes + salt + bytecode_hash_bytes)
    address = address_hash[-20:].hex()

    return to_checksum_address(address)


def derive(address: str, safe_factory: str) -> str:
    address = to_checksum_address(address)
    safe_factory = to_checksum_address(safe_factory)

    salt = keccak(encode(["address"], [address]))
    safe_address = get_create2_address(
        bytecode_hash=SAFE_INIT_CODE_HASH, from_address=safe_factory, salt=salt
    )
    return to_checksum_address(safe_address)
