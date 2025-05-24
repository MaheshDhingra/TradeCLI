import random

def main():
  print("Welcome to the Trading CLI Terminal!")
  print("Type 'help' to see available commands.")
  
  positions = {}
  
  while True:
    try:
      user_input = input("TradeCLI> ").strip()
      if not user_input:
        continue

      parts = user_input.split()
      command = parts[0].lower()
      
      if command == 'help':
        print("Commands:")
        print("  quote <ticker>         - Get a quote for the ticker")
        print("  buy <ticker> <qty>     - Buy number of shares for the ticker")
        print("  sell <ticker> <qty>    - Sell number of shares for the ticker")
        print("  positions              - Show current holdings")
        print("  exit                   - Exit the terminal")
      
      elif command == 'quote':
        if len(parts) != 2:
          print("Usage: quote <ticker>")
          continue
        ticker = parts[1].upper()
        price = round(random.uniform(10, 500), 2)
        print(f"Quote for {ticker}: ${price}")
      
      elif command == 'buy':
        if len(parts) != 3:
          print("Usage: buy <ticker> <qty>")
          continue
        ticker = parts[1].upper()
        try:
          qty = int(parts[2])
          if qty <= 0:
            raise ValueError
        except ValueError:
          print("Quantity must be a positive integer.")
          continue
        price = round(random.uniform(10, 500), 2)
        total_cost = round(price * qty, 2)
        positions[ticker] = positions.get(ticker, 0) + qty
        print(f"Bought {qty} shares of {ticker} at ${price}/share for ${total_cost}.")
      
      elif command == 'sell':
        if len(parts) != 3:
          print("Usage: sell <ticker> <qty>")
          continue
        ticker = parts[1].upper()
        try:
          qty = int(parts[2])
          if qty <= 0:
            raise ValueError
        except ValueError:
          print("Quantity must be a positive integer.")
          continue
        if ticker not in positions or positions[ticker] < qty:
          print("Insufficient shares to sell.")
          continue
        price = round(random.uniform(10, 500), 2)
        total_value = round(price * qty, 2)
        positions[ticker] -= qty
        if positions[ticker] == 0:
          del positions[ticker]
        print(f"Sold {qty} shares of {ticker} at ${price}/share for ${total_value}.")
      
      elif command == 'positions':
        if not positions:
          print("No positions held.")
        else:
          print("Current Positions:")
          for ticker, qty in positions.items():
            print(f"  {ticker}: {qty} shares")
      
      elif command == 'exit':
        print("Exiting Trading CLI Terminal. Goodbye!")
        break
      
      else:
        print("Unknown command. Type 'help' for available commands.")
    except KeyboardInterrupt:
      print("\nExiting Trading CLI Terminal. Goodbye!")
      break

if __name__ == "__main__":
  main()