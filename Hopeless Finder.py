
import asyncio
import aiohttp
import logging
from datetime import datetime
import time

# Constants
CACHE_DURATION = 120
API_REQUEST_DELAY = 30
LOOP_DELAY = 120
MIN_PROFIT_THRESHOLD = 1.0
TRADING_FEES = 0.001
NETWORK_FEES_PERCENTAGE = 0.0005
MAX_RETRIES = 5  # Maximum number of retries for 429 error
RETRY_DELAY = 10  # Initial delay in seconds before retrying

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_coins_from_coingecko():
    return {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'USDT': 'tether',
        'SOL': 'solana',
        'USDC': 'usd-coin',
        'XRP': 'ripple',
        'DOGE': 'dogecoin',
        'BNB': 'binancecoin',
        'TRX': 'tron'
    }

def check_arbitrage_viability(buy_price: float, sell_price: float, trading_fees: float = TRADING_FEES) -> tuple:
    """
    Checks whether arbitrage is viable based on buy and sell prices, including fees.
    Returns a tuple indicating viability and net profit.
    """
    buy_fee = buy_price * trading_fees
    sell_fee = sell_price * trading_fees
    network_fee = buy_price * NETWORK_FEES_PERCENTAGE

    total_cost = buy_price + buy_fee + network_fee
    total_revenue = sell_price - sell_fee

    net_profit = total_revenue - total_cost
    is_viable = net_profit > MIN_PROFIT_THRESHOLD

    return is_viable, net_profit

async def process_arbitrage(session, symbol, coingecko_id):
    """
    Processes arbitrage for a given cryptocurrency symbol and CoinGecko ID.
    Fetches data, checks for arbitrage opportunities, and prints the result.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/tickers"
    retries = 0
    delay = RETRY_DELAY

    while retries < MAX_RETRIES:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'tickers' in data:
                        prices = {t['market']['name']: t['converted_last']['usd'] for t in data['tickers'] if t['converted_last']['usd']}

                        if len(prices) < 2:
                            print(f"Insufficient market data for {symbol}. Skipping.")
                            return

                        buy_exchange = min(prices, key=prices.get)
                        sell_exchange = max(prices, key=prices.get)
                        buy_price = prices[buy_exchange]
                        sell_price = prices[sell_exchange]

                        is_viable, net_profit = check_arbitrage_viability(buy_price, sell_price)

                        if is_viable:
                            print(f"🚨 Arbitrage Alert 🚨")
                            print(f"💎 {symbol}")
                            print(f"📉 Buy: ${buy_price:.4f} ({buy_exchange})")
                            print(f"📈 Sell: ${sell_price:.4f} ({sell_exchange})")
                            print(f"💰 Net Profit: ${net_profit:.4f}")
                            print(f"📊 Profit Margin: {((net_profit/buy_price) * 100):.2f}%")
                            print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
                        else:
                            print(f"⚠️ Low Profit Alert ⚠️")
                            print(f"💎 {symbol}")
                            print(f"📉 Buy: ${buy_price:.4f} ({buy_exchange})")
                            print(f"📈 Sell: ${sell_price:.4f} ({sell_exchange})")
                            print(f"💰 Net Profit: ${net_profit:.4f} (below ${MIN_PROFIT_THRESHOLD})")
                            print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
                        return
                    else:
                        print(f"No tickers found for {symbol}.")
                        return
                elif response.status == 429:
                    # Too many requests, apply exponential backoff
                    print(f"Rate limit hit for {symbol}, retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    retries += 1
                    delay *= 2  # Exponential backoff
                else:
                    print(f"Failed to fetch data for {symbol}. HTTP Status: {response.status}")
                    return
        except aiohttp.ClientError as e:
            print(f"Error fetching data for {symbol}: {e}")
            return

    print(f"Max retries reached for {symbol}. Skipping...")

async def main():
    """
    Main function to start arbitrage checking for multiple coins.
    """
    coins = get_coins_from_coingecko()

    async with aiohttp.ClientSession() as session:
        for symbol, coingecko_id in coins.items():
            await process_arbitrage(session, symbol, coingecko_id)

if __name__ == "__main__":
    asyncio.run(main())
