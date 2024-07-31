import requests
import json
import time


api_key = "72649336-6501-43f2-8552-7137ae393b2e"
base_url = "https://pro-api.coinmarketcap.com/v1/"


symbols = ["BTC", "ETH", "LTC"]
profit_threshold = 0.10  
exchanges = ["binance", "kraken", "coinbase"]

def get_price(symbol, exchange):
    
    url = f"{base_url}cryptocurrency/quotes/latest"
    params = {
        "symbol": symbol,
        "convert": "USD",
        "CMC_PRO_API_KEY": api_key
    }
    headers = {
        "X-CMC_PRO_API_KEY": api_key
    }

    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    
    if response.status_code == 200:
       
        if 'data' in data and symbol in data['data']:
            quote = data["data"][symbol]["quote"]
            if exchange in quote:
                price = quote[exchange]["price"]
                return price
            else:
                return None
        else:
            return None
    else:
        return None

def find_arbitrage_opportunities():
    start_time = time.time()
    opportunities_found = False

    while time.time() - start_time < 180:  
        
        prices = {}

        
        for symbol in symbols:
            prices[symbol] = {}
            for exchange in exchanges:
                price = get_price(symbol, exchange)
                if price is not None:
                    prices[symbol][exchange] = price

       
        for symbol, exchange_prices in prices.items():
            buy_exchange = None
            buy_price = None
            for exchange, price in exchange_prices.items():
                if buy_exchange is None or price < buy_price:
                    buy_exchange = exchange
                    buy_price = price

            for exchange, sell_price in exchange_prices.items():
                if exchange != buy_exchange:
                    price_diff = (sell_price - buy_price) / buy_price
                    if price_diff >= profit_threshold:
                        print(f"Arbitrage opportunity found: Buy {symbol} on {buy_exchange} at ${buy_price:.2f} and sell on {exchange} at ${sell_price:.2f} for a profit of {price_diff*100:.2f}%")
                        opportunities_found = True

        if opportunities_found:
            break

        time.sleep(5)  

    if not opportunities_found:
        print("No arbitrage opportunities found within 3 minutes.")

# Run the bot
find_arbitrage_opportunities()