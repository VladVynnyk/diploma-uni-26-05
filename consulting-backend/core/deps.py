from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils import (
    ALGORITHM,
    JWT_SECRET_KEY
)

from jose import jwt
from pydantic import ValidationError
from pydantic_models import TokenPayload
from daos.users_dao import UsersDAO

from settings import get_settings


db_uri = get_settings().db_uri


reusable_oauth_for_user = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="JWT"
)

async def get_current_user(token: str = Depends(reusable_oauth_for_user)):
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # print("Token data", token_data)
    # user: Union[dict[str, Any], None] = User.get(
    #     User.email == token_data.sub)

    users_dao = UsersDAO(uri=db_uri)
    user = users_dao.get_user_by_email(token_data.sub)

    
    # create client_dao and consultant_dao 
    # client/consultant_dao.get_client/consultant_by_email(token_data.sub)
    # if client/consultant is None:
    # raise HttpException
    # return client/consultant

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_BAD_REQUEST,
            detail="Could not find user"
        )

    return user[0]


async def require_admin(user=Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access is required."
        )
    return user
