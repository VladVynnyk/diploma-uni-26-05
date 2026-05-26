from __future__ import annotations

from database.models import Order, Review, Tag, User


def _serialize_tag(tag: Tag):
    return {
        "id": str(tag.id),
        "name": tag.name,
        "description": tag.description,
    }


def serialize_review(review: Review):
    client = review.__dict__.get("client")
    return {
        "id": str(review.id),
        "description": review.description,
        "rating": review.rating,
        "created_at": review.created_at.isoformat() if review.created_at else None,
        "client_id": str(review.client_id),
        "consultant_id": str(review.consultant_id),
        "client": serialize_user(client, include_tags=False) if client else None,
    }


def serialize_user(
    user: User,
    include_reviews: bool = False,
    include_password: bool = False,
    include_tags: bool = True,
):
    state = user.__dict__
    data = {
        "id": str(state.get("id", user.id)),
        "first_name": state.get("first_name"),
        "last_name": state.get("last_name"),
        "phone_number": state.get("phone_number"),
        "email": state.get("email"),
        "photo": state.get("photo"),
        "description": state.get("description"),
        "price": state.get("price"),
        "created_at": state.get("created_at").isoformat() if state.get("created_at") else None,
        "is_consultant": state.get("is_consultant", False),
        "is_admin": state.get("is_admin", False),
        "rating": float(state.get("rating", 0) or 0),
    }
    if include_tags:
        data["tags"] = [_serialize_tag(tag) for tag in state.get("tags", [])]
    if include_password:
        data["password"] = state.get("password")
    if include_reviews:
        data["reviews_as_consultant"] = [serialize_review(review) for review in state.get("reviews_as_consultant", [])]
    return data


def _can_view_client_contacts(order: Order, viewer: User | None) -> bool:
    if viewer is None:
        return False
    if getattr(viewer, "is_admin", False):
        return True
    return str(order.consultant_id) == str(viewer.id)


def serialize_order(order: Order, viewer: User | None = None):
    client = order.__dict__.get("client")
    consultant = order.__dict__.get("consultant")
    client_payload = serialize_user(client, include_tags=False) if client else None
    consultant_payload = serialize_user(consultant, include_tags=False) if consultant else None

    if client_payload and not _can_view_client_contacts(order, viewer):
        client_payload.pop("email", None)
        client_payload.pop("phone_number", None)

    return {
        "id": str(order.id),
        "price": order.price,
        "status": order.status,
        "topic": order.topic,
        "message": order.message,
        "scheduled_at": order.scheduled_at.isoformat() if order.scheduled_at else None,
        "duration_minutes": order.duration_minutes,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "client_id": str(order.client_id),
        "consultant_id": str(order.consultant_id),
        "client": client_payload,
        "consultant": consultant_payload,
    }
