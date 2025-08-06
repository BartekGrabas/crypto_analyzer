# Crypto Analyzer

Crypto Analyzer is a desktop application for visualising cryptocurrency market data.
It connects to the Binance exchange, renders candlestick charts and provides tools
for basic technical analysis.

## Installation

1. Clone the repository:
   ```bash
   git clone https://example.com/crypto_analyzer.git
   cd crypto_analyzer
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Required Environment Variables

Set your Binance credentials in the environment before launching:

```bash
export BINANCE_API_KEY="<your_api_key>"
export BINANCE_API_SECRET="<your_api_secret>"
```

## Running

Start the application with:

```bash
python -m src.main
```

## Optional Features

- **Binance Testnet** – enable the `testnet` flag in the configuration to
  connect to the Binance test environment.
- **Database Usage** – the application can store data in a local SQLite database
  located at `data/crypto_analyzer.db`.

## Dependency Management

Dependencies are listed in `requirements.txt` and kept in `setup.cfg` for
packaging. Use `pip install -r requirements.txt` during development or
`pip install .` to install the package.
