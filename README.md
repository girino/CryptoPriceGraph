# Crypto Price Graph

A terminal-based cryptocurrency price graph generator that displays historical price data as ASCII/Unicode charts.

## Features

- **Multiple Graph Formats**: Candle charts or dot graphs
- **All Binance Intervals**: Support for all Binance time intervals (1m, 5m, 1h, 1d, etc.)
- **Auto-detection**: Automatically detects terminal size, Unicode support, and color support
- **Color Support**: Colored graphs for better readability (bullish/bearish candles)
- **Flexible Configuration**: Configure via JSON/YAML file or command-line arguments
- **Any Currency Pair**: Support for any base/quote currency pair available on Binance

## Requirements

- Python 3.7+
- `python-binance` library
- `pyyaml` library (optional, for YAML config support)

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd CryptoPriceGraph
   ```

2. Create and activate a virtual environment:
   ```powershell
   # Windows PowerShell
   .\create_graph_venv.ps1
   ```

   Or manually:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   venv\Scripts\activate     # On Windows
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

```powershell
# Windows PowerShell
.\run_graph.ps1 --base-currency BTC --quote-currency USDT --time-interval 1d --graph-format candle
```

Or directly:
```bash
python graph.py --base-currency BTC --quote-currency USDT --time-interval 1d --graph-format candle
```

### Configuration File

Create a `graph_config.json` file (you can copy from `graph_config.json.example`):

```json
{
  "base_currency": "BTC",
  "quote_currency": "USDT",
  "time_interval": "1d",
  "graph_format": "candle",
  "dot_values": "all",
  "use_unicode": "auto",
  "use_color": "auto"
}
```

### Command-Line Arguments

All parameters can be passed via command line (they take precedence over config file):

- `--base-currency`: Base currency symbol (e.g., BTC, ETH)
- `--quote-currency`: Quote currency symbol (e.g., USDT, BRL)
- `--time-interval`: Binance interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
- `--periods`: Number of periods to fetch (auto-calculated from screen width if not specified)
- `--graph-format`: `candle` or `dot`
- `--dot-values`: For dot format: `all`, `high`, `low`, or `close`
- `--width`: Graph width in characters (auto-detect if not specified)
- `--height`: Graph height in lines (auto-detect if not specified)
- `--use-unicode`: `auto`, `true`, or `false`
- `--use-color`: `auto`, `true`, or `false`
- `-f, --config`: Path to config file (default: `graph_config.json`)

### Examples

```bash
# Daily BTC/USDT candle chart
python graph.py --base-currency BTC --quote-currency USDT --time-interval 1d --graph-format candle

# Hourly ETH/BRL dot graph showing only high prices
python graph.py --base-currency ETH --quote-currency BRL --time-interval 1h --graph-format dot --dot-values high

# Force ASCII mode (no Unicode)
python graph.py --base-currency BTC --quote-currency USDT --use-unicode false

# Force color mode
python graph.py --base-currency BTC --quote-currency USDT --use-color true
```

## Graph Formats

### Candle Chart
Shows high, low, open, and close prices for each period:
- **Wick**: Vertical line from high to low
- **Body**: Horizontal bar from open to close
- **Colors**: Green for bullish (close > open), Red for bearish (close < open)

### Dot Graph
Shows individual price points:
- **High**: Cyan dot (▲ in Unicode, ^ in ASCII)
- **Low**: Yellow dot (▼ in Unicode, v in ASCII)
- **Close**: White dot (● in Unicode, o in ASCII)

## Auto-detection

The script automatically detects:
- **Terminal Size**: Uses available terminal width/height (fallback: 80x20)
- **Unicode Support**: Checks if terminal supports Unicode characters
- **Color Support**: Checks if terminal supports ANSI color codes
- **Optimal Periods**: Calculates how many periods fit on screen based on graph format

## License

[Add your license here]

