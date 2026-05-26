from __future__ import annotations

import logging

from sqlalchemy import select, update
from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import OperationalError

from clients.DBClient import DBClient
from database.models import Client

logger = logging.getLogger(__name__)


class ClientsDAO:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, uri: str):
        self._db_client = DBClient(uri)

    def get_client_by_id(self, client_id: int):
        query = select(Client).where(Client.id == client_id)
        return self._get_one_client_by_query(query)

    def get_client_by_email(self, client_email: str):
        query = select(Client).where(Client.email == client_email)
        return self._get_one_client_by_query(query)

    # def get_client_for_operation(self, client_id: int):
    #     query = select(Client).where(Client.id == client_id)
    #     return self._db_client.select_one_object_for_operation(query)

    def get_all_clients(self):
        query = select(Client)
        return self._get_all_clients(query)

    def create_client(self, client: Client):
        return self._db_client.create_object(client)

    def patch_client(self, client_id: int, updated_client: dict[str, any]):
        # todo: check for unique fields ?
        # todo: is it a bug: DB records does not get updated when the same info passed several times?
        query = update(Client).where(Client.id == client_id).values(first_name=updated_client['first_name'], last_name=updated_client['last_name'], email=updated_client['email'], password=updated_client['password']).returning(Client.id, Client.first_name, Client.last_name, Client.email)
        return self._db_client.update_object(query)
    
    def patch_name_of_client(self, client_id: int, updated_value: str):
        query = update(Client).where(Client.id == client_id).values(first_name=updated_value)
        return self._db_client.update_object(query)

    def patch_surname_of_client(self, client_id: int, updated_value: str):
        query = update(Client).where(Client.id == client_id).values(last_name=updated_value)
        return self._db_client.update_object(query)
    
    def patch_password_of_client(self, client_id: int, updated_value: str):
        query = update(Client).where(Client.id == client_id).values(password=updated_value)
        return self._db_client.update_object(query)

    def delete_client(self, client: Client):
        return self._db_client.delete_object(client)

    def _get_one_client_by_query(self, query: Select):
        try:
            return self._db_client.select_one_object_by_query(query)

        except OperationalError as e:
            # NOTE: case for the "DBAPIError" when user id is not a valid UUID
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))

    def _get_all_clients(self, query: Select):
        try:
            return self._db_client.select_all_objects(query)

        except OperationalError as e:
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))
