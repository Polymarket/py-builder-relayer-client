from unittest import TestCase

from py_builder_relayer_client.builder.derive import derive


class TestDerive(TestCase):

    def test_derive_safe(self):
        address = "0x6e0c80c90ea6c15917308F820Eac91Ce2724B5b5"
        safe_factory = "0xaacFeEa03eb1561C4e67d661e40682Bd20E3541b"
        safe = derive(address, safe_factory)
        expected_safe = "0x6d8c4e9aDF5748Af82Dabe2C6225207770d6B4fa"
        self.assertEqual(expected_safe, safe)
