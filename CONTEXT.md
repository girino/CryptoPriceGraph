# CryptoPriceGraph - Project Context

## Project Overview
Terminal-based cryptocurrency price graph generator that displays historical price data as ASCII/Unicode charts. Originally developed as part of the TenDaysBTCPrice project, then separated into its own repository.

## Development History

### Key Features Implemented
1. **Graph Formats**:
   - Candle charts (high, low, open, close with wick and body)
   - Dot graphs (high, low, close as separate symbols)

2. **Auto-detection**:
   - Terminal size detection (fallback: 80x20)
   - Unicode support detection (UTF-8 encoding check)
   - Color support detection (TTY, NO_COLOR env var, Windows detection)
   - Optimal periods calculation based on screen width

3. **Configuration System**:
   - JSON/YAML config file support
   - Command-line arguments (CLI takes precedence over config)
   - Auto-detection with manual override options

4. **Color Support**:
   - ANSI color codes for terminal output
   - Green/Red for bullish/bearish candles
   - Cyan/Yellow/White for high/low/close dots
   - Auto-detection with manual override

### Technical Implementation Details

#### Binance API Integration
- Uses `python-binance` library (no API keys needed for public data)
- Supports all Binance intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
- Note: `1s` interval was removed (not supported by Binance API)
- Uses interval strings directly (e.g., `'1m'`) instead of `Client.KLINE_INTERVAL_*` constants

#### Graph Rendering
- **Candle Graph**:
  - Unicode: `│` for wick, `█` for body
  - ASCII: `|` for wick, `#` for body
  - Body drawn from open to close
  - Wick drawn from high to low (full range)
  - Colors: Green (bullish), Red (bearish), Gray (wick)

- **Dot Graph**:
  - Unicode: `▲` (high), `▼` (low), `●` (close)
  - ASCII: `^` (high), `v` (low), `o` (close)
  - Colors: Cyan (high), Yellow (low), White (close)
  - Can show all values or filter by `dot_values` parameter

#### Graph Layout
- Y-axis: Price labels on left (10 chars reserved)
- X-axis: Timestamps at bottom (start, middle, end)
- Frame: Unicode (`│`, `+`, `─`) or ASCII (`|`, `+`, `-`)
- Legend: Shows currency pair, interval, price range
- Format info: Shows graph format, Unicode/Color status

#### Key Functions
- `load_config()`: Loads JSON/YAML config files
- `parse_arguments()`: CLI argument parsing
- `get_config()`: Merges CLI args and config file (CLI precedence)
- `get_historical_prices()`: Fetches klines from Binance
- `get_terminal_size()`: Detects terminal dimensions
- `detect_unicode_support()`: Checks UTF-8 encoding support
- `detect_color_support()`: Checks ANSI color support
- `should_use_unicode()`: Determines Unicode usage
- `should_use_color()`: Determines color usage
- `calculate_price_range()`: Calculates min/max with 5% padding
- `price_to_y()`: Maps price to Y-coordinate
- `format_price()`: Formats price labels
- `calculate_graph_dimensions()`: Calculates graph area (reserves space for axes/labels)
- `calculate_optimal_periods()`: Determines periods based on screen width
- `render_candle_graph()`: Renders candle chart (returns canvas with (char, color) tuples)
- `render_dot_graph()`: Renders dot chart (returns canvas with (char, color) tuples)
- `render_graph()`: Orchestrates rendering, adds axes, labels, legend, handles truncation

### Issues Fixed During Development
1. **Graph overflow**: Adjusted dimensions to reserve space for Y-axis labels and margins
2. **X-axis label misalignment**: Fixed label positioning to be relative to graph area, centered on data points
3. **Candle rendering issues**: Refactored to draw wick first (high to low), then body (open to close)
4. **Close marker confusion**: Removed close marker (body separation makes it clear)
5. **ASCII frame using Unicode**: Fixed frame symbols to use ASCII when `use_unicode=False`
6. **Color argument missing**: Added `--use-color` to argument parser
7. **Debug output**: Removed all debug print statements for clean output

### Configuration Parameters

#### Config File (`graph_config.json`)
```json
{
  "base_currency": "BTC",
  "quote_currency": "USDT",
  "time_interval": "1d",
  "periods": null,  // null = auto-calculate
  "graph_format": "candle",
  "dot_values": "all",
  "width": null,  // null = auto-detect
  "height": null,  // null = auto-detect
  "use_unicode": "auto",
  "use_color": "auto"
}
```

#### Command-Line Arguments
- `--base-currency`: Base currency (e.g., BTC, ETH)
- `--quote-currency`: Quote currency (e.g., USDT, BRL)
- `--time-interval`: Binance interval string
- `--periods`: Number of periods (null = auto)
- `--graph-format`: `candle` or `dot`
- `--dot-values`: `all`, `high`, `low`, or `close`
- `--width`: Graph width in chars (null = auto)
- `--height`: Graph height in lines (null = auto)
- `--use-unicode`: `auto`, `true`, or `false`
- `--use-color`: `auto`, `true`, or `false`
- `-f, --config`: Config file path (default: `graph_config.json`)

### Dependencies
- `python-binance==1.0.15` - Binance API client
- `pyyaml>=6.0` - YAML config support (optional)

### File Structure
```
CryptoPriceGraph/
├── graph.py                    # Main script
├── graph_config.json           # User config (gitignored)
├── graph_config.json.example   # Config template
├── requirements.txt            # Dependencies
├── create_graph_venv.ps1       # Virtual environment setup
├── run_graph.ps1               # PowerShell runner script
├── README.md                   # Documentation
├── CONTEXT.md                  # This file
└── .gitignore                  # Git ignore rules
```

### Usage Examples
```powershell
# Basic candle chart
.\run_graph.ps1 --base-currency BTC --quote-currency USDT --time-interval 1d --graph-format candle

# Dot graph with only high prices
.\run_graph.ps1 --base-currency ETH --quote-currency BRL --time-interval 1h --graph-format dot --dot-values high

# Force ASCII and color
.\run_graph.ps1 --base-currency BTC --quote-currency USDT --use-unicode false --use-color true
```

### Design Decisions
1. **No API keys needed**: Uses public Binance API endpoints
2. **CLI precedence**: Command-line arguments override config file
3. **Auto-detection defaults**: All auto-detection can be manually overridden
4. **Terminal compatibility**: Works with both Unicode and ASCII terminals
5. **Color optional**: Colors enhance but aren't required
6. **Truncation handling**: Graph output is truncated to fit terminal width
7. **Canvas-based rendering**: Uses 2D canvas array for precise character placement

### Future Considerations
- Could add more graph types (line chart, area chart)
- Could add volume visualization
- Could add technical indicators overlay
- Could add interactive mode (scroll through time)
- Could add export to file/image

## Notes
- Originally part of TenDaysBTCPrice project
- Separated into own repository on 2025-12-05
- All debug output removed for production use
- Tested on Windows PowerShell with modern terminals

