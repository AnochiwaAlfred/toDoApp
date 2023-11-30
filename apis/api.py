from ninja import NinjaAPI, Router
from apis.auth import router as auth_router
from apis.client import router as client_router
from apis.todo import router as todo_router

api = NinjaAPI(title="TaskMaster")

api.add_router('auth', auth_router)
api.add_router('clients', client_router)
api.add_router('todos', todo_router)
