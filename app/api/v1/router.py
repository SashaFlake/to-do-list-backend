from fastapi import APIRouter
from app.api.v1.endpoints import users, todos

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(todos.router, prefix="/todos", tags=["todos"])
