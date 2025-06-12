from config import *
import requests
import time
import hashlib

amount = 100000 
transaction_parameter = 'order_001'

timestamp = str(int(time.time()))
digest = hashlib.sha1((timestamp + secret_key).encode()).hexdigest()

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Auth': f'{merchant_user_id}:{digest}:{timestamp}'
}

data = {
    'service_id': int(service_id),
    'card_token': card_token,
    'amount': amount,
    'transaction_parameter': transaction_parameter
}

response = requests.post(
    'https://api.click.uz/v2/merchant/card_token/payment',
    json=data,
    headers=headers
)

print(response.json())