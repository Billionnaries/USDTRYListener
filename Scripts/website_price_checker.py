import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

class WebsitePriceChecker:
    def __init__(self, url, chrome_driver_path):
        self.url = url
        self.driver = None
        self.last_website_price = None
        self.chrome_driver_path = chrome_driver_path

    def start_browser(self):
        """
        Function to start the website from driver.
        :return:
        """
        service = Service(self.chrome_driver_path)
        self.driver = webdriver.Chrome(service = service)
        self.driver.get(self.url)
        time.sleep(5)

    def setup_price_observer(self):
        """
        Function to start price
        :return:
        """
        script = """
            const targetNode = document.querySelector('span[data-currency="USD"][data-type="amount"]');
            window.priceChanged = null;

            const observer = new MutationObserver((mutationsList, observer) => {
                mutationsList.forEach(mutation => {
                    if (mutation.type === 'characterData' || mutation.type === 'childList') {
                        window.priceChanged = targetNode.textContent;
                    }
                });
            });
            observer.observe(targetNode, { childList: true, subtree: true, characterData: true });
        """
        self.driver.execute_script(script)

    def monitor_website_price(self, usdt_checker, guild_id):
        """
        Function to monitor website updates.
        :param usdt_checker:
        :param guild_id:
        :return:
        """
        try:
            while True:
                new_price = self.driver.execute_script("return window.priceChanged;")

                if new_price:
                    new_price = float(new_price.replace(",", "."))
                    new_price_rounded = round(new_price, 4)
                    last_price_rounded = round(self.last_website_price,
                                               4) if self.last_website_price is not None else None
                    if last_price_rounded is None or new_price_rounded != last_price_rounded:
                        print(f"Website USD/TRY price updated: {new_price_rounded}")
                        if self.last_website_price is not None:
                            usdt_checker.compare_prices(new_price_rounded, guild_id)
                        self.last_website_price = new_price_rounded

            time.sleep(1)
        except KeyboardInterrupt:
            print("Stopped monitoring.")
        finally:
            self.driver.quit()
