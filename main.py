from fastapi import FastAPI
from routes.db_connection import db_connection_router
from routes.schema_management import schema_management_router
from routes.sql_execution import sql_execution_router
from routes.api_key import api_key_router

app = FastAPI()

# Include routers
app.include_router(db_connection_router, prefix="/api")
app.include_router(schema_management_router, prefix="/api")
app.include_router(sql_execution_router, prefix="/api")
app.include_router(api_key_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "FastAPI with dynamic DB schema handling is running!"}
