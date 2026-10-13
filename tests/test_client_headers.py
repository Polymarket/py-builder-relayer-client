import json
from unittest import TestCase
from unittest.mock import Mock

from py_builder_relayer_client.client import RelayClient


# Public Hardhat/Anvil fixture key. This is not a live credential.
TEST_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"


class TestGenerateBuilderHeaders(TestCase):

    def _client(self):
        client = RelayClient(
            relayer_url="http://localhost:8080",
            chain_id=137,
            private_key=TEST_PRIVATE_KEY,
            builder_config=Mock(),
        )
        client.builder_config.generate_builder_headers = Mock(return_value=None)
        return client

    def test_body_is_serialized_as_valid_json(self):
        """
        The body handed to BuilderConfig.generate_builder_headers must be a
        valid JSON string equal to json.dumps(body) — matching the bytes the
        HTTP layer puts on the wire via `requests(..., json=body)`.
        """
        client = self._client()
        body = {"from": "0xabc", "to": "0xdef", "nonce": "0"}

        client._generate_builder_headers("POST", "/submit", body)

        forwarded = client.builder_config.generate_builder_headers.call_args[0][2]
        # Must round-trip as JSON
        self.assertEqual(body, json.loads(forwarded))
        # And must equal the exact wire-format string
        self.assertEqual(json.dumps(body), forwarded)
        # Specifically: not Python repr (single quotes)
        self.assertNotIn("'", forwarded)

    def test_none_body_is_passed_through(self):
        client = self._client()
        client._generate_builder_headers("GET", "/transaction", None)
        forwarded = client.builder_config.generate_builder_headers.call_args[0][2]
        self.assertIsNone(forwarded)
