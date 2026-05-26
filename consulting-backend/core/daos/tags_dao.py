from __future__ import annotations

import logging

from sqlalchemy import select, update
from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import OperationalError

from clients.DBClient import DBClient
from database.models import Tag

logger = logging.getLogger(__name__)


class TagsDAO:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, uri: str):
        self._db_client = DBClient(uri)

    def get_tag_by_id(self, Tag_id: int):
        query = select(Tag).where(Tag.id == Tag_id)
        return self._get_one_client_by_query(query)

    # def get_Tag_for_operation(self, Tag_id: int):
    #     query = select(Tag).where(Tag.id == Tag_id)
    #     return self._db_client.select_one_object_for_operation(query)

    def get_all_Tags(self):
        query = select(Tag).distinct(Tag.name)
        return self._get_all_Tags(query)

    def create_Tag(self, Tag: Tag):
        return self._db_client.create_object(Tag)

    def patch_Tag(self, Tag_id: int, updated_Tag: dict[str, any]):
        # todo: check for unique fields ?
        # todo: is it a bug: DB records does not get updated when the same info passed several times?
        query = update(Tag).where(Tag.id == Tag_id).values(name=updated_Tag['name'], description=updated_Tag['description']).returning(Tag.id, Tag.name, Tag.description)
        return self._db_client.update_object(query)

    def delete_Tag(self, Tag: Tag):
        return self._db_client.delete_object(Tag)

    def _get_one_client_by_query(self, query: Select):
        try:
            return self._db_client.select_one_object_by_query(query)

        except OperationalError as e:
            # NOTE: case for the "DBAPIError" when user id is not a valid UUID
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))

    def _get_all_Tags(self, query: Select):
        try:
            return self._db_client.select_all_objects(query)

        except OperationalError as e:
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))
