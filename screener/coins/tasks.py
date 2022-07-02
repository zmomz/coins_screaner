from django.forms.models import model_to_dict
from celery import shared_task
import requests

from .models import Coin

@shared_task
def get_coins_data():
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false'
    data = requests.get(url).json()
    coins =[]
    for coin in data:
        obj, created = Coin.objects.get_or_create(symbol=coin['symbol'])
        obj.name = coin['name']
        obj.symbol = coin['symbol']
        obj.volume = coin['total_volume']

        if obj.price > coin['current_price']:
            state = 'fall'
        elif obj.price == coin['current_price']:
            state = 'same'
        elif obj.price < coin['current_price']:
            state = 'raise'
        obj.price = coin['current_price']
        obj.rank = coin['market_cap_rank']
        obj.image = coin['image']

        obj.save()

        new_data=model_to_dict(obj)
        new_data.update({'state':state})

        coins.append(new_data)
