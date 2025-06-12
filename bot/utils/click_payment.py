import hashlib
import aiohttp
import logging
import time
from typing import Dict, Any
from configuration import conf

class ClickPayment:
    def __init__(self, service_id: str, merchant_id: str, secret_key: str, merchant_user_id: str):
        self.service_id = service_id
        self.merchant_id = merchant_id
        self.secret_key = secret_key
        self.merchant_user_id = merchant_user_id
        self.base_url = "https://api.click.uz/v2/merchant/"
        
    def _generate_signature(self, data: Dict[str, Any]) -> str:
        timestamp = str(int(time.time()))
        digest = hashlib.sha1((timestamp + self.secret_key).encode()).hexdigest()
        return digest
    
    async def create_card_token(self, card_number: str, expiration_date: str) -> Dict[str, Any]:
        payload = {
            "service_id": self.service_id,
            "card_number": card_number,
            "expire_date": expiration_date,
            "temporary": 0
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/card_token/request", json=payload, headers=headers) as response:
                if response.status == 200 or response.status == 201:
                    return await response.json()
                else:
                    error_data = await response.text()
                    logging.error(f"Failed to create card token: {error_data}")
                    return {"error": True, "message": f"Request failed with status {response.status}"}
    
    async def verify_card_token(self, sms_code: str, card_token: str) -> Dict[str, Any]:
        payload = {
            "service_id": self.service_id,
            "card_token": card_token,
            "sms_code": sms_code
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Auth': f"{self.merchant_user_id}:{self._generate_signature(payload)}:{int(time.time())}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/card_token/verify", json=payload, headers=headers) as response:
                if response.status == 200 or response.status == 201:
                    return await response.json()
                else:
                    error_data = await response.text()
                    logging.error(f"Failed to verify card token: {error_data}")
                    return {"error": True, "message": f"Request failed with status {response.status}"}

    async def payment_with_token(self, card_token: str, amount: int, transaction_parameter: str) -> Dict[str, Any]:
        payload = {
            "service_id": self.service_id,
            "card_token": card_token,
            "amount": amount,
            "transaction_parameter": transaction_parameter
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Auth': f"{self.merchant_user_id}:{self._generate_signature(payload)}:{int(time.time())}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/card_token/payment", json=payload, headers=headers) as response:
                if response.status == 200 or response.status == 201:
                    return await response.json()
                else:
                    error_data = await response.text()
                    logging.error(f"Failed to process payment: {error_data}")
                    return {"error": True, "message": f"Request failed with status {response.status}"}
                

click_payment_instance = ClickPayment(
    service_id=conf.payment.service_id,
    merchant_id=conf.payment.merchant_id,
    secret_key=conf.payment.secret_key,
    merchant_user_id=conf.payment.merchant_user_id
)
