> [!WARNING]
> **This package is deprecated.** Please migrate to the unified Polymarket SDK. Follow the [migration guide](https://docs.polymarket.com/migrate/clob-sdk-to-unified-sdk) to get started.

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

