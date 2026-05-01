from dotenv import load_dotenv
import os

from py_builder_relayer_client.client import RelayClient
from py_builder_signing_sdk.config import BuilderConfig, BuilderApiKeyCreds

load_dotenv()


def main():
    relayer_url = os.getenv("RELAYER_URL", "https://relayer-v2-staging.polymarket.dev/")
    chain_id = int(os.getenv("CHAIN_ID", 80002))
    pk = os.getenv("PK")

    builder_config = BuilderConfig(
        local_builder_creds=BuilderApiKeyCreds(
            key=os.getenv("BUILDER_API_KEY"),
            secret=os.getenv("BUILDER_SECRET"),
            passphrase=os.getenv("BUILDER_PASS_PHRASE"),
        )
    )

    client = RelayClient(relayer_url, chain_id, pk, builder_config)
    print(f"Expected deposit wallet: {client.get_expected_deposit_wallet()}")

    resp = client.deploy_deposit_wallet()
    print(resp)

    awaited_txn = resp.wait()
    print(awaited_txn)


main()
