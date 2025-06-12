from config import * 

import requests

card_number = '9860030801117356'
expire_date = '0226'
temporary = 1  # Vaqtinchalik token uchun 1, aks holda 0

data = {
    'service_id': int(service_id),
    'card_number': card_number,
    'expire_date': expire_date,
    'temporary': temporary
}
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# So‘rov yuborish
response = requests.post('https://api.click.uz/v2/merchant/card_token/request', json=data, headers=headers)
print(response.json())
