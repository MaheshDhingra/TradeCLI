# 🚀 TradeCLI v0.1.3 – Command-Line Trading Terminal

This release delivers major stability improvements and bug fixes for all analytics, gainers/losers, and screener commands. All commands now handle ticker data robustly, preventing crashes from non-ticker entries in market data. The CLI is more reliable and user-friendly than ever.

## 📘 Available Commands

- **help**  
  Show all available commands
- **quote <ticker>**  
  Get the current market quote for a given ticker
- **buy <ticker> <qty>**  
  Buy the specified number of shares
- **sell <ticker> <qty>**  
  Sell the specified number of shares
- **positions**  
  View your current holdings and profit/loss
- **chart <ticker>**  
  Display a price history chart
- **dashboard**  
  View overall portfolio performance
- **analytics**  
  Show advanced analytics (best/worst performer, average return, win rate)
- **alert**  
  Set price/volume alerts
- **integrations**  
  Integrations menu
- **exportcsv**  
  Export portfolio to CSV
- **customize**  
  Customize dashboard
- **popular**  
  Show popular trading pairs with live prices and your holdings
- **gainers**  
  Show top gainers and losers for the session
- **lasttrade**  
  Show last trade time for tickers
- **favourite <ticker>**  
  Add a ticker to your favourites list
- **removefav**  
  Remove a ticker from your favourites list
- **favourites**  
  View your list of favourite tickers
- **screener**  
  Run a price screener for potential opportunities
- **clear / cls**  
  Clear the terminal screen
- **exit**  
  Exit the terminal

---

**What's New in v0.1.3:**
- Fixed all 'NoneType' errors in analytics, gainers, and screener commands
- Improved error handling for all ticker data operations
- All commands now robustly check for valid ticker data before processing
- Documentation and help updated for clarity and accuracy

---

**Note:**
- All prices, charts, and market data are fetched live from Alpha Vantage (no API key setup needed for price/market data).
- Only real trading (buy/sell) requires credentials.

---

Thanks for using TradeCLI! If you have feedback or ideas, please open an issue or pull request.