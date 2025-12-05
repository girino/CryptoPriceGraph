import requests
import datetime
import json
import argparse
import os
import shutil
import sys
from binance.client import Client

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Candle colors
    BULLISH = BRIGHT_GREEN  # Green for bullish (close > open)
    BEARISH = BRIGHT_RED    # Red for bearish (close < open)
    WICK = BRIGHT_BLACK     # Gray for wick
    
    # Dot colors
    HIGH_COLOR = BRIGHT_CYAN
    LOW_COLOR = BRIGHT_YELLOW
    CLOSE_COLOR = BRIGHT_WHITE

def load_config(config_path='graph_config.json'):
    """Load configuration from JSON or YAML file."""
    if not os.path.exists(config_path):
        return {}
    
    try:
        with open(config_path, 'r') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                try:
                    import yaml
                    return yaml.safe_load(f) or {}
                except ImportError:
                    print("Warning: YAML support requires 'pyyaml' package. Install with: pip install pyyaml")
                    return {}
            else:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load config file {config_path}: {e}")
        return {}

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Cryptocurrency Price Graph Generator')
    parser.add_argument('--base-currency', type=str, help='Base currency symbol (e.g., BTC, ETH)')
    parser.add_argument('--quote-currency', type=str, help='Quote currency symbol (e.g., USDT, BRL)')
    parser.add_argument('--time-interval', type=str, help='Binance interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)')
    parser.add_argument('--periods', type=int, help='Number of periods to fetch (optional, auto-calculated from screen width if not specified)')
    parser.add_argument('--graph-format', type=str, choices=['candle', 'dot'], help='Graph format: candle or dot')
    parser.add_argument('--dot-values', type=str, choices=['all', 'high', 'low', 'close'], help='For dot format: all, high, low, or close')
    parser.add_argument('--width', type=int, help='Graph width in characters (optional, auto-detect default)')
    parser.add_argument('--height', type=int, help='Graph height in lines (optional, auto-detect default)')
    parser.add_argument('--use-unicode', type=str, choices=['auto', 'true', 'false'], help='Use unicode: auto, true, or false')
    parser.add_argument('--use-color', type=str, choices=['auto', 'true', 'false'], help='Use colors: auto, true, or false')
    parser.add_argument('-f', '--config', type=str, default='graph_config.json', help='Path to config file (default: graph_config.json)')
    return parser.parse_args()

def get_config():
    """Get configuration from command line args and config file, with CLI taking precedence."""
    args = parse_arguments()
    config = load_config(args.config)
    
    # Build final config with CLI args taking precedence
    final_config = {}
    
    # Base and quote currencies
    base_currency = args.base_currency if args.base_currency else config.get('base_currency', 'BTC')
    quote_currency = args.quote_currency if args.quote_currency else config.get('quote_currency', 'USDT')
    
    final_config['base_currency'] = base_currency
    final_config['quote_currency'] = quote_currency
    
    # Build ticker name (for Binance: BASEQUOTE, e.g., BTCUSDT)
    final_config['ticker_name'] = f"{base_currency}{quote_currency}"
    
    # Time interval
    final_config['time_interval'] = args.time_interval if args.time_interval else config.get('time_interval', '1d')
    
    # Periods - calculate from screen width if not specified
    if args.periods is not None:
        final_config['periods'] = args.periods
    elif 'periods' in config and config['periods'] is not None:
        final_config['periods'] = config['periods']
    else:
        # Auto-calculate based on terminal width
        # Will be calculated in main() after we know the graph width
        final_config['periods'] = None
    
    # Graph format
    final_config['graph_format'] = args.graph_format if args.graph_format else config.get('graph_format', 'candle')
    
    # Dot values
    final_config['dot_values'] = args.dot_values if args.dot_values else config.get('dot_values', 'all')
    
    # Width and height
    final_config['width'] = args.width if args.width is not None else config.get('width')
    final_config['height'] = args.height if args.height is not None else config.get('height')
    
    # Unicode usage
    use_unicode_arg = getattr(args, 'use_unicode', None)
    final_config['use_unicode'] = use_unicode_arg if use_unicode_arg is not None else config.get('use_unicode', 'auto')
    
    # Color usage
    use_color_arg = getattr(args, 'use_color', None)
    final_config['use_color'] = use_color_arg if use_color_arg is not None else config.get('use_color', 'auto')
    
    return final_config

# Binance interval mapping - using string literals (Binance API accepts these directly)
# Note: 1-second intervals are not supported for historical klines
VALID_INTERVALS = {
    '1m': '1m',
    '3m': '3m',
    '5m': '5m',
    '15m': '15m',
    '30m': '30m',
    '1h': '1h',
    '2h': '2h',
    '4h': '4h',
    '6h': '6h',
    '8h': '8h',
    '12h': '12h',
    '1d': '1d',
    '3d': '3d',
    '1w': '1w',
    '1M': '1M',
}

def get_historical_prices(client, ticker_name, interval_str, periods):
    """Fetch historical price data from Binance."""
    if interval_str not in VALID_INTERVALS:
        raise ValueError(f"Invalid interval: {interval_str}. Valid intervals: {list(VALID_INTERVALS.keys())}")
    
    interval = VALID_INTERVALS[interval_str]
    end_time = datetime.datetime.now()
    
    # Fetch klines using the interval string directly
    klines = client.get_klines(symbol=ticker_name, interval=interval, limit=periods)
    
    if not klines:
        raise ValueError(f"No data returned for {ticker_name} with interval {interval_str}")
    
    # Extract prices and timestamps
    timestamps = []
    high_prices = []
    low_prices = []
    close_prices = []
    open_prices = []
    
    for kline in klines:
        timestamps.append(datetime.datetime.fromtimestamp(kline[0] / 1000))
        open_prices.append(float(kline[1]))
        high_prices.append(float(kline[2]))
        low_prices.append(float(kline[3]))
        close_prices.append(float(kline[4]))
    
    return {
        'timestamps': timestamps,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices
    }

def get_terminal_size():
    """Get terminal size, fallback to 80x20 if detection fails."""
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except (OSError, AttributeError):
        return 80, 20

def detect_unicode_support():
    """Detect if terminal supports Unicode characters."""
    try:
        # Check if stdout encoding supports UTF-8
        encoding = sys.stdout.encoding
        if encoding and 'utf' in encoding.lower():
            # Try to encode a Unicode character
            test_char = '│'
            test_char.encode(encoding)
            return True
    except (AttributeError, UnicodeEncodeError):
        pass
    
    # Fallback: try to encode a Unicode character to check support
    try:
        test_char = '│'
        test_char.encode(sys.getdefaultencoding())
        # Also check if we can actually write it
        if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
            test_char.encode(sys.stdout.encoding)
            return True
    except (UnicodeEncodeError, AttributeError):
        pass
    
    return False

def should_use_unicode(config_unicode_setting):
    """Determine if Unicode should be used based on config and detection."""
    if config_unicode_setting == 'true':
        return True
    elif config_unicode_setting == 'false':
        return False
    else:  # 'auto'
        return detect_unicode_support()

def detect_color_support():
    """Detect if terminal supports ANSI color codes."""
    # Check if stdout is a TTY and not redirected
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    
    # Check environment variables
    if os.getenv('NO_COLOR') or os.getenv('TERM') == 'dumb':
        return False
    
    # Check if we're on Windows (may need colorama, but try anyway)
    if sys.platform == 'win32':
        # Windows 10+ supports ANSI colors, but older versions don't
        # We'll assume modern Windows supports it
        return True
    
    # For Unix-like systems, assume color support if TTY
    return True

def should_use_color(config_color_setting):
    """Determine if colors should be used based on config and detection."""
    if config_color_setting == 'true':
        return True
    elif config_color_setting == 'false':
        return False
    else:  # 'auto'
        return detect_color_support()

def calculate_price_range(price_data):
    """Calculate min and max prices from all price data."""
    all_prices = price_data['high'] + price_data['low'] + price_data['close']
    min_price = min(all_prices)
    max_price = max(all_prices)
    
    # Add some padding (5% on each side)
    price_range = max_price - min_price
    padding = price_range * 0.05
    min_price -= padding
    max_price += padding
    
    return min_price, max_price

def price_to_y(price, min_price, max_price, graph_height):
    """Convert price to Y coordinate (row) in the graph."""
    if max_price == min_price:
        return graph_height // 2
    
    # Invert Y so higher prices are at the top
    ratio = (price - min_price) / (max_price - min_price)
    y = int(graph_height - 1 - (ratio * (graph_height - 1)))
    return max(0, min(graph_height - 1, y))

def format_price(price, quote_currency):
    """Format price for display."""
    if price >= 1000:
        return f"{price:,.0f}"
    elif price >= 1:
        return f"{price:,.2f}"
    else:
        return f"{price:.6f}".rstrip('0').rstrip('.')

def calculate_graph_dimensions(config_width, config_height, terminal_width, terminal_height):
    """Calculate graph dimensions, reserving space for axes and labels."""
    # Reserve space for Y-axis labels (10 chars for price + 1 for separator = 11 chars)
    # Reserve additional space for X-axis labels (they need room to display dates)
    # Labels can be up to 8 chars (MM/DD HH:MM format), so we need some margin
    y_axis_width = 11
    x_label_margin = 10  # Space needed for X-axis labels on both sides
    
    if config_width:
        available_width = config_width - y_axis_width
    else:
        # Auto-calculate: leave room for labels
        available_width = terminal_width - y_axis_width - x_label_margin
    
    # Reserve space for X-axis (2 lines) and some margins
    available_height = (config_height or terminal_height) - 4
    
    # Ensure minimum size but don't exceed terminal width
    graph_width = max(20, min(available_width, terminal_width - y_axis_width))
    graph_height = max(5, min(available_height, terminal_height - 4))
    
    return graph_width, graph_height

def calculate_optimal_periods(graph_width, graph_format='candle'):
    """Calculate optimal number of periods based on graph width."""
    # For candle format, we need at least 1 character per candle, but 2-3 is better for readability
    # For dot format, we can fit more (1 char per dot)
    if graph_format == 'candle':
        chars_per_period = 2  # Allow some spacing between candles
    else:  # dot
        chars_per_period = 1.5  # Dots can be closer together
    
    optimal_periods = int(graph_width / chars_per_period)
    
    # Ensure reasonable bounds
    optimal_periods = max(10, min(optimal_periods, 1000))  # Between 10 and 1000 periods
    
    return optimal_periods

def render_candle_graph(price_data, graph_width, graph_height, min_price, max_price, use_unicode, use_color=False):
    """Render candle graph in ASCII or Unicode, with optional colors."""
    num_periods = len(price_data['close'])
    if num_periods == 0:
        return []
    
    # Calculate column width (how many characters per candle)
    chars_per_candle = max(1, graph_width // num_periods)
    
    # Initialize graph canvas (store both character and color)
    canvas = [[(' ', '') for _ in range(graph_width)] for _ in range(graph_height)]
    
    # Symbols for rendering
    if use_unicode:
        v_line = '│'  # Vertical line for wick
        body_fill = '█'  # Filled block for body
    else:
        v_line = '|'  # Vertical line for wick
        body_fill = '#'  # Hash for body (different from wick)
    
    # Render each candle
    for i in range(num_periods):
        high = price_data['high'][i]
        low = price_data['low'][i]
        close = price_data['close'][i]
        open_price = price_data['open'][i]
        
        # Calculate Y positions (remember: lower Y = higher price on screen)
        y_high = price_to_y(high, min_price, max_price, graph_height)
        y_low = price_to_y(low, min_price, max_price, graph_height)
        y_open = price_to_y(open_price, min_price, max_price, graph_height)
        y_close = price_to_y(close, min_price, max_price, graph_height)
        
        # Ensure correct ordering: high should be at top (smaller Y), low at bottom (larger Y)
        if y_high > y_low:
            # Swap if inverted (shouldn't happen, but safety check)
            y_high, y_low = y_low, y_high
        
        # Determine candle body top and bottom
        # Body top is the higher of open/close (lower Y value = higher price)
        # Body bottom is the lower of open/close (higher Y value = lower price)
        y_body_top = min(y_open, y_close)  # Top of body (higher price)
        y_body_bottom = max(y_open, y_close)  # Bottom of body (lower price)
        
        # Calculate X position (center of candle)
        x = (i * graph_width) // num_periods + (chars_per_candle // 2)
        x = min(x, graph_width - 1)
        
        # Determine color for this candle
        if use_color:
            if close > open_price:
                body_color = Colors.BULLISH  # Green for bullish
            else:
                body_color = Colors.BEARISH  # Red for bearish
            wick_color = Colors.WICK  # Gray for wick
        else:
            body_color = ''
            wick_color = ''
        
        # Draw full wick from high to low (this shows the full price range)
        # The wick will be partially overwritten by the body
        for y in range(y_high, y_low + 1):
            if 0 <= y < graph_height:
                canvas[y][x] = (v_line, wick_color)
        
        # Draw candle body (overwrites part of wick)
        if y_body_top == y_body_bottom:
            # Single line body (open == close)
            if 0 <= y_body_top < graph_height:
                canvas[y_body_top][x] = (body_fill, body_color)
        else:
            # Multi-line body
            for y in range(y_body_top, y_body_bottom + 1):
                if 0 <= y < graph_height:
                    canvas[y][x] = (body_fill, body_color)
    
    return canvas

def render_dot_graph(price_data, graph_width, graph_height, min_price, max_price, use_unicode, dot_values, use_color=False):
    """Render dot graph with configurable symbols and optional colors."""
    num_periods = len(price_data['close'])
    if num_periods == 0:
        return []
    
    # Calculate column width
    chars_per_candle = max(1, graph_width // num_periods)
    
    # Initialize graph canvas (store both character and color)
    canvas = [[(' ', '') for _ in range(graph_width)] for _ in range(graph_height)]
    
    # Symbols for rendering
    if use_unicode:
        high_symbol = '▲'
        low_symbol = '▼'
        close_symbol = '●'
    else:
        high_symbol = '^'
        low_symbol = 'v'
        close_symbol = 'o'
    
    # Colors for dots
    if use_color:
        high_color = Colors.HIGH_COLOR
        low_color = Colors.LOW_COLOR
        close_color = Colors.CLOSE_COLOR
    else:
        high_color = ''
        low_color = ''
        close_color = ''
    
    # Render dots
    for i in range(num_periods):
        high = price_data['high'][i]
        low = price_data['low'][i]
        close = price_data['close'][i]
        
        # Calculate Y positions
        y_high = price_to_y(high, min_price, max_price, graph_height)
        y_low = price_to_y(low, min_price, max_price, graph_height)
        y_close = price_to_y(close, min_price, max_price, graph_height)
        
        # Calculate X position
        x = (i * graph_width) // num_periods + (chars_per_candle // 2)
        x = min(x, graph_width - 1)
        
        # Draw symbols based on dot_values setting
        if dot_values == 'all' or dot_values == 'high':
            if 0 <= y_high < graph_height:
                canvas[y_high][x] = (high_symbol, high_color)
        if dot_values == 'all' or dot_values == 'low':
            if 0 <= y_low < graph_height:
                canvas[y_low][x] = (low_symbol, low_color)
        if dot_values == 'all' or dot_values == 'close':
            if 0 <= y_close < graph_height:
                canvas[y_close][x] = (close_symbol, close_color)
    
    return canvas

def render_graph(price_data, config):
    """Main function to render the complete graph with axes, labels, and legend."""
    # Get terminal size
    terminal_width, terminal_height = get_terminal_size()
    
    # Calculate graph dimensions
    graph_width, graph_height = calculate_graph_dimensions(
        config.get('width'), config.get('height'),
        terminal_width, terminal_height
    )
    
    # Determine Unicode usage
    use_unicode = should_use_unicode(config.get('use_unicode', 'auto'))
    
    # Determine color usage
    use_color = should_use_color(config.get('use_color', 'auto'))
    
    # Frame symbols based on Unicode support
    if use_unicode:
        y_separator = '│'
        x_corner = '└'
        x_line = '─'
    else:
        y_separator = '|'
        x_corner = '+'
        x_line = '-'
    
    # Calculate price range
    min_price, max_price = calculate_price_range(price_data)
    
    # Render the graph based on format
    if config['graph_format'] == 'candle':
        canvas = render_candle_graph(price_data, graph_width, graph_height, min_price, max_price, use_unicode, use_color)
    else:  # dot
        canvas = render_dot_graph(price_data, graph_width, graph_height, min_price, max_price, use_unicode, config['dot_values'], use_color)
    
    # Build output lines
    output_lines = []
    
    # Get terminal width for truncation
    terminal_width, _ = get_terminal_size()
    
    # Legend - truncate if too long
    base_currency = config['base_currency']
    quote_currency = config['quote_currency']
    interval = config['time_interval']
    periods = config['periods']
    start_date = price_data['timestamps'][0].strftime('%Y-%m-%d %H:%M')
    end_date = price_data['timestamps'][-1].strftime('%Y-%m-%d %H:%M')
    
    legend = f"{base_currency}/{quote_currency} - {interval} - {periods} periods ({start_date} to {end_date})"
    # Truncate legend if it exceeds terminal width
    if len(legend) > terminal_width:
        legend = legend[:terminal_width-3] + "..."
    output_lines.append(legend)
    output_lines.append("=" * min(len(legend), terminal_width))
    output_lines.append("")
    
    # Y-axis labels and graph
    price_step = (max_price - min_price) / (graph_height - 1)
    
    for y in range(graph_height):
        # Calculate price for this row
        price = max_price - (price_step * y)
        price_label = format_price(price, quote_currency)
        
        # Pad price label to consistent width
        price_label = price_label.rjust(10)
        
        # Graph line - build with colors if enabled
        graph_line_parts = []
        for char, color in canvas[y]:
            if use_color and color:
                graph_line_parts.append(f"{color}{char}{Colors.RESET}")
            else:
                graph_line_parts.append(char)
        graph_line = ''.join(graph_line_parts)
        
        # Calculate total line width (without color codes for width calculation)
        graph_line_no_color = ''.join(char for char, _ in canvas[y])
        total_width = 10 + 1 + len(graph_line_no_color)
        if total_width > terminal_width:
            # Truncate graph line to fit
            max_graph_width = terminal_width - 11
            graph_line = ''.join(graph_line_parts[:max_graph_width])
        
        # Combine - no space between price label and separator for alignment
        output_lines.append(f"{price_label}{y_separator}{graph_line}")
    
    # X-axis - ensure it fits within terminal width and aligns with Y-axis separator
    x_axis_width = min(graph_width, terminal_width - 11)
    output_lines.append(" " * 10 + x_corner + x_line * x_axis_width)
    
    # X-axis labels (show first, middle, last if there's space)
    # Labels need to be positioned relative to the graph area (starting at position 11)
    if graph_width > 20:
        num_periods = len(price_data['timestamps'])
        label_indices = [0, num_periods // 2, num_periods - 1] if num_periods > 2 else [0, num_periods - 1]
        
        # Start label line after Y-axis (11 chars: 10 for price label + 1 for separator)
        label_line = " " * 11
        # Maximum position for labels (graph starts at 11, so graph ends at 11 + graph_width)
        max_label_pos = 11 + graph_width
        
        for idx in label_indices:
            if idx < num_periods:
                timestamp = price_data['timestamps'][idx]
                if interval.endswith('d') or interval.endswith('w') or interval.endswith('M'):
                    label = timestamp.strftime('%m/%d')
                elif interval.endswith('h'):
                    label = timestamp.strftime('%m/%d %H:%M')
                else:
                    label = timestamp.strftime('%H:%M')
                
                # Calculate X position within the graph area (0 to graph_width-1)
                # Then offset by 11 to account for Y-axis
                graph_x_pos = (idx * graph_width) // num_periods
                x_pos = 11 + graph_x_pos
                
                # Center the label on its position (adjust left if label is longer)
                label_start = max(11, x_pos - len(label) // 2)
                label_end = label_start + len(label)
                
                # Ensure label fits within graph area and terminal width
                if label_start >= 11 and label_end <= min(max_label_pos, terminal_width):
                    # Extend label_line if needed
                    if label_end > len(label_line):
                        label_line = label_line.ljust(label_end, ' ')
                    # Place the label
                    label_line = label_line[:label_start] + label + label_line[label_end:]
        
        # Truncate label line to terminal width
        if len(label_line) > terminal_width:
            label_line = label_line[:terminal_width]
        output_lines.append(label_line)
    
    # Format info - truncate if too long
    format_info = f"Format: {config['graph_format']}"
    if config['graph_format'] == 'dot':
        format_info += f" (showing: {config['dot_values']})"
    format_info += f" | Unicode: {use_unicode} | Color: {use_color}"
    # Truncate format info if it exceeds terminal width
    if len(format_info) > terminal_width:
        format_info = format_info[:terminal_width-3] + "..."
    output_lines.append("")
    output_lines.append(format_info)
    
    return '\n'.join(output_lines)

def main():
    """Main function."""
    try:
        config = get_config()
        
        # Get terminal size for calculating optimal periods if needed
        terminal_width, terminal_height = get_terminal_size()
        
        # Detect Unicode support
        use_unicode = should_use_unicode(config.get('use_unicode', 'auto'))
        
        # Calculate graph dimensions to determine optimal periods
        graph_width, graph_height = calculate_graph_dimensions(
            config.get('width'), config.get('height'),
            terminal_width, terminal_height
        )
        
        # Calculate optimal periods if not specified
        if config.get('periods') is None:
            periods = calculate_optimal_periods(graph_width, config['graph_format'])
            config['periods'] = periods
        
        # Initialize Binance client (no API keys needed for public data)
        client = Client()
        
        # Fetch historical price data
        print(f"Fetching {config['periods']} periods of {config['base_currency']}/{config['quote_currency']} data ({config['time_interval']})...")
        price_data = get_historical_prices(
            client,
            config['ticker_name'],
            config['time_interval'],
            config['periods']
        )
        
        # Render and print graph
        graph_output = render_graph(price_data, config)
        print(graph_output)
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
