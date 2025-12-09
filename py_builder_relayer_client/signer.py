from typing import Optional
import os
import requests

from eth_account import Account
from eth_account.messages import encode_defunct
from hexbytes import HexBytes

from .utils.utils import prepend_zx


class Signer:
    def __init__(self, private_key: str, chain_id: int, rpc_url: Optional[str] = None):
        if private_key is None or chain_id is None:
            raise ValueError("invalid private key or chain_id")

        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.chain_id = chain_id
        # Use provided rpc_url, or fall back to environment variable
        self.rpc_url = rpc_url or os.getenv("RPC_URL")

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

    def sign_message(self, message_hash):
        """
        Signs a message hash (for proxy transactions)
        """
        if isinstance(message_hash, bytes):
            msg = encode_defunct(message_hash)
        else:
            msg = encode_defunct(HexBytes(message_hash))
        sig = Account.sign_message(msg, self.private_key).signature.hex()
        return prepend_zx(sig)

    def estimate_gas(self, from_address: str, to: str, data: str) -> int:
        """
        Estimate gas for a transaction by calling eth_estimateGas RPC method
        """
        if self.rpc_url is None:
            raise ValueError("RPC URL is required for gas estimation")

        # Prepare the transaction object for eth_estimateGas
        tx_params = {
            "from": from_address,
            "to": to,
            "data": data,
        }

        # JSON-RPC request payload
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_estimateGas",
            "params": [tx_params],
            "id": 1,
        }

        try:
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                raise ValueError(f"RPC error: {result['error']}")

            if "result" not in result:
                raise ValueError("No result in RPC response")

            # Convert hex string to int
            gas_hex = result["result"]
            if isinstance(gas_hex, str):
                # Remove '0x' prefix and convert to int
                gas_limit = int(gas_hex, 16)
            else:
                gas_limit = int(gas_hex)

            return gas_limit
        except requests.RequestException as e:
            raise ValueError(f"Failed to estimate gas: {e}")
        except (ValueError, KeyError) as e:
            raise ValueError(f"Invalid RPC response: {e}")
