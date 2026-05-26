from __future__ import annotations
from fastapi import APIRouter, Depends
from redis import Redis

from auth_bearer import JWTBearer

from database.models import User
from daos.users_dao import UsersDAO

from settings import get_settings
from utils import decode_token

from deps import get_current_user
from serializers import serialize_user

db_uri = get_settings().db_uri

me_users_router = APIRouter(
    prefix="/users",
)

@me_users_router.get("/me", summary='Get details of currently logged in user')
async def get_me(user: User = Depends(get_current_user)):
    return serialize_user(user, include_reviews=True)


# @users_router.get("/users/me", summary='Get details of currently logged in user', dependencies=[Depends(JWTBearer())])
@me_users_router.get("/account/me", summary='Get details of logged in user by token')
async def get_me(token: str = Depends(JWTBearer())):
    users_dao = UsersDAO(uri=db_uri)
    auth_token = decode_token(token)
    # print(auth_token)
    email = str(auth_token.get('sub'))
    user = users_dao.get_user_by_email_with_reviews(email)
    # response = {"id": user[0].id, "first_name": user[0].first_name, "last_name": user[0].last_name, "email": user[0].email, "password": user[0].password}
    return serialize_user(user[0], include_reviews=True, include_password=True)
