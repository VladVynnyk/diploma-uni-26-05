from __future__ import annotations

import logging

from sqlalchemy import select, update
from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload

from clients.DBClient import DBClient
from database.models import Review, User


logger = logging.getLogger(__name__)


class ReviewsDAO:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, uri: str):
        self._db_client = DBClient(uri)

    def get_all_reviews(self):
        query = (
            select(Review)
            .options(
                joinedload(Review.client).load_only(User.id, User.first_name, User.last_name)
            )
        )
        return self._get_all_reviews(query)

    def get_review_by_id(self, review_id: int):
        query = select(Review).where(Review.id == review_id)
        return self._get_one_review_by_query(query)
    
    def get_reviews_by_client_id(self, client_id):
        query = (
            select(Review)
            .options(
                joinedload(Review.client).load_only(User.id, User.first_name, User.last_name)
            )
            .where(Review.client_id == client_id)
        )
        return self._get_all_reviews(query)
    
    def get_reviews_by_consultant_id(self, consultant_id):
        query = (
            select(Review)
            .options(
                joinedload(Review.client).load_only(User.id, User.first_name, User.last_name)
            )
            .where(Review.consultant_id == consultant_id)
        )
        return self._get_all_reviews(query)

    def create_review(self, review: Review):
        return self._db_client.create_object(review)
    
    def patch_review(self, review_id: int, updated_review: dict[str, any]):
        # todo: check for unique fields ?
        # todo: is it a bug: DB records does not get updated when the same info passed several times?
        query = update(Review).where(Review.id == review_id).values(textOfReview=updated_review['textOfReview']).returning
        (
            Review.id, Review.textOfReview, Review.consultant_id, Review.client_id
        )
        return self._db_client.update_object(query)

    def delete_review(self, review: Review):
        return self._db_client.delete_object(review)
    
    def _get_one_review_by_query(self, query: Select):
        try:
            return self._db_client.select_one_object_by_query(query)

        except OperationalError as e:
            # NOTE: case for the "DBAPIError" when user id is not a valid UUID
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))

    def _get_all_reviews(self, query: Select):
        try:
            return self._db_client.select_all_objects(query)

        except OperationalError as e:
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))
