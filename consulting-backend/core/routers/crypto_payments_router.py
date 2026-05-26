from __future__ import annotations
import requests

from fastapi import APIRouter

from pydantic_models import PaymentSchema

from settings import get_settings

db_uri = get_settings().db_uri
api_key = get_settings().api_key
# db_uri='postgresql+psycopg2://postgres:1234@127.0.0.1:5432/consultingdb'

crypto_payments_router = APIRouter(
    prefix="/crypto/payments",
)


@crypto_payments_router.post("/")
def make_payment(data: PaymentSchema):
    # 1. make call to GET API Status
    # 2. make call to GET check available currencies 
    # 3. make call to GET Minimum payment amount
    # 4. make call to GET Estimated price and check if it is larger than the minimum payment amount
    # 5. make call to POST Create payment 
    # 6. make call to GET Payment status, and display it to customer 
    # 7. make call to GET List of payments ----------------- this step is not important/unimportant 
    headers = {'x-api-key': api_key}
    headers_for_payment = {'x-api-key': api_key, 'Content-Type': 'application/json'}

    data_for_request = {
        "price_amount": data.price,
        "price_currency": "usd",
        "pay_currency": "usdttrc20",
        "ipn_callback_url": "https://nowpayments.io",
        "order_id": "RGDBP-21315",
        "order_description": "Apple Macbook Pro 2019 x 1"
    }

    api_status = requests.get("https://api.nowpayments.io/v1/status")
    available_currencies = requests.get("https://api.nowpayments.io/v1/currencies?fixed_rate=true", headers=headers)
    minimum_amount = requests.get("https://api.nowpayments.io/v1/min-amount?currency_from=usdttrc20&currency_to=usdttrc20&fiat_equivalent=usd&is_fixed_rate=False&is_fee_paid_by_user=False", headers=headers)
    estimated_price = requests.get(f"https://api.nowpayments.io/v1/estimate?amount=10&currency_from=usdttrc20&currency_to=usdttrc20", headers=headers)
    # created_payment = requests.post("https://api.nowpayments.io/v1/payment", headers=headers_for_payment, json=data_for_request)
    print("api_status: ", api_status)
    print(available_currencies)
    print(minimum_amount)
    print(estimated_price)
    # print(created_payment.text)
    # print(created_payment.json())

    # Here I need to change status of consultation to "Paid"
    # Update: I can't change status of consultation here, 
    # because consultants can have access to contacts of customer before they pay
    # ------------------------------------------------------------
    # Instead I need to check status of payment every 1 minute, and when status of payment will be set up to "finished"
    # than I will set status to "Paid"

    # consultation_dao = ConsultationsDAO(uri=db_uri)
    # changed_status = consultation_dao.change_status_of_consultation(consultation_id=data.consultation_id, updated_status="UnPaid")
    # print("Status: ", changed_status)
    response = {
        "payment_id": "5745459419",
        "payment_status": "waiting",
        "pay_address": "3EZ2uTdVDAMFXTfc6uLDDKR6o8qKBZXVkj",
        "price_amount": 3999.5,
        "price_currency": "usd",
        "pay_amount": 0.17070286,
        "pay_currency": "btc",
        "order_id": "RGDBP-21314",
        "order_description": "Apple Macbook Pro 2019 x 1",
        "ipn_callback_url": "https://nowpayments.io",
        "created_at": "2020-12-22T15:00:22.742Z",
        "updated_at": "2020-12-22T15:00:22.742Z",
        "purchase_id": "5837122679",
        "amount_received": "null",
        "payin_extra_id": "null",
        "smart_contract": "",
        "network": "btc",
        "network_precision": 8,
        "time_limit": "null",
        "burning_percent": "null",
        "expiration_estimate_date": "2020-12-23T15:00:22.742Z"
    }
    return response
    # return created_payment.json()


@crypto_payments_router.get("/api-status")
async def check_api_status():
    response = requests.get("https://api.nowpayments.io/v1/status")
    return response.json()


@crypto_payments_router.get("/available-currencies")
async def get_available_currencies():
    response = requests.get("https://api.nowpayments.io/v1/currencies")
    return response.json()


# @payments_router.post("/create-payment")
# async def create_payment(payment_request: PaymentRequest):
#     payment_data = {
#         "amount": payment_request.amount,
#         "currency_from": payment_request.currency_from,
#         "currency_to": payment_request.currency_to,
#         "payout_address": payment_request.payout_address
#     }
#     response = requests.post("https://api.nowpayments.io/v1/payment", json=payment_data)
#     return response.json()


@crypto_payments_router.get("/payment-status/{payment_id}")
async def get_payment_status(payment_id: str):
    response = requests.get(f"https://api.nowpayments.io/v1/payment/{payment_id}")
    return response.json()

@crypto_payments_router.get("/list-payments")
async def list_payments():
    response = requests.get("https://api.nowpayments.io/v1/payments")
    return response.json()