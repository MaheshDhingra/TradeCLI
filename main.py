import math
import os
import random
import matplotlib.pyplot as plt
from typing import Dict, List, Set

GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

market_data: Dict[str, Dict] = {}
favourites: Set[str] = set()

def get_market_price(ticker: str) -> float:
  ticker = ticker.upper()
  if ticker not in market_data:
    market_data[ticker] = {
      't': 0,
      'initial': 100,
      'amplitude': 20,
      'frequency': 0.1,
      'phase': (hash(ticker) % 6283) / 1000,
      'history': [],
      'price': 100.0
    }
  data = market_data[ticker]
  data['t'] += 1
  new_price = data['initial'] + data['amplitude'] * math.sin(data['frequency'] * data['t'] + data['phase'])
  data['price'] = round(new_price, 2)
  data['history'].append(data['price'])
  # Maintain only the latest 100 history entries
  if len(data['history']) > 100:
    data['history'] = data['history'][-100:]
  return data['price']

def show_chart(ticker: str) -> None:
  """
  Plot the historical prices for the ticker symbol.
  """
  ticker = ticker.upper()
  # Generate at least one update if history is empty
  price = get_market_price(ticker)
  data = market_data[ticker]
  if not data['history']:
    print(f"{GREEN}Not enough data to plot chart for {ticker}{RESET}")
    return
  plt.figure(figsize=(8, 4))
  plt.plot(range(len(data['history'])), data['history'], marker='o', label=ticker)
  plt.title(f"Price History for {ticker}")
  plt.xlabel("Time steps")
  plt.ylabel("Price")
  plt.grid(True)
  plt.legend()
  plt.show()

def show_popular_pairs() -> None:
  popular_pairs = [
    "EUR/USD", "GBP/USD", "USD/JPY",
    "AUD/USD", "BTC/USD", "TSLA", "AAPL", "GOOGL"
  ]
  print(f"{BOLD}{GREEN}Popular Pairs and Tickers:{RESET}")
  for pair in popular_pairs:
    print("  " + pair)
  print()

def add_favourite(ticker: str) -> None:
  ticker = ticker.upper()
  favourites.add(ticker)
  print(f"Added {ticker} to favourites.")

def show_favourites() -> None:
  if not favourites:
    print("No favourites yet.")
  else:
    print(f"{BOLD}{GREEN}Favourite Tickers:{RESET}")
    for fav in favourites:
      print("  " + fav)
  print()

def show_screener() -> None:
  # Dummy screener: list tickers with an upward trend in their last two price entries.
  print(f"{BOLD}{GREEN}Screener Results:{RESET}")
  detected = False
  for ticker, data in market_data.items():
    if len(data['history']) >= 2 and data['history'][-1] > data['history'][-2]:
      print(f"  {ticker} is trending up. Current price: ${data['price']}")
      detected = True
  if not detected:
    print("  No trending tickers detected.")
  print()

def clear_screen() -> None:
  """Clear the terminal screen."""
  os.system('cls' if os.name == 'nt' else 'clear')

def print_banner() -> None:
  banner = f"{BOLD}{GREEN}" + "="*50 + "\n" \
       + "            TradeCLI\n" \
       + "="*50 + f"{RESET}"
  print(banner)

def print_help() -> None:
  """Display the help message."""
  print(f"{BOLD}{GREEN}Available Commands:{RESET}")
  print("  help                   - Show this help message")
  print("  quote <ticker>         - Get the current market quote for the ticker")
  print("  buy <ticker> <qty>     - Buy specified number of shares")
  print("  sell <ticker> <qty>    - Sell specified number of shares")
  print("  positions              - Show current holdings and profit/loss")
  print("  chart <ticker>         - Display price history chart")
  print("  dashboard              - Show overall portfolio performance")
  print("  popular                - Show popular trading pairs")
  print("  favourite <ticker>     - Add a ticker to favourites")
  print("  favourites             - List favourite tickers")
  print("  screener               - Run the price screener")
  print("  clear / cls            - Clear the terminal screen")
  print("  exit                   - Exit the terminal")

def process_command(command: str, args: List[str], positions: Dict[str, Dict]) -> bool:
  """
  Process the provided command and update positions accordingly.
  Returns False if the command is exit, otherwise True.
  """
  command = command.lower()
  if command == 'help':
    print_help()

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
      total_cost = round(price * qty, 2)
      if ticker in positions:
        positions[ticker]['qty'] += qty
        positions[ticker]['cost'] += total_cost
      else:
        positions[ticker] = {"qty": qty, "cost": total_cost}
      print(f"Bought {qty} shares of {ticker} at ${price}/share for ${total_cost}.")

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
        positions[ticker]['qty'] -= qty
        positions[ticker]['cost'] -= avg_cost * qty
        if positions[ticker]['qty'] == 0:
          del positions[ticker]
        print(f"Sold {qty} shares of {ticker} at ${price}/share for ${total_value}.")

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
    if not positions:
      print("No positions held.")
    else:
      total_invested = 0.0
      total_value = 0.0
      print("Portfolio Dashboard:")
      for ticker, pos in positions.items():
        current_price = get_market_price(ticker)
        avg_cost = pos['cost'] / pos['qty']
        value = round(current_price * pos['qty'], 2)
        profit_loss = round(value - pos['cost'], 2)
        total_invested += pos['cost']
        total_value += value
        print(f"  {ticker}:")
        print(f"    Shares: {pos['qty']}")
        print(f"    Avg Cost: ${avg_cost:.2f}")
        print(f"    Current Price: ${current_price}")
        print(f"    Market Value: ${value}")
        print(f"    Profit/Loss: ${profit_loss}")
      overall_pl = round(total_value - total_invested, 2)
      print(f"Overall Invested: ${round(total_invested, 2)}")
      print(f"Current Portfolio Value: ${round(total_value, 2)}")
      print(f"Overall Profit/Loss: ${overall_pl}")

  elif command == 'chart':
    if len(args) != 1:
      print("Usage: chart <ticker>")
    else:
      ticker = args[0].upper()
      show_chart(ticker)

  elif command == 'popular':
    show_popular_pairs()

  elif command == 'favourite':
    if len(args) != 1:
      print("Usage: favourite <ticker>")
    else:
      add_favourite(args[0])

  elif command == 'favourites':
    show_favourites()

  elif command == 'screener':
    show_screener()

  elif command in ['clear', 'cls']:
    clear_screen()

  elif command == 'exit':
    print("Exiting TradeCLI. Goodbye!")
    return False

  else:
    print("Unknown command. Type 'help' for available commands.")

  random_notification()
  return True

def main() -> None:
  """
  Main function to run the TradeCLI.
  """
  clear_screen()
  print_banner()
  print(f"{BOLD}{GREEN}Welcome to the TradeCLI!{RESET}")
  print("Type 'help' to see available commands.")

  positions: Dict[str, Dict] = {}  # e.g., positions['AAPL'] = {"qty": 10, "cost": 1000.0}

  # Command loop
  while True:
    try:
      user_input = input(f"{BOLD}{GREEN}TradeCLI> {RESET}").strip()
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