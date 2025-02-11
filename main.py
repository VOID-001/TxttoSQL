from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from routes.db_connection import db_connection_router
from routes.schema_management import schema_management_router
from routes.sql_execution import sql_execution_router
from routes.api_key import api_key_router
from routes.nlp_context import nlp_context_router
from utils.token_counter import token_router

app = FastAPI()
security = HTTPBasic()

# Dummy credentials (replace with secure storage in production)
USERNAME = "admin"
PASSWORD = "password"

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != USERNAME or credentials.password != PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Include routers with authentication
app.include_router(
    db_connection_router,
    prefix="/api",
    dependencies=[Depends(verify_credentials)]
)
app.include_router(
    schema_management_router,
    prefix="/api",
    dependencies=[Depends(verify_credentials)]
)
app.include_router(
    sql_execution_router,
    prefix="/api",
    dependencies=[Depends(verify_credentials)]
)
app.include_router(
    api_key_router,
    prefix="/api",
    dependencies=[Depends(verify_credentials)]
)
app.include_router(
    nlp_context_router,
    prefix="/api",
    dependencies=[Depends(verify_credentials)]
)
app.include_router(
    token_router,
    prefix="/api",
    tags=["tokens"]
)