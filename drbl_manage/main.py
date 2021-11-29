from fastapi import FastAPI
from drbl_manage.api.routes import routes

app = FastAPI(debug=True)

app.include_router(routes)
