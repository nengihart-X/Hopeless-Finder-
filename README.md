Arbitrage Opportunity Finder

This project continuously monitors cryptocurrency prices across various exchanges and identifies arbitrage opportunities. When an arbitrage opportunity is found, it sends an email notification to the specified recipients.
Features

    Fetches cryptocurrency prices from CoinGecko
    Identifies arbitrage opportunities by comparing prices across different exchanges
    Sends email notifications when opportunities are found
    Caches API responses to minimize redundant requests and avoid rate limits

Setup
Prerequisites

    Python 3.6+
    SendGrid API Key (for sending email notifications)



Set up environment variables for the SendGrid API Key:

bash

export SENDGRID_API_KEY='your_sendgrid_api_key'
export SENDGRID_SENDER_EMAIL='your_verified_sender_email'

Replace VERIFIED_EMAILS with your verified email addresses in the code:

python

    VERIFIED_EMAILS = ['email1@example.com', 'email2@example.com']

Usage

Run the script:

bash

python arbitrage_opportunity_finder.py

The script will start searching for arbitrage opportunities and send email notifications to the specified recipients when opportunities are found.
Code Overview
Main Components

    send_email_notification: Sends an email notification using SendGrid.
    get_coins_from_coingecko: Returns a dictionary of supported coins and their CoinGecko IDs.
    get_exchanges_from_coingecko: Returns a dictionary of supported exchanges and their names.
    cache_data: Caches API responses to minimize redundant requests.
    get_cached_data: Retrieves cached data if available and not expired.
    get_prices_from_exchange: Fetches cryptocurrency prices from CoinGecko and caches the results.
    find_arbitrage_opportunities: Finds arbitrage opportunities by comparing prices across different exchanges and sends email notifications.

Logging

The script uses Python's built-in logging module to log various information, including API responses, cache usage, identified arbitrage opportunities, and email sending status.
Contributing

Feel free to contribute to the project by submitting issues or pull requests.
License

This project is licensed under the MIT License.
