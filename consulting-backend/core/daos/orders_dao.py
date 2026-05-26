from __future__ import annotations

import logging

from sqlalchemy import func, select, update, or_
from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import aliased, joinedload

from clients.DBClient import DBClient
from database.models import Order, User


logger = logging.getLogger(__name__)


class OrdersDAO:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, uri: str):
        self._db_client = DBClient(uri)

    def get_all_consultations(self):
        query = self._base_consultations_query()
        return self._get_all_consultations(query)

    def get_consultation_by_id(self, consultation_id: int):
        query = self._base_consultations_query().where(Order.id == consultation_id)
        return self._get_one_consultation_by_query(query)

    def get_consultations_by_user_id(self, user_id):
        # query = select(Order).where(or_(Order.client_id == user_id, Order.consultant_id == user_id))
        Client = aliased(User)
        Consultant = aliased(User)
        
        query = self._base_consultations_query().where(
            or_(Order.client_id == user_id, Order.consultant_id == user_id)
        )
        return self._get_all_consultations(query)

    # Orders, which is created by client
    def get_consultations_by_client_id(self, client_id):
        query = self._base_consultations_query().where(Order.client_id == client_id)
        return self._get_all_consultations(query)
    
    # Orders, which is created by consultant
    def get_consultations_by_consultant_id(self, consultant_id):
        query = self._base_consultations_query().where(Order.consultant_id == consultant_id)
        return self._get_all_consultations(query)
    
    def get_unpaid_consultations(self, consultant_id):
        query = self._base_consultations_query().where(Order.consultant_id == consultant_id).where(Order.status == "new")
        return self._get_all_consultations(query)
    
    def get_paid_consultations(self, consultant_id):
        query = self._base_consultations_query().where(Order.consultant_id == consultant_id).where(Order.status.in_(["confirmed", "in_progress", "completed"]))
        return self._get_all_consultations(query)

    def get_all_consultations_for_admin(self):
        query = self._base_consultations_query()
        return self._get_all_consultations(query)

    def create_consultation(self, consultation: Order):
        return self._db_client.create_object(consultation)
    
    def patch_consultation(self, consultation_id: int, updated_consultation: dict[str, any]):
        # todo: check for unique fields ?
        # todo: is it a bug: DB records does not get updated when the same info passed several times?
        query = update(Order).where(Order.id == consultation_id).values(first_name=updated_consultation['first_name'], last_name=updated_consultation['last_name'], 
                                    email=updated_consultation['email'], password=updated_consultation['password'], phone_number=updated_consultation['phone_number'],
                                    telegram=updated_consultation['telegram'], viber=updated_consultation['viber'], photo=updated_consultation['photo'], 
                                    description=updated_consultation['description']).returning(Order.id, Order.first_name, Order.last_name, Order.email)
        return self._db_client.update_object(query)
    
    def change_status_of_consultation(self, consultation_id: int, updated_status: str):
        query = update(Order).where(Order.id == consultation_id).values(status=updated_status)
        return self._db_client.update_object(query)

    def get_orders_stats(self):
        total_orders = self._db_client.select_number_of_rows_by_query(select(func.count(Order.id)))
        stats = {"total_orders": total_orders or 0}
        for current_status in ["new", "confirmed", "in_progress", "completed", "cancelled"]:
            count = self._db_client.select_number_of_rows_by_query(
                select(func.count(Order.id)).where(Order.status == current_status)
            )
            stats[f"{current_status}_orders"] = count or 0
        return stats




    def delete_consultation(self, consultation: Order):
        return self._db_client.delete_object(consultation)

    def _base_consultations_query(self):
        return (
            select(Order)
            .options(
                joinedload(Order.client).load_only(User.id, User.first_name, User.last_name, User.email, User.phone_number),
                joinedload(Order.consultant).load_only(User.id, User.first_name, User.last_name, User.email, User.phone_number),
            )
            .order_by(Order.created_at.desc())
        )
    
    def _get_one_consultation_by_query(self, query: Select):
        try:
            return self._db_client.select_one_object_by_query(query)

        except OperationalError as e:
            # NOTE: case for the "DBAPIError" when user id is not a valid UUID
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))

    def _get_all_consultations(self, query: Select):
        try:
            return self._db_client.select_all_objects(query)

        except OperationalError as e:
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))
