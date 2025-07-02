from fastapi import FastAPI

from src.db.engine import engine
from src.task.api.rest import router as task_router
from src.core.logging_setup import setup_fastapi_logging

app = FastAPI(title="marketplaceai api")
setup_fastapi_logging(app)

app.include_router(task_router, tags=["Task"], prefix="/api/task")

from sqladmin import Admin

from src.core.admin import authentication_backend
from src.task.api.admin import TaskAdmin

admin = Admin(app, engine=engine, authentication_backend=authentication_backend)
admin.add_view(TaskAdmin)
