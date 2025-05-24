import math
import random
import matplotlib.pyplot as plt
import os  # Added for clearing the terminal

# Simulated market data storage
market_data = {}

def get_market_price(ticker):
  """
  Use a sine-wave based algorithm to simulate price.
  Initialize ticker data if not present.
  """
  ticker = ticker.upper()
  if ticker not in market_data:
    # Initialize with fixed parameters
    market_data[ticker] = {
      't': 0,
      'initial': 100,
      'amplitude': 20,
      'frequency': 0.1,
      'phase': (hash(ticker) % 6283) / 1000,  # Phase offset in radians
      'history': [],
      'price': 100
    }
  data = market_data[ticker]
  data['t'] += 1
  new_price = data['initial'] + data['amplitude'] * math.sin(data['frequency'] * data['t'] + data['phase'])
  data['price'] = round(new_price, 2)
  data['history'].append(data['price'])
  # Keep only last 100 entries
  if len(data['history']) > 100:
    data['history'] = data['history'][-100:]
  return data['price']

def show_chart(ticker):
  ticker = ticker.upper()
  # Ensure ticker data is available
  price = get_market_price(ticker)
  data = market_data[ticker]
  if not data['history']:
    print("Not enough data to plot chart for", ticker)
    return
  plt.plot(list(range(len(data['history']))), data['history'], marker='o')
  plt.title(f"Price History for {ticker}")
  plt.xlabel("Time steps")
  plt.ylabel("Price")
  plt.grid(True)
  plt.show()

def main():
  print("Welcome to the TradeCLI Terminal!")
  print("Type 'help' to see available commands.")
  
  # positions: store quantity and cumulative cost for each ticker
  positions = {}  # e.g., positions['AAPL'] = {"qty": 10, "cost": 1000.0}
  
  while True:
    try:
      user_input = input("TradeCLI> ").strip()
      if not user_input:
        print("\aNo command entered. Please type 'help' to see available commands.")
        continue

      parts = user_input.split()
      command = parts[0].lower()
      args = parts[1:]
      
      if command == 'help':
        print("Commands:")
        print("  quote <ticker>         - Retrieve the current market quote for the specified ticker symbol")
        print("  buy <ticker> <qty>     - Buy number of shares for the ticker")
        print("  sell <ticker> <qty>    - Sell number of shares for the ticker")
        print("  positions              - Show current holdings and profit/loss")
        print("  chart <ticker>         - Display price history chart for the ticker")
        print("  dashboard              - Show portfolio performance")
        print("  clear                  - Clear the terminal screen")  # Added command info
        print("  exit                   - Exit the terminal")
      
      elif command == 'quote':
        if len(args) != 1:
          print("Usage: quote <ticker>")
          continue
        ticker = args[0].upper()
        price = get_market_price(ticker)
        print(f"Quote for {ticker}: ${price}")
      
      elif command == 'buy':
        if len(args) != 2:
          print("Usage: buy <ticker> <qty>")
          continue
        ticker = args[0].upper()
        try:
          qty = int(args[1])
          if qty <= 0:
            raise ValueError
        except ValueError:
          print("Quantity must be a positive integer.")
          continue
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
          continue
        ticker = args[0].upper()
        try:
          qty = int(args[1])
          if qty <= 0:
            raise ValueError
        except ValueError:
          print("Quantity must be a positive integer.")
          continue
        if ticker not in positions or positions[ticker]['qty'] < qty:
          print("Insufficient shares to sell.")
          continue
        price = get_market_price(ticker)
        total_value = round(price * qty, 2)
        # Adjust cost basis proportionally
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
          total_unrealized = 0
          for ticker, pos in positions.items():
            # Update the market price for an up-to-date value
            current_price = get_market_price(ticker)
            avg_cost = pos['cost'] / pos['qty']
            unrealized = round((current_price - avg_cost) * pos['qty'], 2)
            total_unrealized += unrealized
            print(f"  {ticker}: {pos['qty']} shares at avg cost ${avg_cost:.2f}, current ${current_price} -> P/L: ${unrealized}")
          print(f"Total Unrealized P/L: ${total_unrealized}")
      
      elif command == 'dashboard':
        if not positions:
          print("No positions held.")
        else:
          total_invested = 0
          total_value = 0
          print("Portfolio Dashboard:")
          for ticker, pos in positions.items():
            current_price = get_market_price(ticker)
            avg_cost = pos['cost'] / pos['qty']
            value = current_price * pos['qty']
            profit_loss = value - pos['cost']
            total_invested += pos['cost']
            total_value += value
            print(f"  {ticker}:")
            print(f"    Shares: {pos['qty']}")
            print(f"    Avg Cost: ${avg_cost:.2f}")
            print(f"    Current Price: ${current_price}")
            print(f"    Value: ${value:.2f}")
            print(f"    Profit/Loss: ${profit_loss:.2f}")
          overall_pl = total_value - total_invested
          print(f"Overall Invested: ${total_invested:.2f}")
          print(f"Current Portfolio Value: ${total_value:.2f}")
          print(f"Overall Profit/Loss: ${overall_pl:.2f}")
      
      elif command == 'chart':
        if len(args) != 1:
          print("Usage: chart <ticker>")
          continue
        ticker = args[0].upper()
        show_chart(ticker)
      
      elif command == 'clear':
        os.system('cls' if os.name == 'nt' else 'clear')
      
      elif command == 'cls':
        os.system('cls' if os.name == 'nt' else 'clear')
        
      elif command == 'exit':
        print("Exiting TradeCLI Terminal. Goodbye!")
        break
      
      else:
        print("Unknown command. Type 'help' for available commands.")
    except KeyboardInterrupt:
      print("\nExiting TradeCLI Terminal. Goodbye!")
      break

if __name__ == "__main__":
  main()