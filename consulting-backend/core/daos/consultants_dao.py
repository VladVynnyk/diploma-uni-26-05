from __future__ import annotations

import logging

from sqlalchemy import select, update
from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import OperationalError
from sqlalchemy import func

from sqlalchemy.orm import defer

from clients.DBClient import DBClient
from database.models import Consultant, Tag, association_table

logger = logging.getLogger(__name__)


class ConsultantsDAO:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, uri: str):
        self._db_client = DBClient(uri)

    def get_consultant_by_id(self, consultant_id: int):
        query = select(Consultant).where(Consultant.id == consultant_id)
        return self._get_one_consultant_by_query(query)
    
    def get_consultant_by_email(self, consultant_email: str):
        query = select(Consultant).where(Consultant.email == consultant_email)
        return self._get_one_consultant_by_query(query)
    
    def get_all_consultants_by_name_or_surname(self, name: str):

        query = select(Consultant).filter(func.lower(Consultant.first_name).ilike(f"{name}%"))
        second_query = select(Consultant).filter(func.lower(Consultant.last_name).ilike(f"{name}%"))

        consultants = self._get_all_consultants(query)
        if len(consultants) == 0:
            differ_consultants = self._get_all_consultants(second_query)
            return differ_consultants
        return consultants
    

    def filter_consultants_by_category_and_price(self, category: str, lower_price: int, higher_price: int):
        query = select(Consultant).join(association_table).join(Tag).filter((Tag.name == category)).filter((Consultant.price<=higher_price)).filter((Consultant.price>=lower_price))
        return self._get_all_consultants(query)

    def filter_consultants_by_price_only(self, lower_price: int, higher_price: int):
        query = select(Consultant).join(association_table).join(Tag).filter((Consultant.price<=higher_price)).filter((Consultant.price>=lower_price))
        return self._get_all_consultants(query)
        

    def get_consultants_by_tag(self, tag: str):
        query = select(Consultant).join(association_table).join(Tag).filter((Tag.name == tag))
        return self._get_all_consultants(query)
    
    def get_consultants_with_tags(self):
        # This query returns all data with password
        query = select(Consultant)
        # This query exludes password from query
        newQuery = query.options(defer(Consultant.password))
        return self._get_all_consultants(newQuery) 
    

    def get_all_consultants(self):
        query = select(Consultant)
        return self._get_all_consultants(query)

    def create_consultant(self, consultant: Consultant):
        return self._db_client.create_object(consultant)

    # Update of consultant
    def patch_consultant(self, consultant_id: int, updated_consultant: dict[str, any]):
        # todo: check for unique fields ?
        # todo: is it a bug: DB records does not get updated when the same info passed several times?
        query = update(Consultant).where(Consultant.id == consultant_id).values(first_name=updated_consultant['first_name'], last_name=updated_consultant['last_name'], 
                                    email=updated_consultant['email'], password=updated_consultant['password'], phone_number=updated_consultant['phone_number'],
                                    telegram=updated_consultant['telegram'], viber=updated_consultant['viber'], photo=updated_consultant['photo'], 
                                    description=updated_consultant['description'], price=updated_consultant['price'], tags=updated_consultant['tags']).returning(Consultant.id, Consultant.first_name, Consultant.last_name, Consultant.email)
        return self._db_client.update_object(query)
    
    # Functions for updating separate fields
    def patch_name_of_consultant(self, consultant_id: int, updated_value: str):
        query = update(Consultant).where(Consultant.id == consultant_id).values(first_name=updated_value)
        return self._db_client.update_object(query)

    def patch_surname_of_consultant(self, consultant_id: int, updated_value: str):
        query = update(Consultant).where(Consultant.id == consultant_id).values(last_name=updated_value)
        return self._db_client.update_object(query)
    
    def patch_description_of_consultant(self, consultant_id: int, updated_value: str):
        query = update(Consultant).where(Consultant.id == consultant_id).values(description=updated_value)
        return self._db_client.update_object(query)
    
    def patch_password_of_consultant(self, consultant_id: int, updated_value: str):
        query = update(Consultant).where(Consultant.id == consultant_id).values(password=updated_value)
        return self._db_client.update_object(query)

    def patch_price_of_consultant(self, consultant_id: int, updated_value: int):
        query = update(Consultant).where(Consultant.id == consultant_id).values(price=updated_value)
        return self._db_client.update_object(query)
    
    def patch_tags_of_consultant(self, consultant_id: int, updated_value: list):
        query = update(Consultant).where(Consultant.id == consultant_id).values(tags=updated_value)
        return self._db_client.update_object(query)
    
    def patch_photo_of_consultant(self, consultant_id: int, updated_value: str):
        query = update(Consultant).where(Consultant.id == consultant_id).values(photo=updated_value)
        return self._db_client.update_object(query)

    def delete_consultant(self, consultant: Consultant):
        return self._db_client.delete_object(consultant)

    def _get_one_consultant_by_query(self, query: Select):
        try:
            return self._db_client.select_one_object_by_query(query)

        except OperationalError as e:
            # NOTE: case for the "DBAPIError" when user id is not a valid UUID
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))

    def _get_all_consultants(self, query: Select):
        try:
            return self._db_client.select_all_objects(query)

        except OperationalError as e:
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))
