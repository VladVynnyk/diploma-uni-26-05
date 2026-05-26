import random
import math
import os

import argon2
from argon2 import PasswordHasher

from datetime import datetime, timedelta
import time
from typing import Union, Any

from jose import jwt

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
# JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']   # should be kept secret


# JWT_SECRET_KEY = "lkhgiogbnkjbiupho9"
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "dbxvlgmMf67RZww45peIp7fZpZjzTqtX6AhrMpNLb4JMzdqgOE5S4VRxGAURnUK",
)

# should be kept secret
# JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']


# JWT_REFRESH_SECRET_KEY = "oiasdflkasdjfoiasdjf"

JWT_REFRESH_SECRET_KEY = os.getenv(
    "JWT_REFRESH_SECRET_KEY",
    "spkrXAH34sPs6fBjva6ym2cTHkDCz4xb5GnCnrIPgjrGiRQzn6dPYXPJ0h6ibdq",
)

ph = PasswordHasher(time_cost=16, memory_cost=2**15, parallelism=2, hash_len=32, salt_len=16)


def get_hashed_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    # return ph.verify(hash=hashed_pass, password=password)
    try:
        result = ph.verify(hash=hashed_pass, password=password)
        return result
    except argon2.exceptions.VerifyMismatchError:
        return False


# def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
#     if expires_delta is not None:
#         expires_delta = datetime.utcnow() + expires_delta
#     else:
#         expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

#     to_encode = {"exp": expires_delta, "sub": str(subject)}
#     encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
#     return encoded_jwt


# def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
#     if expires_delta is not None:
#         expires_delta = datetime.utcnow() + expires_delta
#     else:
#         expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

#     to_encode = {"exp": expires_delta, "sub": str(subject)}
#     encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
#     return encoded_jwt


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    expires_at = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    to_encode = {"exp": expires_at, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    expires_at = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    
    to_encode = {"exp": expires_at, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except:
        return {}



#-----------------------------send emails--------------------------------
import smtplib, ssl

port = 465  # For SSL
password = 'istckflqpbnbahou'

email_sender = "vladvynnyk1@gmail.com"
email_receiver = "vladik.vunnuk@gmail.com"
message = """\
Subject: Hi there

This message is sent from Python."""



# Function for sending emails to consultant
# def send_fucking_email(email_receiver: str, message: str):
#     context = ssl.create_default_context()
#     try: 
#         with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
#             server.login("vladvynnyk1@gmail.com", password)
#             server.sendmail("vladvynnyk1@gmail.com", email_receiver, message)
#     except:
#         print("Email is not valid!")

def send_fucking_email(email_receiver: str, subject: str, message: str, html: bool = False):
    context = ssl.create_default_context()
    
    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = email_sender
    msg["To"] = email_receiver
    msg["Subject"] = subject
    
    # Attach HTML or plain text
    if html:
        msg.attach(MIMEText(message, "html", "utf-8"))  # Send as HTML
    else:
        msg.attach(MIMEText(message, "plain", "utf-8"))  # Send as plain text

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(email_sender, password)
            server.sendmail(email_sender, email_receiver, msg.as_string())
        print("✅ Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"❌ Failed to send email: {e}")


#-----------------------------generate six-digit code--------------------------------
def generate_six_digit_code():
    ## storing strings in a list
    digits = [i for i in range(0, 10)]

    ## initializing a string
    random_str = ""

    ## we can generate any lenght of string we want
    for i in range(6):
    ## generating a random index
    ## if we multiply with 10 it will generate a number between 0 and 10 not including 10
    ## multiply the random.random() with length of your base list or str
        index = math.floor(random.random() * 10)

        random_str += str(digits[index])

    ## displaying the random string
    print(random_str)
    return random_str


def serialize_dict(attributes, exclude_fields=None):
    """
    Serialize the python dictionary by removing empty fields and excluding specified fields.
    Handles nested dictionaries recursively.

    Args:
        exclude_fields (list, optional): A list of field names to exclude from the output.

    Returns:
        dict: A dictionary of serialized attributes, excluding empty fields and specified fields.
    """
    if exclude_fields is None:
        exclude_fields = []

    serialized_data = {}

    for k, v in attributes.items():
        # Skip if the field is in the exclude_fields list
        if k in exclude_fields:
            continue

        if isinstance(v, dict):
            # Recursively serialize nested dictionaries
            nested_serialized = serialize_dict(v, exclude_fields=exclude_fields)
            if nested_serialized:  # Only add non-empty dictionaries
                serialized_data[k] = nested_serialized
        elif isinstance(v, list):
            # Handle lists by serializing each element if it's a dict
            serialized_list = []
            for item in v:
                if isinstance(item, dict):
                    serialized_item = serialize_dict(item, exclude_fields=exclude_fields)
                    if serialized_item:
                        serialized_list.append(serialized_item)
                else:
                    if item is not None and item != "" and item != {}:
                        serialized_list.append(item)

            if serialized_list:  # Only add non-empty lists
                serialized_data[k] = serialized_list
        else:
            # Skip if the value is empty, None, or a blank string
            if v is not None and v != "" and v != {}:
                serialized_data[k] = v

    return serialized_data


def object_to_dict(obj, include_private=False, include_callable=False):
    """
    Convert a class object into a dictionary.

    Args:
        obj: The class object to convert.
        include_private (bool): Whether to include private attributes (starting with `_`).
        include_callable (bool): Whether to include callable attributes (methods).

    Returns:
        dict: A dictionary representation of the object.
    """
    if not obj:
        return {}

    attributes = dir(obj)
    result = {}
    for attr in attributes:
        if not include_private and attr.startswith("_"):
            continue  # Skip private attributes

        value = getattr(obj, attr)

        if callable(value):
            if include_callable:
                result[attr] = value
            continue  # Skip callable attributes unless explicitly included

        result[attr] = value

    return result
