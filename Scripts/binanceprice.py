import requests

def get_usdttry_price_binance():
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {
        'symbol': 'USDTTRY'
    }
    response = requests.get(url, params=params)
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return float(data['price'])
    else:
        return None
def get_usdttry_price_btcturk():
    url = "https://api.btcturk.com/api/v2/ticker"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for pair in data['data']:
            if pair['pair'] == 'USDTTRY':
                return float(pair['last'])
    else:
        return None
btcturk_usdttry_price = get_usdttry_price_btcturk()
binance_usdttry_price = get_usdttry_price_binance()
print(f"Current USDT/TRY price on BtcTurk: {btcturk_usdttry_price}")
print(f"Current USDT/TRY price on Binance: {binance_usdttry_price}")
