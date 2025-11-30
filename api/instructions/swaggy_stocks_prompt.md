## 🧠 Prompt: Scrape SwaggyStocks Tickers

You are a web-scraping assistant. Visit the following SwaggyStocks pages and extract all unique stock tickers mentioned on each page.

### Target URLs:
1. https://swaggystocks.com/dashboard/wallstreetbets/ticker-sentiment  
2. https://swaggystocks.com/dashboard/stocks/market-sentiment  
3. https://swaggystocks.com/dashboard/short-squeeze/stocks-list  

### Instructions:
1. For each page, extract **all stock tickers** shown on the dashboard (e.g., “AAPL”, “TSLA”, “NVDA”).  
2. Combine tickers from all three pages into a **single flat array**.  
3. Remove duplicates and ensure all tickers are uppercase.  
4. Return the final result **only** in JSON array format, like this:

```json
["AAPL", "TSLA", "NVDA", "PLTR", "AMC", "GME"]
```