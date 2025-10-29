from unittest import TestCase

from py_builder_relayer_client.builder.create import (
    create_safe_create_signature,
    create_safe_create_struct_hash,
)
from py_builder_relayer_client.signer import Signer
from py_builder_relayer_client.config import get_contract_config


class TestCreate(TestCase):

    def test_create_safe_create_struct_hash(self):
        chain_id = 137
        config = get_contract_config(chain_id)
        factory = config.safe_factory

        payment_token = "0x0000000000000000000000000000000000000000"
        payment = "0"
        payment_receiver = "0x0000000000000000000000000000000000000000"

        expected_struct_hash = (
            "0x563ac315294c5be01ab1f3b04a5abdfa39e8317a9d90679d4e63caf760b126a4"
        )
        struct_hash = create_safe_create_struct_hash(
            factory, chain_id, payment_token, payment, payment_receiver
        )

        self.assertEqual(expected_struct_hash, struct_hash)

    def test_create_safe_create_signature(self):
        chain_id = 137

        # Publicly known PK
        signer = Signer(
            private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
            chain_id=chain_id,
        )
        config = get_contract_config(chain_id)
        factory = config.safe_factory

        payment_token = "0x0000000000000000000000000000000000000000"
        payment = "0"
        payment_receiver = "0x0000000000000000000000000000000000000000"

        expected_sig = "0xe3e791c24134b7bebe93b4771bd07c7fe7bbe115eeb0bf629ac3b7a435e7ac8d05f979729d873f7d0e16205becf48ee450aa382bc28c65eedcd6454e81d81f921b"
        sig = create_safe_create_signature(
            signer, factory, chain_id, payment_token, payment, payment_receiver
        )

        self.assertEqual(expected_sig, sig)
