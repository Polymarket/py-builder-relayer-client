from poly_eip712_structs import EIP712Struct
from eth_utils import keccak, to_hex
from ..utils.utils import prepend_zx


class BaseEIP712Model(EIP712Struct):
    def generate_struct_hash(self, domain) -> str:
        struct_hash = keccak(self.signable_bytes(domain)).hex()
        return prepend_zx(struct_hash)
