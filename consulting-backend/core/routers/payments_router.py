from __future__ import annotations
import httpx

from fastapi import APIRouter

from pydantic_models import PaymentBody, CardPaymentType
from daos.card_payments_dao import CardPaymentsDAO
from database.models import CardPayment

from settings import get_settings

db_uri = get_settings().db_uri
api_key = get_settings().api_key
# db_uri='postgresql+psycopg2://postgres:1234@127.0.0.1:5432/consultingdb'

payments_router = APIRouter(
    prefix="/payments",
)


@payments_router.post('/get-payment-details', summary='Get payment details(Uncompleted route)')
def getPaymentDetails(data: CardPaymentType):
    pass


@payments_router.post("/proxy/create-card-payment")
def proxy(paymentBody: PaymentBody):
    print("paymentBody: ", paymentBody)
    with httpx.Client() as client:
        response = client.post(
            'https://pay.fondy.eu/api/checkout/url/', json=paymentBody.model_dump())
        print(response.json())
        return response.json()


@payments_router.post("/proxy/accept-card-payment")
def proxy(body: CardPaymentType):
    card_payments_dao = CardPaymentsDAO(uri=db_uri)
    paymentForInsert = CardPayment(rrn=body.rrn, masked_card=body.masked_card, sender_cell_phone=body.sender_cell_phone,
                                   response_signature_string=body.response_signature_string, response_status=body.response_status,
                                   sender_account=body.sender_account, fee=body.fee, rectoken_lifetime=body.rectoken_lifetime,
                                   reversal_amount=body.reversal_amount, settlement_amount=body.settlement_amount, actual_amount=body.actual_amount,
                                   order_status=body.order_status, response_description=body.response_description, verification_status=body.verification_status,
                                   order_time=body.order_time, actual_currency=body.actual_currency,
                                   order_id=body.order_id, parent_order_id=body.parent_order_id,
                                   merchant_data=body.merchant_data, tran_type=body.tran_type, eci=body.eci, settlement_date=body.settlement_date,
                                   payment_system=body.payment_system, rectoken=body.rectoken, approval_code=body.approval_code, merchant_id=body.merchant_id,
                                   settlement_currency=body.settlement_currency, payment_id=body.payment_id, product_id=body.product_id, currency=body.currency,
                                   card_bin=body.card_bin, response_code=body.response_code, card_type=body.card_type, amount=body.amount, sender_email=body.sender_email,
                                   signature=body.signature)

    created_payment = card_payments_dao.create_cardPayment(paymentForInsert)

    # if insert was successfull, send email to user

    return created_payment
