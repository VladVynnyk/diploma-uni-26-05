from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Union

class ClientSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class TagSchema(BaseModel):
    name: str
    description: str

class ConsultantSchema(BaseModel):
    first_name: str
    last_name: str
    tags: list[TagSchema]
    phone_number: str
    photo: str
    description: str
    price: str
    email: str
    password: str

class UserSchema(BaseModel):
    first_name: str
    last_name: str
    tags: list[TagSchema]
    phone_number: str
    photo: str
    description: str
    price: str
    email: str
    # password: str
    is_consultant: bool
    is_admin: bool = False

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Phone number is required.")
        return value.strip()

class RegisterUserSchema(BaseModel):
    first_name: str
    last_name: str
    tags: list[TagSchema]
    phone_number: str
    photo: str
    description: str
    price: str
    email: str
    password: str
    is_consultant: bool
    is_admin: bool = False

class FilterConsultantSchema(BaseModel):
    category: str
    lower_price_limit: int
    higher_price_limit: int

class ConsultationBaseSchema(BaseModel):
    consultant_id: str
    price: int
    topic: str = Field(min_length=1, max_length=255)
    message: str = ""
    scheduled_at: datetime | None = None
    duration_minutes: int = Field(default=60, ge=1, le=1440)


class RegisteredUserSchema(ConsultationBaseSchema):
    consultant_id: str
    client_id: str


class UnregisteredUserSchema(ConsultationBaseSchema):
    first_name: str
    last_name: str
    phone_number: str
    email: str

class ConsultationSchema(BaseModel):
    consultation: Union[RegisteredUserSchema, UnregisteredUserSchema]


class OrderStatusUpdateSchema(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().lower()
        allowed = {"new", "confirmed", "in_progress", "completed", "cancelled"}
        if normalized not in allowed:
            raise ValueError("Unsupported consultation status.")
        return normalized


class UserAdminStatusUpdateSchema(BaseModel):
    is_admin: bool

class ReviewSchema(BaseModel):
    description: str
    consultant_id: str
    client_id: str
    rating: int
    

class UserSchemaRegister(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_registration_password(cls, value: str) -> str:
        password = value.strip()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(char.isalpha() for char in password) or not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one letter and one number.")
        return password


class CompleteRegistrationSchema(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        password = value.strip()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(char.isalpha() for char in password) or not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one letter and one number.")
        return password

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, value: str) -> str:
        return value.strip()

class EmailRequest(BaseModel):
    email: str

class RecoveryPasswordCodeRequest(BaseModel):
    email: str
    code: str

class RecoveryPasswordPasswordRequest(BaseModel):
    email: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None

class SystemUser(BaseModel):
    password: str


class PaymentSchema(BaseModel):
    price: int
    consultation_id: int


class Request(BaseModel):
    server_callback_url: str
    order_id: str
    merchant_id: int
    order_desc: str
    amount: int
    currency: str
    signature: str


class PaymentBody(BaseModel):
    request: Request


class CardPaymentType(BaseModel):
    rrn: str
    masked_card: str
    sender_cell_phone: str | None
    response_signature_string: str
    response_status: str
    sender_account: str | None
    fee: str | None
    rectoken_lifetime: str | None
    reversal_amount: str
    settlement_amount: str
    actual_amount: str
    order_status: str
    response_description: str | None
    verification_status: str | None
    order_time: str | None
    actual_currency: str
    order_id: str | None
    parent_order_id: str | None
    merchant_data: str
    tran_type: str
    eci: str | None
    settlement_date: str | None
    payment_system: str
    rectoken: str | None
    approval_code: str
    merchant_id: int
    settlement_currency: str | None
    payment_id: int
    product_id: str | None
    currency: str
    card_bin: int
    response_code: str | None
    card_type: str
    amount: int
    sender_email: str
    signature: str
