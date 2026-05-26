from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from database.models import Order, User
from pydantic_models import ConsultationSchema, RegisteredUserSchema, UnregisteredUserSchema
from daos.orders_dao import OrdersDAO
from daos.users_dao import UsersDAO
from deps import get_current_user
from serializers import serialize_order

from routers.users.read import get_user

from settings import get_settings

from utils import send_fucking_email

db_uri = get_settings().db_uri

orders_router = APIRouter(
    prefix="/orders",
)

# @orders_router.post("/")
# def add_consultation(consultation: ConsultationSchema):
#     consultation_for_insert = Order(price=consultation.price, status="Unpaid", 
#                                     consultant_id=consultation.consultant_id, client_id=consultation.client_id)
#     print("Consultation: ", consultation)
#     consultations_dao = OrdersDAO(uri=db_uri)
#     created_consultation = consultations_dao.create_consultation(consultation_for_insert)
    
#     #For sending emails we need:
#     # 1. Get consultant which will receive email
#     # 2. call function and paste email of consultant in parameters
#     # send_fucking_email()

#     current_consultant = get_user(user_id=consultation.consultant_id)
#     # message = f"{current_consultant['first_name']} {current_consultant['last_name']}, у вас користувач {consultation.first_name_of_client} {consultation.surname_of_client} замовив консультацію. Будь ласка зв'яжіться з ним якнайшвидше.".encode('utf-8')
   
#     # name_and_surname_of_client = str(consultation.first_name_of_client) + str(consultation.surname_of_client)
#     # message = """\
#     #     У вас замовлення!
#     #     У вас користувач {name} {surname} замовив консультацію. Будь ласка зв'яжіться з ним якнайшвидше.""".format(name=consultation.first_name_of_client, surname=consultation.surname_of_client).encode('utf-8')
#     # # send_fucking_email(current_consultant['email'], message=message)

#     return created_consultation


@orders_router.post("/")
def add_consultation(consultation_data: ConsultationSchema):
    consultation = consultation_data.consultation
    auth_flow = {
        "email": None,
        "requires_complete_registration": False,
        "should_login": False,
        "message": None,
    }

    # Handle registered user case
    if isinstance(consultation, RegisteredUserSchema):
        if consultation.consultant_id == consultation.client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot order your own consultation.",
            )

        consultation_for_insert = Order(
            price=consultation.price, 
            status="new",
            topic=consultation.topic,
            message=consultation.message,
            scheduled_at=consultation.scheduled_at,
            duration_minutes=consultation.duration_minutes,
            consultant_id=consultation.consultant_id, 
            client_id=consultation.client_id
        )
    # Handle unregistered user case
    elif isinstance(consultation, UnregisteredUserSchema):
        users_dao = UsersDAO(uri=db_uri)
        existing_user = users_dao.get_user_by_email(consultation.email)
        current_user_id = None

        if existing_user is not None:
            existing_user_record = existing_user[0]
            current_user_id = existing_user_record.id
            auth_flow["email"] = consultation.email

            if existing_user_record.password:
                auth_flow["should_login"] = True
                auth_flow["message"] = "Користувач уже зареєстрований. Увійдіть у систему, щоб відстежувати статус консультації."
            else:
                auth_flow["requires_complete_registration"] = True
                auth_flow["message"] = "Заяву створено. Завершіть реєстрацію, щоб відстежувати статус консультації."
        else:
            user_for_insert = User(
                first_name=consultation.first_name,
                last_name=consultation.last_name,
                email=consultation.email,
                phone_number=consultation.phone_number,
            )
            created_user = users_dao.create_user(user_for_insert)
            current_user_id = created_user.id
            auth_flow["email"] = consultation.email
            auth_flow["requires_complete_registration"] = True
            auth_flow["message"] = "Заяву створено. Завершіть реєстрацію, щоб відстежувати статус консультації."

        consultation_for_insert = Order(
            price=consultation.price, 
            status="new",
            topic=consultation.topic,
            message=consultation.message,
            scheduled_at=consultation.scheduled_at,
            duration_minutes=consultation.duration_minutes,
            consultant_id=consultation.consultant_id, 
            client_id=current_user_id
        )
    
    print("Consultation: ", consultation)
    consultations_dao = OrdersDAO(uri=db_uri)
    created_consultation = consultations_dao.create_consultation(consultation_for_insert)

    consultation_with_relations = consultations_dao.get_consultation_by_id(created_consultation.id)
    return {
        "order": serialize_order(consultation_with_relations[0]),
        "auth_flow": auth_flow,
    }


@orders_router.get("/")
def get_consultations():
    consultations_dao = OrdersDAO(uri=db_uri)
    consultations = consultations_dao.get_all_consultations()
    return [serialize_order(order) for order in consultations]


@orders_router.get("/{id}")
def get_consultation(consultation_id: str):
    consultations_dao = OrdersDAO(uri=db_uri)
    consultation = consultations_dao.get_consultation_by_id(consultation_id)
    response = {"id": consultation[0].id, "first_name_of_client": consultation[0].first_name_of_client, "surname_of_client": consultation[0].surname_of_client, 
                "phone_number_of_client": consultation[0].phone_number_of_client, "messenger": consultation[0].messenger, "consultant_id": consultation[0].consultant_id}
    return response


# get all consultations which is not paid for single consultant
@orders_router.get("/unpaid/consultant/{consultant_id}", summary="Get not paid consultations for single consultant")
def get_consultations(consultant_id: str):
    consultations_dao = OrdersDAO(uri=db_uri)
    consultations = consultations_dao.get_unpaid_consultations(consultant_id)
    return [serialize_order(order) for order in consultations]

# get all consultations which is paid for single consultant
@orders_router.get("/paid/consultant/{consultant_id}", summary="Get paid consultations for single consultant")
def get_consultations(consultant_id: str):
    consultations_dao = OrdersDAO(uri=db_uri)
    consultations = consultations_dao.get_paid_consultations(consultant_id)
    return [serialize_order(order) for order in consultations]

# get consultations created by client
@orders_router.get("/account/client/{client_id}", summary="Get consultations for single client")
def get_consultations(client_id: str, current_user: User = Depends(get_current_user)):
    if str(current_user.id) != client_id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot view these consultations.")
    consultations_dao = OrdersDAO(uri=db_uri)
    consultations = consultations_dao.get_consultations_by_client_id(client_id)
    return [serialize_order(order, viewer=current_user) for order in consultations]

# get consultations, created by consultant
@orders_router.get("/account/consultant/{consultant_id}", summary="Get consultations for consultant")
def get_consultations(consultant_id: str, current_user: User = Depends(get_current_user)):
    if str(current_user.id) != consultant_id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot view these consultations.")
    consultations_dao = OrdersDAO(uri=db_uri)
    consultations = consultations_dao.get_consultations_by_consultant_id(consultant_id)
    return [serialize_order(order, viewer=current_user) for order in consultations]

@orders_router.get("/account/{user_id}")
def get_consultations(user_id: str, current_user: User = Depends(get_current_user)):
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot view these consultations.")
    orders_dao = OrdersDAO(uri=db_uri)
    orders = orders_dao.get_consultations_by_user_id(user_id)
    return [serialize_order(order, viewer=current_user) for order in orders]

@orders_router.patch("/{id}")
def update_consultation(consultation_id: str, updated_consultation: ConsultationSchema):
    consultations_dao = OrdersDAO(uri=db_uri)
    # print("model dump: ", updated_consultant.model_dump())
    consultation_to_update = consultations_dao.patch_consultation(consultation_id, updated_consultation.model_dump())
    return consultation_to_update


@orders_router.delete("/{id}")
def delete_consultant(consultation_id: str):
    consultations_dao = OrdersDAO(uri=db_uri)
    consultation_to_delete = consultations_dao.delete_consultation(consultation_id)

    deleted_consultation = consultations_dao.delete_consultation(consultation_to_delete[0])

    response = {"id": deleted_consultation[0].id, "first_name_of_client": deleted_consultation[0].first_name_of_client, "surname_of_client": deleted_consultation[0].surname_of_client, 
                "phone_number_of_client": deleted_consultation[0].phone_number_of_client, "messenger": deleted_consultation[0].messenger, "consultant_id": deleted_consultation[0].consultant_id}
    return response
