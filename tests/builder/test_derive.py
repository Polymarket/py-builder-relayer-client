from unittest import TestCase

from py_builder_relayer_client.builder.derive import derive, derive_deposit_wallet


class TestDerive(TestCase):

    def test_derive_safe(self):
        address = "0x6e0c80c90ea6c15917308F820Eac91Ce2724B5b5"
        safe_factory = "0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b"
        safe = derive(address, safe_factory)
        expected_safe = "0x6d8c4e9aDF5748Af82Dabe2C6225207770d6B4fa"
        self.assertEqual(expected_safe, safe)

    def test_derive_deposit_wallet(self):
        owner = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        factory = "0x801c740Bcd28531d75a5da176D5511F3329Ab049"
        implementation = "0x24f3257BF9451bA575E864777ab6f8D7Eac0139B"
        wallet = derive_deposit_wallet(owner, factory, implementation)
        expected_wallet = "0x63cB1B4eC2F274Ed553aD5079c6A2542d1c02bd7"
        self.assertEqual(expected_wallet, wallet)
