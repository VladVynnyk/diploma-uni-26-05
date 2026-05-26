from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import OperationalError

from clients.DBClient import DBClient
from database.models import CardPayment
from pydantic_models import CardPaymentType


logger = logging.getLogger(__name__)


class CardPaymentsDAO:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, uri: str):
        self._db_client = DBClient(uri)

    def get_cardPayment_by_id(self, cardPayment_id: int) -> CardPaymentType | None:
        query = select(CardPayment).where(CardPayment.id == cardPayment_id)
        return self._get_one_cardPayment_by_query(query)

    def get_all_cardPayments(self) -> CardPaymentType | None:
        query = select(CardPayment)
        return self._get_all_cardPayments(query)

    def create_cardPayment(self, cardPayment: CardPayment) -> CardPaymentType | None:
        return self._db_client.create_object(cardPayment)

    # def patch_cardPayment(self, cardPayment_id: int, updated_cardPayment: dict[str, any]) -> CardPaymentType | None:
        # todo: check for unique fields ?
        # todo: is it a bug: DB records does not get updated when the same info passed several times?
        # query = update(CardPayment).where(CardPayment.id == cardPayment_id).values(cardPaymentname=updated_cardPayment['cardPaymentname'], email=updated_cardPayment['email'], password=updated_cardPayment['password'], created_at=datetime.now(
        # )).returning(CardPayment.id, CardPayment.cardPaymentname, CardPayment.email, CardPayment.password, CardPayment.created_at)
        # return self._db_client.update_object(query)

    def delete_cardPayment(self, cardPayment: CardPayment) -> CardPaymentType | None:
        return self._db_client.delete_object(cardPayment)

    def _get_one_cardPayment_by_query(self, query: Select) -> CardPaymentType | None:
        try:
            return self._db_client.select_one_object_by_query(query)

        except OperationalError as e:
            # NOTE: case for the "DBAPIError" when cardPayment id is not a valid UUID
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))

    def _get_all_cardPayments(self, query: Select) -> CardPaymentType | None:
        try:
            return self._db_client.select_all_objects(query)

        except OperationalError as e:
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))
