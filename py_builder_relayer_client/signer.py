from eth_account import Account
from eth_account.messages import encode_defunct
from hexbytes import HexBytes
from .utils.utils import prepend_zx


class Signer:
    def __init__(self, private_key: str, chain_id: int):
        if private_key is None or chain_id is None:
            raise ValueError("invalid private key or chain_id")

        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.chain_id = chain_id

    def address(self):
        return self.account.address

    def get_chain_id(self):
        return self.chain_id

    def sign(self, message_hash):
        """
        Signs a message hash
        """
        return prepend_zx(
            Account._sign_hash(message_hash, self.private_key).signature.hex()
        )

    def sign_eip712_struct_hash(self, message_hash):
        """
        Applies EIP191 prefix then signs a EIP712 struct hash
        """
        msg = encode_defunct(HexBytes(message_hash))
        sig = Account.sign_message(msg, self.private_key).signature.hex()
        return prepend_zx(sig)
