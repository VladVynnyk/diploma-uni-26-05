from __future__ import annotations
from fastapi import APIRouter

from daos.users_dao import UsersDAO

from settings import get_settings


db_uri = get_settings().db_uri

delete_users_router = APIRouter(
    prefix="/users",
)

@delete_users_router.delete("/{id}")
def delete_user(user_id: int):
    users_dao = UsersDAO(uri=db_uri)
    user_for_delete = users_dao.get_user_by_id(user_id)
    # print("user for delete: ", user_for_delete[0])

    deleted_user = users_dao.delete_user(user_for_delete[0])

    response = {"id": user_for_delete[0].id, "first_name": user_for_delete[0].first_name, "last_name": user_for_delete[0].last_name, "email": user_for_delete[0].email}
    return response

