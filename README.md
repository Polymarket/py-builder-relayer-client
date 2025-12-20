# py-builder-relayer-client

Python client library for interacting with the Polymarket Relayer infrastructure

## Installation

```bash
pip install py-builder-relayer-client
```

## Configuration

Create a `.env` file based on .env.example with credentials:

```env
RELAYER_URL=https://relayer-v2-staging.polymarket.dev/
CHAIN_ID=80002
PK=your_private_key_here
BUILDER_API_KEY=your_api_key
BUILDER_SECRET=your_api_secret
BUILDER_PASS_PHRASE=your_passphrase
```
## End-to-end example

The snippet below shows how to read configuration from the environment,
fetch builder headers from a local signing server, and then call the
Relayer with those headers attached.

import os
from py_builder_relayer_client import RelayerClient

relayer_url = os.environ["RELAYER_URL"]
signing_server_url = os.environ.get("SIGNING_SERVER_URL", "http://localhost:3000")

client = RelayerClient(base_url=relayer_url)

Obtain builder headers from the signing server
payload = {
"method": "POST",
"path": "/orders",
"body": "{}",
}
resp = client.session.post(
f"{signing_server_url}/sign",
json=payload,
timeout=10,
)
resp.raise_for_status()
builder_headers = resp.json()

Example: list markets while forwarding builder headers
markets = client.get_markets(
headers={
"x-builder-signature": builder_headers["signature"],
"x-builder-address": builder_headers["address"],
}
)

print(f"Loaded {len(markets)} markets")

This ties together the environment configuration, the builder signing
server and the Python Relayer client in a single runnable script.

