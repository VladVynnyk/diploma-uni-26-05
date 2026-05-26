from __future__ import annotations

from fastapi import APIRouter, Depends

from database.models import Tag
from pydantic_models import TagSchema
from daos.tags_dao import TagsDAO
from deps import require_admin

from settings import get_settings

db_uri = get_settings().db_uri

# db_uri='postgresql+psycopg2://postgres:1234@127.0.0.1:5432/consultingdb'

tags_router = APIRouter(
    prefix="/tags",
)

@tags_router.post("/", dependencies=[Depends(require_admin)])
def add_tag(tag_for_insert: TagSchema):
    print("_____________DB_URI___________: ", db_uri)
    Tag_for_insert = Tag(name=tag_for_insert.name, description=tag_for_insert.description)
    Tags_dao = TagsDAO(uri=db_uri)
    created_Tag = Tags_dao.create_Tag(Tag_for_insert)
    print("Tag: ", created_Tag)
    print("created_Tag", created_Tag)
    return created_Tag

@tags_router.get("/")
def get_tags():
    print("_____________DB_URI___________: ", db_uri)
    Tags_dao = TagsDAO(uri=db_uri)
    tags = Tags_dao.get_all_Tags()
    return tags

@tags_router.get("/{id}")
def get_tag(id: str) -> TagSchema:
    Tags_dao = TagsDAO(uri=db_uri)
    Tag = Tags_dao.get_tag_by_id(id)

    response = {"id": Tag[0].id, "name": Tag[0].name, "description": Tag[0].description}
    return response

@tags_router.patch("/{id}", dependencies=[Depends(require_admin)])
def update_tag(id: str, updated_Tag: TagSchema):
    Tags_dao = TagsDAO(uri=db_uri)
    Tag_to_update = Tags_dao.patch_Tag(id, updated_Tag.model_dump())
    return Tag_to_update

@tags_router.delete("/{id}", dependencies=[Depends(require_admin)])
def delete_tag(id: str):
    Tags_dao = TagsDAO(uri=db_uri)
    Tag_for_delete = Tags_dao.get_tag_by_id(id)
    print("tag for delete: ", Tag_for_delete[0])

    tag_to_delete = Tags_dao.delete_Tag(Tag_for_delete[0])
    response = {"id": Tag_for_delete[0].id, "name": Tag_for_delete[0].name, "description": Tag_for_delete[0].description}
    return response
