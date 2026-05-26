from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from clients.DBClient import DBClient
from daos.orders_dao import OrdersDAO
from daos.reviews_dao import ReviewsDAO
from daos.tags_dao import TagsDAO
from daos.users_dao import UsersDAO
from database.models import Review, Tag, User
from deps import get_current_user, require_admin
from pydantic_models import OrderStatusUpdateSchema, UserAdminStatusUpdateSchema
from serializers import serialize_order, serialize_review, serialize_user
from settings import get_settings


db_uri = get_settings().db_uri

admin_router = APIRouter()

STATUS_TRANSITIONS = {
    "new": {"confirmed", "cancelled"},
    "confirmed": {"in_progress", "cancelled"},
    "in_progress": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


@admin_router.get("/users/admin/all", dependencies=[Depends(require_admin)])
def get_all_users_for_admin():
    users_dao = UsersDAO(uri=db_uri)
    return [serialize_user(user) for user in users_dao.get_all_users_for_admin()]


@admin_router.patch("/users/{user_id}/admin-status", dependencies=[Depends(require_admin)])
def update_user_admin_status(
    user_id: str,
    payload: UserAdminStatusUpdateSchema,
    current_user: User = Depends(get_current_user),
):
    if str(current_user.id) == user_id and not payload.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove your own admin access.",
        )

    users_dao = UsersDAO(uri=db_uri)
    user = users_dao.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    users_dao.patch_admin_status_of_user(user_id, payload.is_admin)
    updated_user = users_dao.get_user_by_id(user_id)
    return serialize_user(updated_user[0])


@admin_router.get("/orders/admin/all", dependencies=[Depends(require_admin)])
def get_all_orders_for_admin(current_user: User = Depends(get_current_user)):
    orders_dao = OrdersDAO(uri=db_uri)
    return [serialize_order(order, viewer=current_user) for order in orders_dao.get_all_consultations_for_admin()]


@admin_router.patch("/orders/{order_id}/status")
def update_order_status(
    order_id: str,
    payload: OrderStatusUpdateSchema,
    current_user: User = Depends(get_current_user),
):
    normalized_status = payload.status

    orders_dao = OrdersDAO(uri=db_uri)
    order = orders_dao.get_consultation_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    consultation = order[0]
    is_admin = current_user.is_admin
    is_consultant = str(consultation.consultant_id) == str(current_user.id)
    if not is_admin and not is_consultant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot change the status of this consultation.",
        )

    current_status = consultation.status
    if normalized_status == current_status:
        updated_order = orders_dao.get_consultation_by_id(order_id)
        return serialize_order(updated_order[0], viewer=current_user)

    allowed_next_statuses = STATUS_TRANSITIONS.get(current_status, set())
    if normalized_status not in allowed_next_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status cannot be changed from '{current_status}' to '{normalized_status}'.",
        )

    orders_dao.change_status_of_consultation(order_id, normalized_status)
    updated_order = orders_dao.get_consultation_by_id(order_id)
    return serialize_order(updated_order[0], viewer=current_user)


@admin_router.get("/reviews/admin/all", dependencies=[Depends(require_admin)])
def get_all_reviews_for_admin():
    reviews_dao = ReviewsDAO(uri=db_uri)
    return [serialize_review(review) for review in reviews_dao.get_all_reviews()]


@admin_router.get("/dashboard/admin/stats", dependencies=[Depends(require_admin)])
def get_admin_stats():
    users_dao = UsersDAO(uri=db_uri)
    reviews_dao = ReviewsDAO(uri=db_uri)
    tags_dao = TagsDAO(uri=db_uri)
    orders_dao = OrdersDAO(uri=db_uri)
    db_client = DBClient(db_uri)

    total_users = db_client.select_number_of_rows_by_query(select(func.count(User.id))) or 0
    total_consultants = db_client.select_number_of_rows_by_query(
        select(func.count(User.id)).where(User.is_consultant == True)
    ) or 0
    total_reviews = db_client.select_number_of_rows_by_query(select(func.count(Review.id))) or 0
    total_tags = db_client.select_number_of_rows_by_query(select(func.count(Tag.id))) or 0
    average_rating = db_client.select_number_of_rows_by_query(select(func.coalesce(func.avg(Review.rating), 0))) or 0

    order_stats = orders_dao.get_orders_stats()
    return {
        "total_users": total_users,
        "total_consultants": total_consultants,
        "total_clients": max(total_users - total_consultants, 0),
        "total_orders": order_stats["total_orders"],
        "new_orders": order_stats["new_orders"],
        "confirmed_orders": order_stats["confirmed_orders"],
        "in_progress_orders": order_stats["in_progress_orders"],
        "completed_orders": order_stats["completed_orders"],
        "cancelled_orders": order_stats["cancelled_orders"],
        "total_reviews": total_reviews,
        "average_rating": float(average_rating),
        "total_tags": total_tags,
    }
