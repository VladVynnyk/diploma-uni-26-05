from __future__ import annotations
from fastapi import APIRouter

from database.models import User, Tag
from pydantic_models import RegisterUserSchema
from daos.users_dao import UsersDAO

from settings import get_settings


db_uri = get_settings().db_uri

create_users_router = APIRouter(
    prefix="/users",
)

@create_users_router.post("/")
def add_user(user: RegisterUserSchema):
    user_for_insert = User(first_name=user.first_name, last_name=user.last_name, email=user.email, password=user.password, 
            phone_number=user.phone_number, photo=user.photo, description=user.description)

    for tag in user.tags:
        new_tag = Tag(name=tag.name, description=tag.description)
        user_for_insert.tags.append(new_tag)
    
    users_dao = UsersDAO(uri=db_uri)
    created_user = users_dao.create_user(user_for_insert)
    return created_user
