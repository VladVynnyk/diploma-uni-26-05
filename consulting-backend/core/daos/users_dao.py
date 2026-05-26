from __future__ import annotations

import logging

from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert

from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import OperationalError
from sqlalchemy import func

from sqlalchemy.orm import defer, joinedload, subqueryload

from clients.DBClient import DBClient
from database.models import User, Review, Tag, association_table

logger = logging.getLogger(__name__)


class UsersDAO:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, uri: str):
        self._db_client = DBClient(uri)

    def get_user_by_id(self, user_id: int):
        query = select(User).where(User.id == user_id)
        return self._get_one_user_by_query(query)

    def get_user_by_email(self, user_email: str):
        query = select(User).where(User.email == user_email)
        return self._get_one_user_by_query(query)
    
    def get_user_by_email_with_reviews(self, user_email: str):
        # query = select(User).where(User.email == user_email).options(joinedload(User.reviews_as_consultant), defer(User.password))
        query = select(User).where(User.email == user_email).options(joinedload(User.reviews_as_consultant))
        return self._get_one_user_by_query(query)
    
    # def get_user_for_operation(self, user_id: int):
    #     query = select(user).where(user.id == user_id)
    #     return self._db_user.select_one_object_for_operation(query)

    def get_all_users(self):
        query = select(User)
        return self._get_all_users(query)

    def get_all_users_for_admin(self):
        query = (
            select(User)
            .options(
                joinedload(User.tags),
                joinedload(User.reviews_as_consultant)
            )
            .order_by(User.created_at.desc())
        )
        return self._get_all_users(query)
    
    def get_all_users_by_name_or_surname(self, name: str):
        # TODO: improve/optimize this method
        # TODO: we should select users only with is_consultant=True
        query = select(User).filter(func.lower(User.first_name).ilike(f"{name}%"))
        second_query = select(User).filter(func.lower(User.last_name).ilike(f"{name}%"))

        users = self._get_all_users(query)
        if len(users) == 0:
            differ_users = self._get_all_users(second_query)
            return differ_users
        return users
    
    def filter_users_by_price_only(self, lower_price: int, higher_price: int):
        query = select(User).join(association_table).join(Tag).filter((User.price<=higher_price)).filter((User.price>=lower_price))
        return self._get_all_users(query)
    
    def filter_consultants_by_category_only(self, lower_price: int, higher_price: int):
        query = select(User).join(association_table).join(Tag).filter((User.price<=higher_price)).filter((User.price>=lower_price))
        return self._get_all_consultants(query)

    def filter_consultants_by_category_and_price(self, category: str, lower_price: int, higher_price: int):
        query = select(User).join(association_table).join(Tag).filter((Tag.name == category)).filter((User.price<=higher_price)).filter((User.price>=lower_price))
        return self._get_all_users(query)
    
    def get_users_by_tag(self, tag: str):
        query = select(User).join(association_table).join(Tag).filter((Tag.name == tag))
        return self._get_all_users(query)
    
    # This is bullshit, because I don't know the difference
    # Between get_users_by_tag, and get_users_with_tags
    def get_users_with_tags(self):
        # This query returns all data with password
        query = select(User)
        # This query exludes password from query
        newQuery = query.options(defer(User.password))
        return self._get_all_users(newQuery) 
    
    def get_consultant_users_with_reviews(self):
        # query = select(User).options(joinedload(User.reviews_as_consultant), defer(User.password)).filter(User.is_consultant==True)

        query = (
                select(User)
                .options(
                    joinedload(User.reviews_as_consultant).joinedload(Review.client).load_only(User.first_name, User.last_name),
                    defer(User.password)
                )
                .filter(User.is_consultant == True)
            )
        return self._get_all_users(query)
    

    def get_consultant_users_with_reviews_paginated(self, page: int, page_size: int):
        query = (
            select(User)
            .options(
                subqueryload(User.reviews_as_consultant)
                .joinedload(Review.client)
                .load_only(User.first_name, User.last_name),
                defer(User.password)
            )
            .filter(User.is_consultant == True)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        return self._get_all_users(query)


    def get_consultant_users_with_reviews_by_tag_paginated(self, tag: str, page: int, page_size: int):
        query = select(User).join(association_table).join(Tag).filter((Tag.name == tag))
        query = (
            select(User).join(association_table).join(Tag).filter((Tag.name == tag))
            .options(
                subqueryload(User.reviews_as_consultant)
                .joinedload(Review.client)
                .load_only(User.first_name, User.last_name),
                defer(User.password)
            )
            .filter(User.is_consultant == True)
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        return self._get_all_users(query)


    def get_consultant_users_with_reviews_offset(self, offset: int, limit: int):
        query = (
            select(User)
            .options(
                subqueryload(User.reviews_as_consultant)
                .joinedload(Review.client)
                .load_only(User.first_name, User.last_name),
                defer(User.password)
            )
            .filter(User.is_consultant == True)
            .limit(limit)
            .offset(offset)
        )
        return self._get_all_users(query)
    
    def get_consultant_users_count(self):
        """
        Get the total number of consultant users.
        """
        query = select(func.count(User.id)).filter(User.is_consultant == True)
        result = self._db_client.select_number_of_rows_by_query(query)
        return result

    def create_user(self, user: User):
        return self._db_client.create_object(user)

    def patch_user(self, user_id: str, updated_user: dict[str, any]):
        # todo: check for unique fields ?
        # todo: is it a bug: DB records does not get updated when the same info passed several times?
        query = update(User).where(User.id == user_id).values(first_name=updated_user['first_name'], last_name=updated_user['last_name'], 
                                                              email=updated_user['email'], phone_number=updated_user['phone_number'],
                                                              photo=updated_user['photo'], description=updated_user['description'], price=updated_user['price'],
                                                              is_consultant=updated_user['is_consultant'],
                                                              #password=updated_user['password'],
                                                              ).returning(User.id, User.first_name, User.last_name, User.email)
        return self._db_client.update_object(query)
    
    def patch_user_with_tags(self, user_id: str, updated_user: dict[str, any]):
        # Update scalar fields using the update_object method
        query = (
            update(User)
            .where(User.id == user_id)
            .values(
                first_name=updated_user.get('first_name'),
                last_name=updated_user.get('last_name'),
                email=updated_user.get('email'),
                phone_number=updated_user.get('phone_number'),
                photo=updated_user.get('photo'),
                description=updated_user.get('description'),
                price=updated_user.get('price'),
                is_consultant=updated_user.get('is_consultant'),
            )
            .returning(User.id, User.first_name, User.last_name, User.email)
        )

        update_result = self._db_client.update_object(query)
        
        # If no rows were updated, return None (user might not exist)
        if not update_result:
            return None

        # Prepare tag update query
        if 'tags' in updated_user:
            tag_updates = updated_user['tags']  # Expecting a list of tag dictionaries

            delete_tags_query = (
                delete(association_table)
                .where(association_table.c.user_id == user_id)
            )
            self._db_client.update_object(delete_tags_query)

            for tag_data in tag_updates:
                tag_name = tag_data.get("name")
                tag_description = tag_data.get("description", "")

                # Upsert tag into Tag table
                insert_tag_query = insert(Tag).values(
                    name=tag_name,
                    description=tag_description
                ).on_conflict_do_nothing()
                self._db_client.update_object(insert_tag_query)

                # Insert association
                add_user_tag_query = insert(association_table).values(
                    tag_id=select(Tag.id).where(Tag.name == tag_name).scalar_subquery(),
                    user_id=user_id
                )
                self._db_client.update_object(add_user_tag_query)

        return {
            "id": user_id,
            "first_name": updated_user.get("first_name"),
            "last_name": updated_user.get("last_name"),
            "email": updated_user.get("email"),
            "tags": updated_user.get("tags", [])
        }

    def patch_password_of_user(self, user_id: str, updated_value: str):
        query = update(User).where(User.id == user_id).values(password=updated_value)
        return self._db_client.update_object(query)
    
    #-----------------------------------------------
    def patch_name_of_user(self, user_id: str, updated_value: str):
        query = update(User).where(User.id == user_id).values(first_name=updated_value)
        return self._db_client.update_object(query)

    def patch_surname_of_user(self, user_id: str, updated_value: str):
        query = update(User).where(User.id == user_id).values(last_name=updated_value)
        return self._db_client.update_object(query)
    
    def patch_description_of_user(self, user_id: str, updated_value: str):
        query = update(User).where(User.id == user_id).values(description=updated_value)
        return self._db_client.update_object(query)
    
    def patch_price_of_user(self, user_id: str, updated_value: int):
        query = update(User).where(User.id == user_id).values(price=updated_value)
        return self._db_client.update_object(query)

    def patch_admin_status_of_user(self, user_id: str, is_admin: bool):
        query = update(User).where(User.id == user_id).values(is_admin=is_admin)
        return self._db_client.update_object(query)
    
    def patch_tags_of_user(self, user_id: str, updated_value: list):
        query = update(User).where(User.id == user_id).values(tags=updated_value)
        return self._db_client.update_object(query)
    
    def patch_photo_of_user(self, user_id: str, updated_value: str):
        query = update(User).where(User.id == user_id).values(photo=updated_value)
        return self._db_client.update_object(query)
    #-----------------------------------------------

    def delete_user(self, user: User):
        return self._db_client.delete_object(user)

    def _get_one_user_by_query(self, query: Select):
        try:
            return self._db_client.select_one_object_by_query(query)

        except OperationalError as e:
            # NOTE: case for the "DBAPIError" when user id is not a valid UUID
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))

    def _get_all_users(self, query: Select):
        try:
            return self._db_client.select_all_objects(query)

        except OperationalError as e:
            logger.error(e.code)
            print(e)
            raise OperationalError("Operational error: ", str(e), str(e.orig))
        
