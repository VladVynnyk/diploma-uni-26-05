from __future__ import annotations
import json
from fastapi import APIRouter, Query
from redis import Redis

from pydantic_models import UserSchema
from daos.users_dao import UsersDAO

from settings import get_settings
from utils import serialize_dict, object_to_dict

# It's connection for redis from localhost in docker
# r = Redis(host='localhost', port=6379, decode_responses=True)

#It's connection for redis from docker in docker
# r = Redis(host='redis', port=6379, decode_responses=True)


db_uri = get_settings().db_uri

redis_host = get_settings().redis_host
redis_port = get_settings().redis_port

r = Redis(host=redis_host, port=redis_port, decode_responses=True)

read_users_router = APIRouter(
    prefix="/users",
)

@read_users_router.get("/")
def get_users():
    # r = Redis(host='localhost', port=6379)
    # Here should be function for caching responses 
    
    # print("Cached value: ", r.delete("vladik.vunnuk@gmail.com"))
    # current_users = r.get("current_users")

    current_users = r.lrange('current_users', 0, -1)
    if current_users == []:
        print("None")
        users_dao = UsersDAO(uri=db_uri)
        # users = users_dao.get_users_with_tags()
        users = users_dao.get_consultant_users_with_reviews()
        for i, dictionary in enumerate(users):
            print("Iteration : ", i)
            serialized_tags = []
            for tags in dictionary.tags:
                tag = json.dumps({"id": tags.id.__str__(), "name": tags.name, "description": tags.description})
                serialized_tags.append(tag)
                print("serialized tags: ", serialized_tags)
            serialized_data = json.dumps({"id": dictionary.id.__str__(), "first_name": dictionary.first_name, "last_name": dictionary.last_name, "email": dictionary.email, "price": dictionary.price, "description":dictionary.description, "photo":dictionary.photo, "tags": serialized_tags, "rating": str(dictionary.rating)})
            r.rpush('current_users', serialized_data)
            r.expire('current_users', 60)
            serialized_tags.clear()
            
        return users
    else:
        print("not none")
        retrieved_data = r.lrange('current_users', 0, -1)
        retrieved_tuple_of_objects = []

        for obj in retrieved_data:
            data_dict = json.loads(obj)
            serialized_tags = []
            for tags in data_dict['tags']:
                t = json.loads(tags)
                tag = {"id": t['id'], "name": t['name'], "description": t['description']}
                serialized_tags.append(tag)
            serialized_data = json.dumps({"id": data_dict['id'], "first_name": data_dict['first_name'], "last_name": data_dict['last_name'], "email": data_dict['email'], "price": data_dict['price'], "description":data_dict['description'], "photo":data_dict['photo'], "tags": serialized_tags})
            retrieved_tuple_of_objects.append(serialized_data)

        response = []
        for item in retrieved_tuple_of_objects:
            tmp = json.loads(item)
            response.append(tmp)
        
        return response
    
    
@read_users_router.get("/paginated")
def get_users_paginated(page: int = Query(1, description="Page number, starting from 1"), 
                        page_size: int = Query(10, description="Number of records per page")):
    """
    Get users with pagination.
    """
    current_users_key = f"current_users_page_{page}_size_{page_size}"
    current_users = r.lrange(current_users_key, 0, -1)

    # if not current_users:
    users_dao = UsersDAO(uri=db_uri)
    amount_of_users = users_dao.get_consultant_users_count()
    users = users_dao.get_consultant_users_with_reviews_paginated(page=page, page_size=page_size)
    for user in users:
        serialized_tags = [
            json.dumps({"id": tag.id.__str__(), "name": tag.name, "description": tag.description}) 
            for tag in user.tags
        ]
        serialized_reviews = [
            {
                "description": review.description,
                "rating": review.rating,
                "client_id": review.client_id.__str__(),
                "id": review.id.__str__(),
                "created_at": review.created_at.isoformat(),
                "consultant_id": review.consultant_id.__str__(),
                "client": {
                    "id": review.client.id.__str__(),
                    "last_name": review.client.last_name,
                    "first_name": review.client.first_name,
                    "tags": [
                        {"id": tag.id.__str__(), "name": tag.name, "description": tag.description}
                        for tag in review.client.tags
                    ],
                },
            }
            for review in user.reviews_as_consultant
        ]
        serialized_data = json.dumps({
            "id": user.id.__str__(),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "price": user.price,
            "description": user.description,
            "photo": user.photo,
            "tags": serialized_tags,
            "rating": str(user.rating),
            "reviews_as_consultant": serialized_reviews,
        })
        r.rpush(current_users_key, serialized_data)
    r.expire(current_users_key, 60)  # Cache expiration in seconds
    return {
        "users": users,
        "total_count": amount_of_users,
        "page": page,
        "page_size": page_size
    }
    # else:
    #     users_dao = UsersDAO(uri=db_uri)
    #     total_count = users_dao.get_consultant_users_count()

    #     # Deserialize and return cached users
    #     users = [
    #         {
    #             **json.loads(user),  # Load the main user object
    #             "tags": [
    #                 json.loads(tag) for tag in json.loads(user)["tags"]  # Deserialize each tag
    #             ]
    #         }
    #         for user in current_users
    #     ]

    #     return {
    #         "users": users,
    #         "total_count": total_count,
    #         "page": page,
    #         "page_size": page_size
    #     }
        


@read_users_router.get("/offset")
def get_users_offset(offset: int = Query(0, description="Number of records to skip"),
                     limit: int = Query(10, description="Number of records to fetch")):
    """
    Get users with offset-based pagination.
    """
    current_users_key = f"current_users_offset_{offset}_limit_{limit}"
    current_users = r.lrange(current_users_key, 0, -1)

    if not current_users:
        users_dao = UsersDAO(uri=db_uri)
        users = users_dao.get_consultant_users_with_reviews_offset(offset=offset, limit=limit)
        for user in users:
            serialized_tags = [
                    json.dumps({"id": tag.id.__str__(), "name": tag.name, "description": tag.description}) 
                    for tag in user.tags
                ]
            serialized_reviews = [
                {
                    "description": review.description,
                    "rating": review.rating,
                    "client_id": review.client_id.__str__(),
                    "id": review.id.__str__(),
                    "created_at": review.created_at.isoformat(),
                    "consultant_id": review.consultant_id.__str__(),
                    "client": {
                        "id": review.client.id.__str__(),
                        "last_name": review.client.last_name,
                        "first_name": review.client.first_name,
                        "tags": [
                            {"id": tag.id.__str__(), "name": tag.name, "description": tag.description}
                            for tag in review.client.tags
                        ],
                    },
                }
                for review in user.reviews_as_consultant
            ]
            serialized_data = json.dumps({
                "id": user.id.__str__(),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "price": user.price,
                "description": user.description,
                "photo": user.photo,
                "tags": serialized_tags,
                "rating": str(user.rating),
                "reviews_as_consultant": serialized_reviews,
            })
            r.rpush(current_users_key, serialized_data)
        r.expire(current_users_key, 60)  # Cache expiration in seconds
        return users
    else:
        # Deserialize and return cached users
        return [
            {
                **json.loads(user),  # Load the main user object
                "tags": [
                    json.loads(tag) for tag in json.loads(user)["tags"]  # Deserialize each tag
                ]
            }
            for user in current_users
        ]


@read_users_router.get("/{id}")
def get_user(user_id: str):
    users_dao = UsersDAO(uri=db_uri)
    user = users_dao.get_user_by_id(user_id)
    response = {"id": user[0].id, "first_name": user[0].first_name, "last_name": user[0].last_name, "email": user[0].email, "password": user[0].password}
    return response


@read_users_router.get("/email/{email}")
def get_user_by_email(email: str):
    users_dao = UsersDAO(uri=db_uri)
    user = users_dao.get_user_by_email(email)
    response = {"id": user[0].id, "first_name": user[0].first_name, "last_name": user[0].last_name, "email": user[0].email, "password": user[0].password}
    return response


@read_users_router.get("/search/")
def get_users_by_name_or_surname(name: str):
    users_dao = UsersDAO(uri=db_uri)
    users = users_dao.get_all_users_by_name_or_surname(name)
    return users


# get users by tags
# logic of selecting users by tags:
# 1. tags[] = select * from tags where name == tag; (here we can select only id from tags. And in the next row we will do this:
#  tags_users[] = select * from tags_users where tags_users.tag_id == tags[i];)
# 2. tags_users[] = select * from tags_users where tags_users.tag_id == tags[i].id;
# 3. select * from users where users.id == tags_users[i].user_id; 
@read_users_router.get("/sort_by_tag/{tag}")
def get_users_by_tag(tag: str, page: int = Query(1, description="Page number, starting from 1"), 
                        page_size: int = Query(10, description="Number of records per page")):
    users_dao = UsersDAO(uri=db_uri)
    # users = users_dao.get_users_by_tag(tag)

    current_users_key = f"filtered_users_page_{page}_size_{page_size}"
    current_users = r.lrange(current_users_key, 0, -1)

    amount_of_users = users_dao.get_consultant_users_count()
    users = users_dao.get_consultant_users_with_reviews_by_tag_paginated(tag, page=page, page_size=page_size)
    for user in users:
        serialized_tags = [
            json.dumps({"id": tag.id.__str__(), "name": tag.name, "description": tag.description}) 
            for tag in user.tags
        ]
        serialized_reviews = [
            {
                "description": review.description,
                "rating": review.rating,
                "client_id": review.client_id.__str__(),
                "id": review.id.__str__(),
                "created_at": review.created_at.isoformat(),
                "consultant_id": review.consultant_id.__str__(),
                "client": {
                    "id": review.client.id.__str__(),
                    "last_name": review.client.last_name,
                    "first_name": review.client.first_name,
                    "tags": [
                        {"id": tag.id.__str__(), "name": tag.name, "description": tag.description}
                        for tag in review.client.tags
                    ],
                },
            }
            for review in user.reviews_as_consultant
        ]
        serialized_data = json.dumps({
            "id": user.id.__str__(),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "price": user.price,
            "description": user.description,
            "photo": user.photo,
            "tags": serialized_tags,
            "rating": str(user.rating),
            "reviews_as_consultant": serialized_reviews,
        })
        r.rpush(current_users_key, serialized_data)
    r.expire(current_users_key, 60)  # Cache expiration in seconds
    return {
        "users": users,
        "total_count": amount_of_users,
        "page": page,
        "page_size": page_size
    }

@read_users_router.get("/filter/", summary="Endpoint for filtering users by category, and price")
def filter_users(category: str, lower_price: int, higher_price: int):
    print("category: ", category)
    users_dao = UsersDAO(uri=db_uri)
    filtered_users = users_dao.filter_users_by_category_and_price(category=category, lower_price=lower_price, higher_price=higher_price)
    return filtered_users


@read_users_router.get("/filter-price/", summary="Endpoint for filtering users by price only")
def filter_users_by_price(lower_price: int, higher_price: int):
    users_dao = UsersDAO(uri=db_uri)
    filtered_users = users_dao.filter_users_by_price_only(lower_price=lower_price, higher_price=higher_price)
    return filtered_users
