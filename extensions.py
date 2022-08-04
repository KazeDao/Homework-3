import requests
import json
from Config import keys


class APIException(Exception):
    pass


class Converter:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        if quote == base:
            raise APIException(f'Вы пытаетесь перевести одну и ту же валюту {base}.')

        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise APIException(f'Не удается обработать валюту, такой валюты не найдено: {quote}')
        try:
            base_ticker = keys[base]
        except KeyError:
            raise APIException(f'Не удается обработать валюту, такой валюты не найдено: {base}')
        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удается обработать количество {amount}')
        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')
        total_base = json.loads(r.content)[keys[base]] * amount
        total_base = round(total_base, 4)

        return total_base
