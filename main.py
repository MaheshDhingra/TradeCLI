import math
import os
import requests
import json
import random
import datetime
from typing import Dict, List, Set

TRADING_MODE = "dummy"
TRADING_CONFIG: Dict[str, str] = {}

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

market_data: Dict[str, Dict] = {}
favourites: Set[str] = set()
watchlist: Set[str] = set()

ALPHA_VANTAGE_KEY = "PKCP234ZXWY3IG2O"
portfolio_history: List[float] = []
command_history: List[str] = []
ticker_notes: Dict[str, List[str]] = {}

user_profiles: Dict[str, Dict] = {}
current_profile: str = 'default'
macros: Dict[str, str] = {}
last_action: Dict = {}


def configure_real_trading():
    print("Enter credentials for real trading platform:")
    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    TRADING_CONFIG['api_key'] = api_key
    TRADING_CONFIG['api_secret'] = api_secret
    print("Real trading configuration saved.")


def fetch_alpha_vantage_price(ticker: str) -> float:
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        price = data.get("Global Quote", {}).get("05. price")
        if price:
            return round(float(price), 2)
        else:
            print(f"Alpha Vantage: No price for {ticker}.")
            return 0.0
    except Exception as e:
        print(f"Alpha Vantage error: {e}")
        return 0.0


def get_market_price(ticker: str) -> float:
    ticker = ticker.upper()
    price = fetch_alpha_vantage_price(ticker)
    if ticker not in market_data:
        market_data[ticker] = {'history': [], 'price': price}
    data = market_data[ticker]
    data['price'] = price
    data['history'].append(price)
    if len(data['history']) > 100:
        data['history'] = data['history'][-100:]
    return price


def place_real_order(order_type: str, ticker: str, qty: int, price: float):
    print(f"Placed real {order_type} order: {qty} shares of {ticker} at ${price}/share.")


def show_chart(ticker: str, interval: str = '5min'):
    ticker = ticker.upper()
    interval = interval.lower()
    if interval in ['d', '1d', 'day']:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}"
        time_key = "Time Series (Daily)"
        label = 'Daily'
    elif interval in ['1h', 'hour', '60min']:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=60min&apikey={ALPHA_VANTAGE_KEY}"
        time_key = "Time Series (60min)"
        label = 'Hourly'
    elif interval in ['4h', '4hour', '240min']:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=240min&apikey={ALPHA_VANTAGE_KEY}"
        time_key = "Time Series (240min)"
        label = '4 Hour'
    elif interval in ['1min', 'minute']:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=1min&apikey={ALPHA_VANTAGE_KEY}"
        time_key = "Time Series (1min)"
        label = '1 Minute'
    else:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=5min&apikey={ALPHA_VANTAGE_KEY}"
        time_key = "Time Series (5min)"
        label = '5min'
    try:
        r = requests.get(url, timeout=10)
        data = r.json().get(time_key, {})
        if not data:
            print(f"No chart data for {ticker}.")
            return
        times = list(data.keys())[::-1]
        prices = [float(data[t]["4. close"]) for t in times]
        min_p = min(prices)
        max_p = max(prices)
        width = min(50, len(prices))
        height = 10
        scale = (max_p - min_p) / (height - 1) if max_p != min_p else 1
        chart = [[' ' for _ in range(width)] for _ in range(height)]
        for i in range(width):
            idx = -width + i if len(prices) >= width else i
            p = prices[idx]
            y = int(round((p - min_p) / scale)) if scale else 0
            y = min(y, height - 1)
            chart[height - 1 - y][i] = '*'
        print(f"\nPrice History for {ticker} ({label} ASCII Chart):")
        y_labels = [min_p + scale * (height - 1 - i) for i in range(height)]
        for i, row in enumerate(chart):
            label = f"{y_labels[i]:7.2f} | "
            print(label + ''.join(row))
        print("        +" + "-" * width)
        print("         " + ''.join([str((i//10)%10) if i%10==0 else ' ' for i in range(width)]))
        print(f"Min: {min_p:.2f}  Max: {max_p:.2f}")
    except Exception as e:
        print(f"Chart error: {e}")


def show_popular_pairs(positions=None):
    popular_pairs = [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "BTCUSD", "ETHUSD", "TSLA", "AAPL", "GOOGL", "MSFT", "NVDA", "META", "AMZN", "NFLX", "BABA", "INTC", "AMD", "UBER", "DIS", "V", "JPM", "BAC", "WMT", "T", "KO", "PEP", "MCD", "PYPL", "SBUX", "SHOP", "SQ"
    ]
    print(f"Popular Pairs and Tickers:{RESET}")
    for pair in popular_pairs:
        price = get_market_price(pair)
        holding = None
        if positions and pair in positions:
            holding = positions[pair]['qty']
        holding_str = f" | Holding: {holding}" if holding else ""
        print(f"  {pair}: ${price}{holding_str}")
    print()


def remove_favourite():
    q = input("Enter ticker to remove from favourites: ").strip().upper()
    if q in favourites:
        favourites.remove(q)
        print(f"Removed {q} from favourites.")
    else:
        print(f"{q} is not in favourites.")


def show_gainers_losers():
    print("Top Gainers/Losers (session):")
    changes = []
    for ticker, data in market_data.items():
        if isinstance(data, dict) and 'history' in data and isinstance(data['history'], list) and len(data['history']) >= 2:
            change = data['history'][-1] - data['history'][0]
            changes.append((change, ticker))
    if not changes:
        print("Not enough data.")
        return
    changes.sort(reverse=True)
    print("Gainers:")
    for ch, t in changes[:5]:
        print(f"  {t}: {ch:+.2f}")
    print("Losers:")
    for ch, t in changes[-5:]:
        print(f"  {t}: {ch:+.2f}")


def show_last_trade_time():
    print("Last trade time for tickers:")
    for ticker, data in market_data.items():
        if isinstance(data, dict) and 'history' in data and data['history']:
            print(f"  {ticker}: {len(data['history'])} updates ago")


def print_banner():
    banner = "=" * 50 + "\n" + "            TradeCLI\n" + "=" * 50 + f"{RESET}"
    print(banner)


def print_help():
    print(f"Available Commands:{RESET}")
    print("  help                   - Show this help message")
    print("  quote <ticker>         - Get the current market quote for the ticker")
    print("  buy <ticker> <qty>     - Buy specified number of shares")
    print("  sell <ticker> <qty>    - Sell specified number of shares")
    print("  positions              - Show current holdings and profit/loss")
    print("  chart <ticker> <day|hour|4hour|minute|5min> - Display price history chart (ASCII)")
    print("  dashboard              - Show customizable dashboard summary")
    print("  analytics              - Show advanced analytics")
    print("  alert                  - Set price/volume alerts")
    print("  integrations           - Integrations menu")
    print("  exportcsv              - Export portfolio to CSV")
    print("  customize              - Customize dashboard")
    print("  popular                - Show popular trading pairs/tickers with price and holding")
    print("  gainers                - Show top gainers and losers")
    print("  lasttrade              - Show last trade time for tickers")
    print("  favourite <ticker>     - Add a ticker to favourites")
    print("  removefav              - Remove a ticker from favourites")
    print("  favourites             - List favourite tickers")
    print("  screener               - Run the price screener")
    print("  setmode <dummy|real>   - Set trading mode")
    print("  config                 - Configure credentials for real trading mode")
    print("  ai <prompt>              - Ask Hack Club AI any question")
    print("  clear / cls            - Clear the terminal screen")
    print("  exit                   - Exit the terminal")


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def add_favourite(ticker: str):
    ticker = ticker.upper()
    favourites.add(ticker)
    print(f"Added {ticker} to favourites.")

def show_favourites():
    if not favourites:
        print("No favourites yet.")
    else:
        print(f"Favourite Tickers:{RESET}")
        for fav in favourites:
            print("  " + fav)
    print()

def show_screener():
    print(f"Screener Results:{RESET}")
    detected = False
    for ticker, data in market_data.items():
        if isinstance(data, dict) and 'history' in data and isinstance(data['history'], list) and len(data['history']) >= 2 and data['history'][-1] > data['history'][-2]:
            print(f"  {ticker} is trending up. Current price: ${data['price']}")
            detected = True
    if not detected:
        print("  No trending tickers detected.")
    print()


def show_analytics():
    if not market_data:
        print("No analytics available yet.")
        return
    changes = []
    for ticker, data in market_data.items():
        if isinstance(data, dict) and 'history' in data and isinstance(data['history'], list) and len(data['history']) >= 2:
            change = data['history'][-1] - data['history'][0]
            changes.append((change, ticker))
    if not changes:
        print("Not enough data for analytics.")
        return
    changes.sort(reverse=True)
    best = changes[0]
    worst = changes[-1]
    avg_return = sum([c[0] for c in changes]) / len(changes)
    win_count = sum(1 for c in changes if c[0] > 0)
    print(f"Best performer: {best[1]} ({best[0]:+.2f})")
    print(f"Worst performer: {worst[1]} ({worst[0]:+.2f})")
    print(f"Average return: {avg_return:+.2f}")
    print(f"Win rate: {win_count}/{len(changes)} ({win_count/len(changes)*100:.1f}%)")

def set_alert():
    ticker = input("Set alert for ticker: ").strip().upper()
    try:
        target = float(input("Alert when price crosses: ").strip())
    except ValueError:
        print("Invalid price.")
        return
    print(f"Alert set for {ticker} at ${target} (session only)")
    if 'alerts' not in market_data:
        market_data['alerts'] = []
    market_data['alerts'].append((ticker, target))

def set_percentage_alert():
    ticker = input("Set percentage alert for ticker: ").strip().upper()
    try:
        percent = float(input("Alert when price moves by percent (e.g. 5 for ±5%): ").strip())
    except ValueError:
        print("Invalid percent.")
        return
    price = get_market_price(ticker)
    if price == 0.0:
        print("Failed to fetch a valid market price. Please try again later.")
        return
    if 'alerts_pct' not in market_data:
        market_data['alerts_pct'] = []
    market_data['alerts_pct'].append((ticker, price, percent))
    print(f"Percentage alert set for {ticker}: ±{percent}% from ${price}")


def check_alerts():
    if 'alerts' not in market_data:
        return
    fired = []
    for (ticker, target) in market_data['alerts']:
        price = get_market_price(ticker)
        if price >= target:
            print(f"ALERT: {ticker} has reached ${price} (target: ${target})!")
            fired.append((ticker, target))
    for alert in fired:
        market_data['alerts'].remove(alert)

def check_percentage_alerts():
    if 'alerts_pct' not in market_data:
        return
    fired = []
    for (ticker, base_price, percent) in market_data['alerts_pct']:
        price = get_market_price(ticker)
        if price == 0.0:
            continue
        change = ((price - base_price) / base_price) * 100
        if abs(change) >= percent:
            print(f"ALERT: {ticker} has moved {change:+.2f}% (target: ±{percent}%) from ${base_price} to ${price}!")
            fired.append((ticker, base_price, percent))
    for alert in fired:
        market_data['alerts_pct'].remove(alert)

def integrations_menu():
    print("Integrations:")
    print("  - Export portfolio to CSV (type 'exportcsv')")
    print("  - [Future] Discord, Telegram, broker APIs")

def export_portfolio_csv(positions):
    import csv
    fname = "portfolio_export.csv"
    with open(fname, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Ticker", "Shares", "Avg Cost", "Current Price", "Market Value"])
        for ticker, pos in positions.items():
            current_price = get_market_price(ticker)
            avg_cost = pos['cost'] / pos['qty']
            value = round(current_price * pos['qty'], 2)
            writer.writerow([ticker, pos['qty'], f"{avg_cost:.2f}", f"{current_price:.2f}", f"{value:.2f}"])
    print(f"Portfolio exported to {fname}")

def customize_dashboard():
    print("Dashboard customization:")
    print("You can select which tickers to show in your dashboard.")
    print("Type a comma-separated list of tickers (e.g. TSLA,AAPL,GOOGL) or 'all' for all holdings.")
    tickers = input("Tickers for dashboard: ")

    if tickers.strip().upper() == 'ALL':
        market_data['dashboard_custom'] = None
        print("Dashboard will show all holdings.")
    else:
        selected = [t.strip().upper() for t in tickers.split(',') if t.strip()]
        market_data['dashboard_custom'] = selected
        print(f"Dashboard will show: {', '.join(selected)}")

def dashboard_summary(positions, filter_type=None):
    print("Customizable Dashboard (basic summary):")
    total_invested = 0.0
    total_value = 0.0
    filtered = positions.items()
    custom = market_data.get('dashboard_custom', None)
    if custom is not None:
        filtered = [(t, p) for t, p in positions.items() if t in custom]
    if filter_type == 'gainers':
        filtered = [(t, p) for t, p in filtered if get_market_price(t) > (p['cost']/p['qty'])]
    elif filter_type == 'losers':
        filtered = [(t, p) for t, p in filtered if get_market_price(t) < (p['cost']/p['qty'])]
    if not filtered:
        print("No positions to display in dashboard.")
        return
    for ticker, pos in filtered:
        current_price = get_market_price(ticker)
        value = round(current_price * pos['qty'], 2)
        total_invested += pos['cost']
        total_value += value
        print(f"  {ticker}: {pos['qty']} shares | Value: ${value} | Current: ${current_price}")
    print(f"Total Invested: ${total_invested}")
    print(f"Portfolio Value: ${total_value}")
    if filter_type:
        print(f"(Filtered: {filter_type})")
    if custom is not None:
        print(f"(Custom dashboard: {', '.join(custom)})")

def ask_hackclub_ai(prompt: str):
    url = "https://ai.hackclub.com/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)
        if resp.status_code == 200:
            result = resp.json()
            if "choices" in result and result["choices"]:
                print("AI:", result["choices"][0]["message"]["content"])
            else:
                print("AI: No response received.")
        else:
            print(f"AI error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"AI request failed: {e}")

def update_portfolio_history(positions: Dict[str, Dict]):
    total_value = 0.0
    for ticker, pos in positions.items():
        current_price = get_market_price(ticker)
        total_value += current_price * pos['qty']
    portfolio_history.append(round(total_value, 2))


def show_portfolio_history():
    if not portfolio_history:
        print("No portfolio history yet.")
        return
    width = min(50, len(portfolio_history))
    height = 10
    values = portfolio_history[-width:]
    min_v = min(values)
    max_v = max(values)
    scale = (max_v - min_v) / (height - 1) if max_v != min_v else 1
    chart = [[' ' for _ in range(width)] for _ in range(height)]
    for i in range(width):
        v = values[i]
        y = int(round((v - min_v) / scale)) if scale else 0
        y = min(y, height - 1)
        chart[height - 1 - y][i] = '*'
    print("\nPortfolio Value History (ASCII Chart):")
    y_labels = [min_v + scale * (height - 1 - i) for i in range(height)]
    for i, row in enumerate(chart):
        label = f"{y_labels[i]:7.2f} | "
        print(label + ''.join(row))
    print("        +" + "-" * width)
    print("         " + ''.join([str((i//10)%10) if i%10==0 else ' ' for i in range(width)]))
    print(f"Min: {min_v:.2f}  Max: {max_v:.2f}")


def save_data(positions, favourites):
    with open('portfolio_save.json', 'w') as f:
        json.dump({'positions': positions, 'favourites': list(favourites)}, f)
    print("Portfolio and favourites saved.")

def load_data():
    try:
        with open('portfolio_save.json', 'r') as f:
            data = json.load(f)
        print("Portfolio and favourites loaded.")
        return data.get('positions', {}), set(data.get('favourites', []))
    except Exception as e:
        print(f"Load failed: {e}")
        return {}, set()

def add_note(ticker: str, note: str):
    ticker = ticker.upper()
    if ticker not in ticker_notes:
        ticker_notes[ticker] = []
    ticker_notes[ticker].append(note)
    print(f"Note added for {ticker}.")

def show_notes(ticker: str):
    ticker = ticker.upper()
    notes = ticker_notes.get(ticker, [])
    if not notes:
        print(f"No notes for {ticker}.")
    else:
        print(f"Notes for {ticker}:")
        for n in notes:
            print(f"- {n}")

def diversification_analysis(positions):
    if not positions:
        print("No positions to analyze.")
        return
    total = sum(get_market_price(t) * p['qty'] for t, p in positions.items())
    print("Portfolio Diversification:")
    for t, p in positions.items():
        value = get_market_price(t) * p['qty']
        percent = (value / total) * 100 if total else 0
        print(f"  {t}: {percent:.2f}% of portfolio")

def suggest_ticker():
    tickers = list(market_data.keys()) or ["AAPL", "TSLA", "GOOGL", "MSFT", "BTCUSD", "ETHUSD"]
    print(f"Suggested ticker: {random.choice(tickers)}")

def show_news():
    print("Market News Headlines:")
    try:
        r = requests.get("https://newsapi.org/v2/top-headlines?category=business&apiKey=demo", timeout=10)
        data = r.json()
        for a in data.get('articles', [])[:5]:
            print(f"- {a.get('title')}")
    except Exception as e:
        print(f"News fetch error: {e}")

def show_command_history():
    print("Session Command History:")
    for cmd in command_history:
        print(cmd)

def clear_all_alerts():
    market_data['alerts'] = []
    market_data['alerts_pct'] = []
    print("All alerts cleared.")

def show_candlestick_chart(ticker: str):
    print(f"ASCII Candlestick Chart for {ticker} (feature coming soon)")


def add_to_watchlist(ticker: str):
    ticker = ticker.upper()
    watchlist.add(ticker)
    print(f"Added {ticker} to watchlist.")

def remove_from_watchlist(ticker: str):
    ticker = ticker.upper()
    if ticker in watchlist:
        watchlist.remove(ticker)
        print(f"Removed {ticker} from watchlist.")
    else:
        print(f"{ticker} not in watchlist.")

def show_watchlist():
    if not watchlist:
        print("Watchlist is empty.")
    else:
        print("Watchlist:")
        for t in watchlist:
            print(f"- {t}")


def convert_portfolio(currency: str, positions):
    print(f"Portfolio value in {currency.upper()} (feature coming soon)")

def suggest_rebalance(positions):
    print("Rebalancing suggestion (feature coming soon)")

def simulate_dividends(positions):
    print("Simulated dividend payouts (feature coming soon)")

def autocomplete_ticker(partial: str):
    matches = [t for t in market_data if t.startswith(partial.upper())]
    print(f"Autocomplete suggestions: {', '.join(matches) if matches else 'None'}")

def show_market_status():
    print("Market status (feature coming soon)")

def show_session_pl():
    print("Session P&L summary (feature coming soon)")

def export_notes():
    try:
        with open('notes_export.json', 'w') as f:
            json.dump(ticker_notes, f)
        print("Notes exported.")
    except Exception as e:
        print(f"Export failed: {e}")

def import_notes():
    try:
        with open('notes_export.json', 'r') as f:
            notes = json.load(f)
        ticker_notes.update(notes)
        print("Notes imported.")
    except Exception as e:
        print(f"Import failed: {e}")

def set_default_dashboard(tickers):
    market_data['dashboard_custom'] = [t.upper() for t in tickers]
    print(f"Default dashboard set to: {', '.join(market_data['dashboard_custom'])}")

def show_volatile():
    print("Most volatile tickers (feature coming soon)")

def show_top_volume():
    tickers_with_volume = []
    for ticker in market_data:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}"
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            volume = int(data.get("Global Quote", {}).get("06. volume", 0))
            tickers_with_volume.append((volume, ticker))
        except Exception:
            continue
    if not tickers_with_volume:
        print("No volume data available.")
        return
    tickers_with_volume.sort(reverse=True)
    print("Top Volume Tickers:")
    for volume, ticker in tickers_with_volume[:5]:
        print(f"  {ticker}: {volume:,} shares")

def show_sector_breakdown():
    print("Sector breakdown (feature coming soon)")

def show_rsi(ticker: str):
    print(f"RSI for {ticker} (feature coming soon)")

def show_moving_average(ticker: str, window: int):
    print(f"Moving average for {ticker} (window {window}) (feature coming soon)")


def schedule_alert(ticker: str, price: float, interval: str):
    print(f"Scheduled alert for {ticker} at ${price} every {interval} (feature coming soon)")

def analyze_risk(positions):
    print("Portfolio risk analysis (feature coming soon)")

def create_macro(name: str, commands: str):
    macros[name] = commands
    print(f"Macro '{name}' saved.")

def run_macro(name: str, positions):
    if name in macros:
        print(f"Running macro '{name}': {macros[name]}")
        for cmd in macros[name].split(';'):
            process_command(*cmd.strip().split(), positions)
    else:
        print(f"Macro '{name}' not found.")

def switch_profile(name: str):
    global current_profile
    current_profile = name
    print(f"Switched to profile: {name}")

def manage_apikeys():
    print("API key management (feature coming soon)")

def export_all():
    print("Exporting all data (feature coming soon)")

def import_all():
    print("Importing all data (feature coming soon)")

def tab_complete():
    print("Tab completion suggestions (feature coming soon)")

def change_theme(name: str):
    print(f"Theme changed to {name} (feature coming soon)")

def session_report():
    print("Session summary report (feature coming soon)")

def undo_last_action():
    print("Undo last action (feature coming soon)")

def toggle_interactive():
    print("Interactive mode toggled (feature coming soon)")

def quick_start():
    print("Quick start guide (feature coming soon)")

def submit_feedback(message: str):
    print(f"Feedback submitted: {message}")

def show_overlay(overlay_type: str, ticker: str):
    print(f"Overlay {overlay_type} for {ticker} (feature coming soon)")


def process_command(command: str, args: List[str], positions: Dict[str, Dict]) -> bool:
    global TRADING_MODE, favourites, watchlist, current_profile
    command_history.append(' '.join([command] + args))
    command = command.lower()

    # Aliases
    if command == 'q':
        command = 'quote'
    elif command == 'b':
        command = 'buy'

    if command == 'help':
        print_help()
    elif command == "setmode":
        if len(args) != 1 or args[0].lower() not in ["dummy", "real"]:
            print("Usage: setmode <dummy|real>")
        else:
            TRADING_MODE = args[0].lower()
            print(f"Trading mode set to: {TRADING_MODE}")
            if TRADING_MODE == "real":
                print("Don't forget to run 'config' to configure your trading credentials.")
    elif command == "config":
        if TRADING_MODE != "real":
            print("Configuration is only required for real trading mode.")
        else:
            configure_real_trading()
    elif command == 'quote':
        if len(args) != 1:
            print("Usage: quote <ticker>")
        else:
            ticker = args[0].upper()
            price = get_market_price(ticker)
            print(f"Quote for {ticker}: ${price}")
    elif command == 'buy':
        if len(args) != 2:
            print("Usage: buy <ticker> <qty>")
        else:
            ticker = args[0].upper()
            try:
                qty = int(args[1])
                if qty <= 0:
                    raise ValueError
            except ValueError:
                print("Quantity must be a positive integer.")
                return True
            price = get_market_price(ticker)
            if price == 0.0:
                print("Failed to fetch a valid market price. Please try again later.")
                return True
            total_cost = round(price * qty, 2)
            if TRADING_MODE == "real":
                if not TRADING_CONFIG:
                    print("Please configure your trading platform by running 'config'.")
                    return True
                place_real_order("buy", ticker, qty, price)
                positions.setdefault(ticker, {"qty": 0, "cost": 0.0})
                positions[ticker]['qty'] += qty
                positions[ticker]['cost'] += total_cost
            else:
                if ticker in positions:
                    positions[ticker]['qty'] += qty
                    positions[ticker]['cost'] += total_cost
                else:
                    positions[ticker] = {"qty": qty, "cost": total_cost}
                print(f"Bought {qty} shares of {ticker} at ${price}/share for ${total_cost}.")
            update_portfolio_history(positions)
    elif command == 'sell':
        if len(args) != 2:
            print("Usage: sell <ticker> <qty>")
        else:
            ticker = args[0].upper()
            try:
                qty = int(args[1])
                if qty <= 0:
                    raise ValueError
            except ValueError:
                print("Quantity must be a positive integer.")
                return True
            if ticker not in positions or positions[ticker]['qty'] < qty:
                print("Insufficient shares to sell.")
            else:
                price = get_market_price(ticker)
                total_value = round(price * qty, 2)
                avg_cost = positions[ticker]['cost'] / positions[ticker]['qty']
                if TRADING_MODE == "real":
                    if not TRADING_CONFIG:
                        print("Please configure your trading platform by running 'config'.")
                        return True
                    place_real_order("sell", ticker, qty, price)
                    positions[ticker]['qty'] -= qty
                    positions[ticker]['cost'] -= avg_cost * qty
                    if positions[ticker]['qty'] == 0:
                        del positions[ticker]
                else:
                    positions[ticker]['qty'] -= qty
                    positions[ticker]['cost'] -= avg_cost * qty
                    if positions[ticker]['qty'] == 0:
                        del positions[ticker]
                    print(f"Sold {qty} shares of {ticker} at ${price}/share for ${total_value}.")
            update_portfolio_history(positions)
    elif command == 'positions':
        if not positions:
            print("No positions held.")
        else:
            print("Current Positions:")
            total_unrealized = 0.0
            for ticker, pos in positions.items():
                current_price = get_market_price(ticker)
                avg_cost = pos['cost'] / pos['qty']
                unrealized = round((current_price - avg_cost) * pos['qty'], 2)
                total_unrealized += unrealized
                print(f"  {ticker}: {pos['qty']} shares (avg cost: ${avg_cost:.2f}, current: ${current_price}) -> P/L: ${unrealized}")
            print(f"Total Unrealized P/L: ${total_unrealized}")
    elif command == 'dashboard':
        if len(args) == 1 and args[0] in ['gainers', 'losers', 'all']:
            dashboard_summary(positions, filter_type=args[0] if args[0] != 'all' else None)
        else:
            dashboard_summary(positions)
    elif command == 'analytics':
        show_analytics()
    elif command == 'alert':
        set_alert()
    elif command == 'alertpct':
        set_percentage_alert()
    elif command == 'integrations':
        integrations_menu()
    elif command == 'exportcsv':
        export_portfolio_csv(positions)
    elif command == 'customize':
        customize_dashboard()
    elif command == 'chart':
        if len(args) == 0:
            print("Usage: chart <ticker> [interval]")
        else:
            ticker = args[0].upper()
            interval = args[1] if len(args) > 1 else '5min'
            show_chart(ticker, interval)
    elif command == 'popular':
        show_popular_pairs(positions)
    elif command == 'favourite':
        if len(args) != 1:
            print("Usage: favourite <ticker>")
        else:
            add_favourite(args[0])
    elif command == 'removefav':
        remove_favourite()
    elif command == 'favourites':
        show_favourites()
    elif command == 'screener':
        show_screener()
    elif command == 'gainers':
        show_gainers_losers()
    elif command == 'lasttrade':
        show_last_trade_time()
    elif command == 'history':
        show_portfolio_history()
    elif command == 'performance':
        # Simple performance summary
        print("Performance summary (feature coming soon)")
    elif command == 'save':
        save_data(positions, favourites)
    elif command == 'load':
        loaded_positions, loaded_favourites = load_data()
        positions.clear()
        positions.update(loaded_positions)
        favourites = loaded_favourites
    elif command == 'notes':
        if not args:
            print("Usage: notes <ticker> [note]")
        elif len(args) == 1:
            show_notes(args[0])
        else:
            add_note(args[0], ' '.join(args[1:]))
    elif command == 'diversify':
        diversification_analysis(positions)
    elif command == 'suggest':
        suggest_ticker()
    elif command == 'news':
        show_news()
    elif command == 'historycmds':
        show_command_history()
    elif command == 'clearalerts':
        clear_all_alerts()
    elif command == 'candlestick':
        if not args:
            print("Usage: candlestick <ticker>")
        else:
            show_candlestick_chart(args[0])
    elif command == 'addwatch':
        if not args:
            print("Usage: addwatch <ticker>")
        else:
            add_to_watchlist(args[0])
    elif command == 'removewatch':
        if not args:
            print("Usage: removewatch <ticker>")
        else:
            remove_from_watchlist(args[0])
    elif command == 'watchlist':
        show_watchlist()
    elif command == 'convert':
        if not args:
            print("Usage: convert <currency>")
        else:
            convert_portfolio(args[0], positions)
    elif command == 'rebalance':
        suggest_rebalance(positions)
    elif command == 'dividends':
        simulate_dividends(positions)
    elif command == 'autocomplete':
        if not args:
            print("Usage: autocomplete <partial>")
        else:
            autocomplete_ticker(args[0])
    elif command == 'marketstatus':
        show_market_status()
    elif command == 'sessionpl':
        show_session_pl()
    elif command == 'exportnotes':
        export_notes()
    elif command == 'importnotes':
        import_notes()
    elif command == 'setdashboard':
        if not args:
            print("Usage: setdashboard <tickers>")
        else:
            set_default_dashboard(args)
    elif command == 'volatile':
        show_volatile()
    elif command == 'topvolume':
        show_top_volume()
    elif command == 'sectorbreakdown':
        show_sector_breakdown()
    elif command == 'rsi':
        if not args:
            print("Usage: rsi <ticker>")
        else:
            show_rsi(args[0])
    elif command == 'ma':
        if len(args) != 2:
            print("Usage: ma <ticker> <window>")
        else:
            try:
                window = int(args[1])
                show_moving_average(args[0], window)
            except ValueError:
                print("Window must be an integer.")
    elif command == 'schedulealert':
        if len(args) != 3:
            print("Usage: schedulealert <ticker> <price> <interval>")
        else:
            try:
                price = float(args[1])
                schedule_alert(args[0], price, args[2])
            except ValueError:
                print("Price must be a number.")
    elif command == 'risk':
        analyze_risk(positions)
    elif command == 'macro':
        if len(args) < 2:
            print("Usage: macro <name> <commands>")
        else:
            create_macro(args[0], ' '.join(args[1:]))
    elif command == 'runmacro':
        if not args:
            print("Usage: runmacro <name>")
        else:
            run_macro(args[0], positions)
    elif command == 'profile':
        if not args:
            print("Usage: profile <name>")
        else:
            switch_profile(args[0])
    elif command == 'switchprofile':
        if not args:
            print("Usage: switchprofile <name>")
        else:
            switch_profile(args[0])
    elif command == 'apikeys':
        manage_apikeys()
    elif command == 'exportall':
        export_all()
    elif command == 'importall':
        import_all()
    elif command == 'tabcomplete':
        tab_complete()
    elif command == 'theme':
        if not args:
            print("Usage: theme <name>")
        else:
            change_theme(args[0])
    elif command == 'sessionreport':
        session_report()
    elif command == 'undo':
        undo_last_action()
    elif command == 'interactive':
        toggle_interactive()
    elif command == 'quickstart':
        quick_start()
    elif command == 'feedback':
        if not args:
            print("Usage: feedback <message>")
        else:
            submit_feedback(' '.join(args))
    elif command == 'overlay':
        if len(args) < 2:
            print("Usage: overlay <type> <ticker>")
        else:
            show_overlay(args[0], args[1])
    else:
        print("Unknown command. Type 'help' for available commands.")
    check_alerts()
    check_percentage_alerts()
    return True


def main():
    global TRADING_MODE
    clear_screen()
    print_banner()
    print(f"Welcome to TradeCLI!{RESET}")
    mode_choice = input("Choose trading mode (dummy/real) [default: dummy]: ").strip().lower()
    if mode_choice in ["real", "dummy"]:
        TRADING_MODE = mode_choice
    else:
        TRADING_MODE = "dummy"
    print(f"Trading mode set to: {TRADING_MODE}")
    if TRADING_MODE == "real":
        answer = input("Would you like to configure real trading credentials now? (y/n): ").strip().lower()
        if answer == "y":
            configure_real_trading()
    print("Type 'help' to see available commands.")
    positions: Dict[str, Dict] = {}
    update_portfolio_history(positions)  # Initialize history at start
    while True:
        try:
            user_input = input(f"TradeCLI> {RESET}").strip()
            if not user_input:
                print("\aNo command entered. Please type 'help' for available commands.")
                continue
            parts = user_input.split()
            cmd = parts[0]
            args = parts[1:]
            if not process_command(cmd, args, positions):
                break
        except KeyboardInterrupt:
            print("\nExiting TradeCLI. Goodbye!")
            break
        except Exception as ex:
            print(f"An error occurred: {ex}")


if __name__ == "__main__":
    main()