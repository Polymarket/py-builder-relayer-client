from py_builder_relayer_client.client import RelayClient

from dotenv import load_dotenv
import os

load_dotenv()


def main():
    print("starting...")
    relayer_url = os.getenv(
        "RELAYER_URL_PROD", "https://relayer-v2-staging.polymarket.dev/"
    )
    chain_id = int(os.getenv("CHAIN_ID_PROD", 80002))
    client = RelayClient(relayer_url, chain_id)

    resp = client.get_transaction("019a2e46-3fc9-77d7-9ad7-451288a2a8a6")
    print(resp)


main()
