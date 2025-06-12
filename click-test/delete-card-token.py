

from config import *
import requests
import time
import hashlib

# Vaqt tamg‘asi va imzo
timestamp = str(int(time.time()))
digest = hashlib.sha1((timestamp + secret_key).encode()).hexdigest()

# Headerlar
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Auth': f'{merchant_user_id}:{digest}:{timestamp}'
}

# So‘rov yuborish
response = requests.delete(
    f'https://api.click.uz/v2/merchant/card_token/{service_id}/{card_token}',
    headers=headers
)

# Natijani chiqarish
print(response.json())