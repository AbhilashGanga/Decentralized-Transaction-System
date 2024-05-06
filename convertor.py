from forex_python.converter import CurrencyRates

def convert_currency(type, amt):
    c = CurrencyRates()
    return amt * c.get_rate(type,'USD')

def convert_crypto(type, amt):
    
    rates = {
        'BTC': 37311,
        'ETH': 2052.94,
        'USDT':1,
        'Dogecoin':0.077,
        'BNB':231.47
    }

    return rates[type]*amt