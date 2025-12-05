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

   **Windows PowerShell:**
   ```powershell
   .\create_venv.ps1
   ```

   **Linux/macOS/Cygwin (Bash):**
   ```bash
   ./create_venv.sh
   ```

   Or manually:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac/Cygwin
   venv\Scripts\activate     # On Windows
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

**Windows PowerShell:**
```powershell
.\run.ps1 --base-currency BTC --quote-currency USDT --time-interval 1d --graph-format candle
```

**Linux/macOS/Cygwin (Bash):**
```bash
./run.sh --base-currency BTC --quote-currency USDT --time-interval 1d --graph-format candle
```

**Direct Python execution:**
```bash
python graph.py --base-currency BTC --quote-currency USDT --time-interval 1d --graph-format candle
```

Note: The bash scripts automatically detect if running on Cygwin and use the appropriate virtual environment (`venv-cygwin` for Cygwin, `venv-unix` for other Unix systems). PowerShell scripts use `venv-windows`.

### Configuration File

Create a `config.json` file (you can copy from `config.json.example`):

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
- `-f, --config`: Path to config file (default: `config.json`)

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

## Platform Support

- **Windows**: Use PowerShell scripts (`create_venv.ps1`, `run.ps1`) - creates `venv-windows/`
- **Linux/macOS**: Use Bash scripts (`create_venv.sh`, `run.sh`) - creates `venv-unix/`
- **Cygwin**: Use Bash scripts (`create_venv.sh`, `run.sh`) - automatically detects Cygwin and creates `venv-cygwin/`

The bash scripts automatically detect the platform and use the appropriate virtual environment directory.

## Troubleshooting

### Virtual Environment Issues
- If you get "virtual environment does not exist" errors, make sure you've run the appropriate setup script first
- On Unix systems, you may need to make scripts executable: `chmod +x create_venv.sh run.sh`

### Unicode/Color Display Issues
- If Unicode characters don't display correctly, use `--use-unicode false`
- If colors don't work, check your terminal's ANSI color support or use `--use-color false`
- Some terminals may require specific settings for UTF-8 encoding

### Binance API Issues
- The script uses public Binance API endpoints (no API keys required)
- If you encounter rate limiting or connection errors, wait a moment and try again
- Ensure you have an active internet connection

## License

This project is licensed under **Girino's Anarchist License (GAL)**.

See [LICENSE](LICENSE) file for details, or visit https://license.girino.org

