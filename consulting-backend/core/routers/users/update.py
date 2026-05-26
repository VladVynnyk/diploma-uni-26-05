from __future__ import annotations
from fastapi import APIRouter, HTTPException, UploadFile, status

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse

import boto3
from botocore.exceptions import NoCredentialsError
import tempfile

from pathlib import Path

from database.models import User, Tag
from pydantic_models import UserSchema
from daos.users_dao import UsersDAO


from settings import get_settings

settings = get_settings()
db_uri = settings.db_uri
aws_access_secret_id = settings.aws_access_key_id
aws_secret_access_key = settings.aws_secret_access_key
aws_region = settings.aws_region
avatars_bucket_name = settings.avatars_bucket_name
avatars_base_url = settings.avatars_base_url

update_users_router = APIRouter(
    prefix="/users",
)

@update_users_router.patch("/update/{user_id}")
def update_user(user_id: str, updated_user: UserSchema):
    print(updated_user.model_dump())
    if not updated_user.phone_number.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is required.",
        )
    users_dao = UsersDAO(uri=db_uri)
    updated_payload = updated_user.model_dump(exclude={"is_admin"})
    user_to_update = users_dao.patch_user_with_tags(str(user_id), updated_payload)
    return user_to_update

@update_users_router.patch("/change/email", summary="Change email of account (not important)")
async def change_email(user_id: str, user_email: str):
    pass

@update_users_router.patch("/change/photo", summary="Add or change photo of user")
async def change_photo(user_id: str, photo: UploadFile):
    try:
        # Create a temporary file to save the uploaded data
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, "wb") as temp_file:
            temp_file.write(photo.file.read())

        # Configure AWS S3 client
        client_kwargs = {"region_name": aws_region}
        if aws_access_secret_id and aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = aws_access_secret_id
            client_kwargs["aws_secret_access_key"] = aws_secret_access_key
        s3 = boto3.client("s3", **client_kwargs)

        # Define your S3 bucket name and the key (object name) for the uploaded file
        bucket_name = avatars_bucket_name or 'avatar-bucket-main'
        s3_object_key = f"avatars/{photo.filename}"

        users_dao = UsersDAO(uri=db_uri)
        current_user = users_dao.get_user_by_id(user_id)
        url_of_old_photo = current_user[0].photo
        parsed_url = urlparse(url_of_old_photo)
        old_object_key = parsed_url.path.lstrip("/")

        if old_object_key:
            s3.delete_object(Bucket=bucket_name, Key=old_object_key)

        # Upload the file to S3
        s3.upload_file(temp_file.name, bucket_name, s3_object_key, ExtraArgs={
                "ContentType": photo.content_type  # Set the content type from the uploaded file
            })
        print("content type ", photo.content_type)

        # Clean up the temporary file
        Path(temp_file.name).unlink()

        if avatars_base_url:
            link = f"{avatars_base_url.rstrip('/')}/avatars/{photo.filename}"
        else:
            link = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/avatars/{photo.filename}"
    
        user = users_dao.patch_photo_of_user(user_id, link)

        return {"message": "Photo uploaded successfully"}
    except NoCredentialsError:
        return {"error": "AWS credentials not found. Ensure your credentials are configured correctly."}

@update_users_router.patch("/change/name", summary="Add or change name of user")
async def change_name(user_id: str, name: str):
    users_dao = UsersDAO(uri=db_uri)
    user = users_dao.patch_name_of_user(user_id, name)
    return "Object updated"


@update_users_router.patch("/change/surname", summary="Add or change surname of user")
async def change_surname(user_id: str, surname: str):
    users_dao = UsersDAO(uri=db_uri)
    user = users_dao.patch_surname_of_user(user_id, surname)
    return "Object updated"

@update_users_router.patch("/change/description", summary="Add or change surname of user")
async def change_description(user_id: str, description: str):
    users_dao = UsersDAO(uri=db_uri)
    user = users_dao.patch_description_of_user(user_id, description)
    return "Object updated"

@update_users_router.patch("/change/price", summary="Add or change price of hour of consultation")
async def change_price(user_id: str, price: int):
    users_dao = UsersDAO(uri=db_uri)
    user = users_dao.patch_price_of_user(user_id, price)
    return "Object updated"

@update_users_router.patch("/add/tags", summary="In tags list should be names of tags, they can be not exist in db")
def add_tags_to_user(user_id: str, tags: list[str]): # tags - it's a names of tags
    engine = create_engine(db_uri)  # Use your database URL
    Session = sessionmaker(bind=engine)
    session = Session()
    tags_array = []
    for tag in tags: 
        # This code if tags with TagSchema
        # new_tag = Tag(name=tag.name, description=tag.description)
        new_tag = Tag(name=tag, description="") # Here also we can check, if tag in table exists
        tags_array.append(new_tag)
    current_user = session.query(User).get(user_id)
    print(current_user)
    for tag in tags_array: 
        current_user.tags.append(tag)
        session.commit()
    return "Object updated"


@update_users_router.patch("/remove/tags")
def remove_tags_from_user(user_id: str, tag_ids: list[str]):
    engine = create_engine(db_uri)  # Use your database URL
    Session = sessionmaker(bind=engine)
    session = Session()
    tags_array = []
    current_user = session.query(User).get(user_id)
    for tag in tag_ids:
        current_tag = session.query(Tag).get(tag) 
        # new_tag = Tag(name=tag.name, description=tag.description)
        # tags_array.append(new_tag)
        current_user.tags.remove(current_tag)
        session.commit()
    return "Object updated"

