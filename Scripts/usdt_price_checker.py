import requests
import time
import asyncio


class USDTPriceChecker:
    def __init__(self, fetch_interval, discord_bot, slack_bot, loop):
        self.fetch_interval = fetch_interval
        self.discord_bot = discord_bot
        self.slack_bot = slack_bot
        self.loop = loop
        self.last_binance_price = None
        self.last_btcturk_price = None
        self.last_website_price = None
        self.threshold = self.discord_bot.threshold if self.discord_bot else 0.005  # Use 0.005 as default
        self.binance_alert_sent = False
        self.btcturk_alert_sent = False

    def set_threshold(self, new_threshold):
        self.threshold = new_threshold
        self.binance_alert_sent = False
        self.btcturk_alert_sent = False
        if self.discord_bot:
            self.discord_bot.save_threshold_to_file(new_threshold)
        print(f"Threshold updated to {new_threshold}% and warning flags reset")

    def get_usdttry_price_binance(self):
        """
        Function to get USDTRY Price from Binance API
        :return:
        """
        url = "https://api.binance.com/api/v3/ticker/price"
        params = {'symbol': 'USDTTRY'}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return float(data['price'])
        else:
            return None

    def get_usdttry_price_btcturk(self):
        """
                Function to get USDTRY Price from Binance API
                :return:
                """
        url = "https://api.btcturk.com/api/v2/ticker"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for pair in data['data']:
                if pair['pair'] == 'USDTTRY':
                    return float(pair['last'])
        else:
            return None

    def fetch_usdt_prices(self):
        """
        Function to get USDTRY prices from Binance and BtcTurk Api in
        :return:
        """
        while True:
            binance_price = self.get_usdttry_price_binance()
            if binance_price is not None:
                self.last_binance_price = binance_price

            # Fetch BtcTurk price
            btcturk_price = self.get_usdttry_price_btcturk()
            if btcturk_price is not None:
                self.last_btcturk_price = btcturk_price
            if self.last_website_price:
                self.compare_prices(self.last_website_price, self.discord_bot.guild_id)
            time.sleep(self.fetch_interval)

    def compare_prices(self, website_price, guild_id):
        """
        Function to compare Binance and BtcTurk prices with website USDTRY price
        :param website_price:
        :param guild_id:
        :return:
        """
        threshold_value = website_price * (self.threshold / 100)
        if self.threshold >= 1:
            recovery_value = website_price * ((self.threshold - 1) / 100)
        else:
            recovery_value = website_price * (self.threshold / 2 / 100)
        binance_diff = abs(website_price - self.last_binance_price)
        btcturk_diff = abs(website_price - self.last_btcturk_price)


        if binance_diff > threshold_value and not self.binance_alert_sent:
            message = f"Price difference with Binance. Last Binance Price {self.last_binance_price} Last Website price {website_price}"
            print(message)
            self.discord_bot.loop.create_task(self.discord_bot.notify_threshold_exceeded(message))
            asyncio.run_coroutine_threadsafe(self.slack_bot.send_message(message), self.loop)
            self.binance_alert_sent = True

        elif self.binance_alert_sent and binance_diff <= recovery_value:
            message = f"Price difference DROPPED to {binance_diff:.2f} with Binance. Last Binance Price {self.last_binance_price} Last Website price {website_price}"
            print(message)
            self.discord_bot.loop.create_task(self.discord_bot.notify_threshold_exceeded( message))
            asyncio.run_coroutine_threadsafe(self.slack_bot.send_message(message), self.loop)
            self.binance_alert_sent = False

        if btcturk_diff > threshold_value and not self.btcturk_alert_sent:
            message = f"Price difference with BtcTurk. Last BtcTurk Price {self.last_btcturk_price} Last Website price {website_price}"
            print(message)
            self.discord_bot.loop.create_task(self.discord_bot.notify_threshold_exceeded( message))
            asyncio.run_coroutine_threadsafe(self.slack_bot.send_message(message), self.loop)
            self.btcturk_alert_sent = True
            
        elif self.btcturk_alert_sent and btcturk_diff <= recovery_value:
            message = f"Price difference DROPPED to {btcturk_diff:.2f} with BtcTurk. Last BtcTurk Price {self.last_btcturk_price} Last Website price {website_price}"
            print(message)
            self.discord_bot.loop.create_task(self.discord_bot.notify_threshold_exceeded( message))
            asyncio.run_coroutine_threadsafe(self.slack_bot.send_message(message), self.loop)
            self.btcturk_alert_sent = False
