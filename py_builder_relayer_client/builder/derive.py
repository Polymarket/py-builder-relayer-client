from eth_abi import encode
from eth_abi.packed import encode_packed
from eth_utils import to_bytes, to_checksum_address, keccak

from ..constants.constants import SAFE_INIT_CODE_HASH, PROXY_INIT_CODE_HASH

ERC1967_CONST1 = "0xcc3735a920a3ca505d382bbc545af43d6000803e6038573d6000fd5b3d6000f3"
ERC1967_CONST2 = "0x5155f3363d3d373d3d363d7f360894a13ba1a3210667c828492db98dca3e2076"
ERC1967_PREFIX = 0x61003D3D8160233D3973


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


def derive_proxy_wallet(address: str, proxy_factory: str) -> str:
    address = to_checksum_address(address)
    proxy_factory = to_checksum_address(proxy_factory)

    salt = keccak(encode_packed(["address"], [address]))
    proxy_address = get_create2_address(
        bytecode_hash=PROXY_INIT_CODE_HASH, from_address=proxy_factory, salt=salt
    )
    return to_checksum_address(proxy_address)


def init_code_hash_erc1967(implementation: str, args: bytes) -> str:
    implementation = to_checksum_address(implementation)
    n = len(args)
    combined = ERC1967_PREFIX + (n << 56)
    init_code = (
        combined.to_bytes(10, "big")
        + to_bytes(hexstr=implementation)
        + to_bytes(hexstr="0x6009")
        + to_bytes(hexstr=ERC1967_CONST2)
        + to_bytes(hexstr=ERC1967_CONST1)
        + args
    )
    return "0x" + keccak(init_code).hex()


def derive_deposit_wallet(owner: str, factory: str, implementation: str) -> str:
    owner = to_checksum_address(owner)
    factory = to_checksum_address(factory)
    implementation = to_checksum_address(implementation)

    wallet_id = to_bytes(hexstr=owner).rjust(32, b"\x00")
    args = encode(["address", "bytes32"], [factory, wallet_id])
    salt = keccak(args)
    bytecode_hash = init_code_hash_erc1967(implementation, args)
    wallet_address = get_create2_address(
        bytecode_hash=bytecode_hash, from_address=factory, salt=salt
    )
    return to_checksum_address(wallet_address)
