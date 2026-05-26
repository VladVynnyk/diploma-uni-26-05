from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from redis import Redis

from jose import jwt, JWTError, ExpiredSignatureError
from datetime import timedelta

from database.models import User
from pydantic_models import UserSchemaRegister, EmailRequest, RecoveryPasswordCodeRequest, RecoveryPasswordPasswordRequest, RefreshTokenRequest, CompleteRegistrationSchema
from daos.users_dao import UsersDAO

from utils import get_hashed_password, verify_password, create_access_token, create_refresh_token
from utils import send_fucking_email, generate_six_digit_code
from utils import JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

from settings import get_settings


db_uri = get_settings().db_uri
redis_host = get_settings().redis_host
redis_port = get_settings().redis_port

r = Redis(host=redis_host, port=redis_port, decode_responses=True)

auth_router = APIRouter(
    prefix="/auth",
)
logger = logging.getLogger(__name__)

@auth_router.post("/signup", summary="Create new user")
async def create_user(data: UserSchemaRegister):
    # querying database to check if user already exist
    # user = User.get(data.email)
    logger.info("Signup attempt received for email=%s", data.email)

    users_dao = UsersDAO(uri=db_uri)
    user = users_dao.get_user_by_email(data.email)
    
    if user is not None:
        logger.warning("Signup rejected for duplicate email=%s", data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )

    user_to_create = User(
        email=data.email,
        password=get_hashed_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
    )
    created_user = users_dao.create_user(user_to_create)
    logger.info("Signup succeeded for email=%s user_id=%s", data.email, created_user.id)

    message = """\
        Шановний клієнте! Ви успішно створили акаунт!
        Просимо вас звернути увагу на те, що для того щоб користуватись нашим сервісом, вам потрібно створити крипто-гаманець, щоб оплачувати наші послуги криптовалютою USDT. 
        """.encode('utf-8')
    # send_fucking_email(data.email, message=message)

    return created_user


@auth_router.post("/complete-registration", summary="Complete registration for guest order user")
async def complete_registration(data: CompleteRegistrationSchema):
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Паролі не збігаються.",
        )

    users_dao = UsersDAO(uri=db_uri)
    user = users_dao.get_user_by_email(data.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача не знайдено.",
        )

    current_user = user[0]
    if current_user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач уже зареєстрований. Увійдіть у систему.",
        )

    hashed_password = get_hashed_password(data.password)
    users_dao.patch_password_of_user(current_user.id, hashed_password)

    return {
        "access_token": create_access_token(current_user.email),
        "refresh_token": create_refresh_token(current_user.email),
    }

@auth_router.post("/login", summary="Create access and refresh tokens for user")
async def login(form_data: OAuth2PasswordRequestForm = Depends()): 
    users_dao = UsersDAO(uri=db_uri)
    user = users_dao.get_user_by_email(form_data.username)

    if user is None:
        print("User is none")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    if user is not None: 
        hashed_pass = user[0].password
        if not verify_password(form_data.password, hashed_pass):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password"
            )
        return {
            "access_token": create_access_token(user[0].email),
            "refresh_token": create_refresh_token(user[0].email),
        }
    
@auth_router.post("/refresh-token")
async def refresh_token(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(request.refresh_token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token (missing user ID)")

        # 🔹 Generate new tokens
        new_access_token = create_access_token(user_id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        new_refresh_token = create_refresh_token(user_id, timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))

        return {"access_token": new_access_token, "refresh_token": new_refresh_token}
    
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid refresh token (decode failed)")
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


#------------------ this is routes for recovering password -------------------------------
@auth_router.patch("/recovery/send-code", summary="Send code for recover password")
async def send_code_to_email(data: EmailRequest):
    print("DATA: ", data)
    random_six_digit_code = generate_six_digit_code()
    # send email     
    subject = "🔒 Код підтвердження для відновлення паролю"

    message = f"""\
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #2C3E50;">КОД ПІДТВЕРДЖЕННЯ</h2>
            <p>Ваш код підтвердження для відновлення паролю:</p>
            <h1 style="color: #E74C3C; font-size: 24px;">{random_six_digit_code}</h1>
            <p><strong>Увага! Код діє тільки 5 хвилин!</strong></p>
        </body>
    </html>
    """.encode('utf-8')
    send_fucking_email(data.email, subject=subject, message=message, html=True)

    # r.set(data.email, random_six_digit_code)
    r.setex(data.email, 300, random_six_digit_code)  
    print("Cached value: ", r.get('foo'))

    return {"message", "Code was sent successfully"}

@auth_router.patch("/recovery/check-code", summary="Check code for recovering password")
async def check_code(data: RecoveryPasswordCodeRequest):
    generated_code = r.get(data.email)
    if generated_code == data.code:
        r.delete(data.email)
        return {"message", "Success"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code is not corect"
        )

@auth_router.patch("/recovery/password", summary="Recover password")
async def recover_password(data: RecoveryPasswordPasswordRequest):
    users_dao = UsersDAO(uri=db_uri)
    user = users_dao.get_user_by_email(data.email)
    hashed_password = get_hashed_password(data.password)
    updated_password = users_dao.patch_password_of_user(user[0].id, hashed_password)
    print(user[0].id)
    print(updated_password)
    print(verify_password(data.password, hashed_password))
    return "Object updated"
