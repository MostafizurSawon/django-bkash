import requests
from django.conf import settings

class BKashError(Exception):
    pass

def _headers_with_token(id_token: str):
    return {
        "Authorization": id_token,          # token for subsequent calls
        "X-APP-Key": settings.BKASH_APP_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def get_token():
    url = f"{settings.BKASH_BASE_URL}/tokenized/checkout/token/grant"
    payload = {
        "app_key": settings.BKASH_APP_KEY,
        "app_secret": settings.BKASH_APP_SECRET,
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        # IMPORTANT: bKash expects these as headers (not HTTP Basic Auth)
        "username": settings.BKASH_USERNAME,
        "password": settings.BKASH_PASSWORD,
    }
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    data = r.json()
    if "id_token" not in data:
        raise BKashError(f"Failed to get token: {data}")
    return data["id_token"]

def create_payment(id_token: str, amount: str, invoice_id: str, payer_reference: str = "payer"):
    url = f"{settings.BKASH_BASE_URL}/tokenized/checkout/create"
    payload = {
        "mode": "0011",
        "payerReference": payer_reference,
        "callbackURL": settings.BKASH_CALLBACK_URL,
        "amount": str(amount),
        "currency": "BDT",
        "intent": "sale",
        "merchantInvoiceNumber": str(invoice_id),
    }
    headers = _headers_with_token(id_token)
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    data = r.json()
    if "paymentID" not in data:
        raise BKashError(f"Create payment failed: {data}")
    return data

def execute_payment(id_token: str, payment_id: str):
    url = f"{settings.BKASH_BASE_URL}/tokenized/checkout/execute"
    payload = {"paymentID": payment_id}
    headers = _headers_with_token(id_token)
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    return r.json()