# Pydantic AI Trading Agent

A sophisticated Uniswap V3 trading agent built with Python, leveraging Pydantic
for data validation and Web3.py for blockchain interactions.

## Features:.

- Sepolia testnet support
- Uniswap V3 pool investigation
- Robust error handling
- Detailed logging
- Environment-based configuration
- Real-time price data from Dune Analytics

## Prerequisites

- Python 3.8+
- Poetry
- Ethereum wallet with Sepolia testnet ETH
- Dune Analytics API key

## Setup

1. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone the repository

```bash
git clone https://github.com/yourusername/pydantic-trader.git
cd pydantic-trader
```

3. Install dependencies

```bash
poetry install
```

4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your:

- `ALCHEMY_RPC_URL`: Alchemy Sepolia endpoint
- `WALLET_PRIVATE_KEY`: Your Ethereum wallet private key
- `DUNE_API_KEY`: Your Dune Analytics API key
- `DUNE_API_REQUEST_TIMEOUT`: Timeout in seconds (recommended: 120)

## Usage

Run the main trading script:

```bash
poetry run python pydantic_trader/pydantic_trader_main.py
```

### Real-Time Price Fetching

The system uses Dune Analytics to fetch real-time ETH prices:

```bash
# Run the price comparison script
poetry run python -m pydantic_trader.scripts.run_realtime_price
```

## Development

### Code Formatting

```bash
poetry run black .
poetry run isort .
```

### Running Tests

```bash
# Run all tests
./pydantic_trader/tests/run_tests.sh

# Run specific tests
./pydantic_trader/tests/run_tests.sh pydantic_trader/tests/test_realtime_price.py

# For more options
./pydantic_trader/tests/run_tests.sh --help
```

See `pydantic_trader/tests/testREADME.md` for detailed testing instructions.

# Security Recommendations

- Never commit sensitive information to version control
- Use hardware wallets for production
- Implement proper key rotation and management strategies
- Ensure `.env` is added to `.gitignore`

## Current Pools Investigated

- UNI/ETH 0.3% Pool
- USDC/ETH 0.3% Pool (used for real-time price fetching)

## Disclaimer

This is a research and educational project. Use at your own risk.
