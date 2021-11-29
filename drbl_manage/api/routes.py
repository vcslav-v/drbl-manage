from fastapi import APIRouter
from drbl_manage.api.local_routes import api

routes = APIRouter()

routes.include_router(api.router, prefix='/api')
