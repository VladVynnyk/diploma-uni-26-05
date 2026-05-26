from __future__ import annotations
from fastapi import APIRouter, Depends

from database.models import Review
from pydantic_models import ReviewSchema
from daos.reviews_dao import ReviewsDAO
from deps import require_admin
from serializers import serialize_review

from settings import get_settings


db_uri = get_settings().db_uri

reviews_router = APIRouter(
    prefix="/reviews",
)

@reviews_router.post("/")
def add_review(review: ReviewSchema):
    review_for_insert = Review(description=review.description, client_id=review.client_id, consultant_id=review.consultant_id, rating=review.rating)
    print("review: ", review)
    reviews_dao = ReviewsDAO(uri=db_uri)
    created_review = reviews_dao.create_review(review_for_insert)
    return created_review

@reviews_router.get("/")
def get_reviews():
    reviews_dao = ReviewsDAO(uri=db_uri)
    reviews = reviews_dao.get_all_reviews()
    return [serialize_review(review) for review in reviews]

@reviews_router.get("/{id}")
def get_review(id: str):
    reviews_dao = ReviewsDAO(uri=db_uri)
    review = reviews_dao.get_review_by_id(id)
    response = {"id": review[0].id, "text_of_review": review[0].description, "consultant_id": review[0].consultant_id, "client_id": review[0].client_id}
    return response

@reviews_router.get("/client/{client_id}", summary="Get reviews for single client")
def get_reviews(client_id: str):
    reviews_dao = ReviewsDAO(uri=db_uri)
    reviews = reviews_dao.get_reviews_by_client_id(client_id)
    return [serialize_review(review) for review in reviews]

@reviews_router.get("/consultant/{consultant_id}", summary="Get reviews for consultant")
def get_reviews(consultant_id: str):
    reviews_dao = ReviewsDAO(uri=db_uri)
    reviews = reviews_dao.get_reviews_by_consultant_id(consultant_id)
    return [serialize_review(review) for review in reviews]

@reviews_router.patch("/{id}", dependencies=[Depends(require_admin)])
def update_review(id: str, updated_review: ReviewSchema):
    reviews_dao = ReviewsDAO(uri=db_uri)
    review_to_update = reviews_dao.patch_review(id, updated_review.model_dump())
    return review_to_update

@reviews_router.delete("/{id}", dependencies=[Depends(require_admin)])
def delete_review(id: str):
    reviews_dao = ReviewsDAO(uri=db_uri)
    review_to_delete = reviews_dao.get_review_by_id(id)

    deleted_review = reviews_dao.delete_review(review_to_delete[0])

    response = {"id": deleted_review.id, "description": deleted_review.description,
                "client_id": deleted_review.client_id, "consultant_id": deleted_review.consultant_id}
    return response
