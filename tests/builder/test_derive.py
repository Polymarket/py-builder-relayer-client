from unittest import TestCase

from py_builder_relayer_client.builder.derive import (
    derive,
    derive_beacon_deposit_wallet,
    derive_deposit_wallet,
    derive_uups_deposit_wallet,
)


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
        expected_wallet = "0x3c6D4D368D1Af2C1555Effbf17Da30Add851A6Ae"
        self.assertEqual(expected_wallet, wallet)

    def test_derive_deposit_wallet_polygon_factory(self):
        owner = "0xA60601A4d903af91855C52BFB3814f6bA342f201"
        factory = "0x00000000000Fb5C9ADea0298D729A0CB3823Cc07"
        implementation = "0x58CA52ebe0DadfdF531Cde7062e76746de4Db1eB"
        wallet = derive_uups_deposit_wallet(owner, factory, implementation)
        expected_wallet = "0x8b60BF0f650Bf7a0d93F10D72375b37De18F8c40"
        self.assertEqual(expected_wallet, wallet)

    def test_derive_beacon_deposit_wallet_polygon_factory(self):
        owner = "0x0000000000000000000000000000000000000001"
        factory = "0x00000000000Fb5C9ADea0298D729A0CB3823Cc07"
        beacon = "0x7A18EDfe055488A3128f01F563e5B479D92ffc3a"
        wallet = derive_beacon_deposit_wallet(owner, factory, beacon)
        expected_wallet = "0x94bF330955A0b957662fEaF878dE77bf25f76cD9"
        self.assertEqual(expected_wallet, wallet)
