from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.users.create import create_users_router
from routers.users.read import read_users_router
from routers.users.update import update_users_router
from routers.users.delete import delete_users_router
from routers.users.me import me_users_router 

from routers.users.auth import auth_router

from routers.admin_router import admin_router
from routers.orders_router import orders_router
from routers.tags_router import tags_router
from routers.reviews_router import reviews_router
from routers.payments_router import payments_router


origins = ["*", "localhost:3000","https://consulting-frontend-production.vercel.app"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(create_users_router)
app.include_router(read_users_router)
app.include_router(update_users_router)
app.include_router(delete_users_router)
app.include_router(me_users_router)

app.include_router(auth_router)

app.include_router(admin_router)
app.include_router(orders_router)
app.include_router(tags_router)
app.include_router(reviews_router)
app.include_router(payments_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
