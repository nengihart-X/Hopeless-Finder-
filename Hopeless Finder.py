
import logging
from datetime import datetime, timedelta
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import json
import time
import hashlib
import pickle
from pprint import pprint

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SENDGRID_API_KEY = os.getenv('')  # Ensure this is set correctly in your environment
SENDGRID_SENDER_EMAIL = ''
VERIFIED_EMAILS = ['', '']  # Replace with your verified email addresses
CACHE_DURATION = 300  # Cache duration in seconds
API_REQUEST_DELAY = 60  # Delay between API requests in seconds
LOOP_DELAY = 300  # Delay between each loop iteration in seconds (5 minutes)

def send_email_notification(subject: str, message: str, recipient: str) -> None:
    email = Mail(
        from_email=SENDGRID_SENDER_EMAIL,
        to_emails=recipient,
        subject=subject,
        plain_text_content=message)

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(email)
        logging.info(f"Email sent successfully with status code {response.status_code}")
        logging.info(f"Response body: {response.body}")
        logging.info(f"Response headers: {response.headers}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def get_coins_from_coingecko() -> dict:
    return {'BTC': 'bitcoin', 'ETH': 'ethereum', 'USDT': 'tether', 'BUSD': 'binance-usd', 'SOL': 'solana', 'USDC': 'usd-coin', 'XRP': 'ripple', 'DOGE': 'dogecoin', 'TRX': 'tron', 'LTC': 'litecoin'}

def get_exchanges_from_coingecko() -> dict:
    return {'binance': 'Binance', 'coinbase': 'Coinbase', 'okx': 'OKx', 'bybit': 'Bybit', 'upbit': 'Upbit', 'kraken': 'Kraken', 'gate.io': 'Gate.io', 'huobi': 'Huobi', 'bitfinex': 'Bitfinex'}

def cache_data(key: str, data: dict, duration: int = CACHE_DURATION) -> None:
    with open(f'cache_{key}.pkl', 'wb') as f:
        pickle.dump({'data': data, 'expiry': datetime.now() + timedelta(seconds=duration)}, f)

def get_cached_data(key: str) -> dict:
    try:
        with open(f'cache_{key}.pkl', 'rb') as f:
            cache = pickle.load(f)
            if cache['expiry'] > datetime.now():
                return cache['data']
    except FileNotFoundError:
        pass
    return None

def get_prices_from_exchange(coingecko_id: str) -> dict:
    cache_key = hashlib.md5(coingecko_id.encode()).hexdigest()
    cached_data = get_cached_data(cache_key)
    if cached_data:
        logging.info(f"Using cached data for {coingecko_id}")
        return cached_data

    url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/tickers"
    response = requests.get(url)
    time.sleep(API_REQUEST_DELAY)  # Wait to avoid hitting the rate limit

    if response.status_code == 200:
        data = response.json()
        if 'tickers' in data:
            prices = {}
            for ticker in data['tickers']:
                exchange = ticker['market']['name']
                price = ticker['converted_last']['usd']
                prices[exchange] = price
            cache_data(cache_key, prices)
            return prices
        else:
            logging.warning(f"No 'tickers' key found in API response for {coingecko_id}: {json.dumps(data, indent=2)}")
    else:
        logging.warning(f"Failed to fetch data for {coingecko_id}: {response.status_code} {response.text}")

    return {}

def find_arbitrage_opportunities(user_email: str) -> None:
    coins = get_coins_from_coingecko()
    exchanges = get_exchanges_from_coingecko()

    if not coins or not exchanges:
        logging.error("Failed to fetch coins or exchanges from CoinGecko. Exiting.")
        return

    arbitrage_opportunities = []

    for symbol, coingecko_id in coins.items():
        logging.info(f"Processing {symbol}...")
        prices = get_prices_from_exchange(coingecko_id)
        logging.info(f"Prices for {symbol}: {prices}")

        if len(prices) < 2:
            logging.info(f"Not enough prices for {symbol}. Skipping.")
            continue

        # Find the exchange with the lowest price (buy)
        buy_exchange = min(prices, key=prices.get)
        buy_price = prices[buy_exchange]
        logging.info(f"Buy {symbol} on {buy_exchange} at ${buy_price:.2f}")

        # Find the exchange with the highest price (sell)
        sell_exchange = max(prices, key=prices.get)
        sell_price = prices[sell_exchange]
        logging.info(f"Sell {symbol} on {sell_exchange} at ${sell_price:.2f}")

        # Calculate the profit in USD
        profit_usd = sell_price - buy_price
        logging.info(f"Profit: ${profit_usd:.2f}")

        if profit_usd > 0:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = (f"Arbitrage opportunity found: Buy {symbol} on {buy_exchange} at ${buy_price:.2f} "
                       f"and sell on {sell_exchange} at ${sell_price:.2f} for a profit of ${profit_usd:.2f} "
                       f"at {timestamp}")
            logging.info(message)
            pprint(message)
            arbitrage_opportunities.append(message)

    if arbitrage_opportunities:
        all_opportunities = "\n\n".join(arbitrage_opportunities)
        send_email_notification("Arbitrage Opportunity Alert", all_opportunities, user_email)
        logging.info("Email notification sent for arbitrage opportunities.")
    else:
        logging.info("No arbitrage opportunities found.")
if __name__ == "__main__":
    logging.info("Starting arbitrage opportunity search...")
    pprint("Starting arbitrage opportunity search...")

    while True:
        for email in VERIFIED_EMAILS:
            find_arbitrage_opportunities(email)
        logging.info("Arbitrage opportunity search completed. Resting for 5 minutes...")
        pprint("Arbitrage opportunity search completed. Resting for 5 minutes...")
        time.sleep(LOOP_DELAY)
