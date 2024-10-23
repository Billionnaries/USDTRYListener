import threading
import discord
import asyncio
from discord_bot import DiscordBot
from usdt_price_checker import USDTPriceChecker
from website_price_checker import WebsitePriceChecker
from slack_bot import SlackBot



def update_threshold(new_threshold, usdt_checker):
    """ This function will be passed as the threshold callback. """
    usdt_checker.set_threshold(new_threshold)

async def start_operations(usdt_checker):
    price_thread = threading.Thread(target=usdt_checker.fetch_usdt_prices)
    price_thread.daemon = True
    price_thread.start()

    website_checker = WebsitePriceChecker('https://canlidoviz.com/doviz-kurlari/dolar', 'chromedriver.exe')
    website_checker.start_browser()
    website_checker.setup_price_observer()

    website_thread = threading.Thread(target=website_checker.monitor_website_price, args=(usdt_checker, GUILD_ID))
    website_thread.daemon = True
    website_thread.start()

async def main():
    fetch_interval = 5
    slack_bot = SlackBot(SLACK_TOKEN, SLACK_CHANNEL)
    discord_bot = DiscordBot(guild_id = GUILD_ID,
                             threshold_callback=None)
    loop = asyncio.get_running_loop()
    usdt_checker = USDTPriceChecker(fetch_interval, discord_bot, slack_bot, loop)
    discord_bot.threshold_callback = lambda new_threshold: update_threshold(new_threshold, usdt_checker)
    bot_task = asyncio.create_task(discord_bot.start(DISCORD_TOKEN))
    await start_operations(usdt_checker)
    await bot_task

if __name__ == "__main__":
    asyncio.run(main())
